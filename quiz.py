from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Quiz, Question, AnswerOption, QuizAttempt, UserAnswer
from app import db
from datetime import datetime, timedelta
import json

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's quiz statistics
    total_attempts = QuizAttempt.query.filter_by(user_id=current_user.id).count()
    completed_attempts = QuizAttempt.query.filter_by(user_id=current_user.id, is_completed=True).count()
    
    avg_score = db.session.query(db.func.avg(QuizAttempt.score)).filter_by(
        user_id=current_user.id, is_completed=True
    ).scalar() or 0
    
    # Recent attempts
    recent_attempts = QuizAttempt.query.filter_by(
        user_id=current_user.id, is_completed=True
    ).order_by(QuizAttempt.end_time.desc()).limit(5).all()
    
    # Available quizzes
    available_quizzes = Quiz.query.filter_by(is_active=True).all()
    
    # Filter quizzes based on max attempts
    quiz_data = []
    for quiz in available_quizzes:
        user_attempts = QuizAttempt.query.filter_by(
            user_id=current_user.id, quiz_id=quiz.id
        ).count()
        can_attempt = user_attempts < quiz.max_attempts
        
        quiz_data.append({
            'quiz': quiz,
            'attempts_taken': user_attempts,
            'can_attempt': can_attempt
        })
    
    return render_template('user/dashboard.html',
                         total_attempts=total_attempts,
                         completed_attempts=completed_attempts,
                         avg_score=round(avg_score, 1),
                         recent_attempts=recent_attempts,
                         quiz_data=quiz_data)

@quiz_bp.route('/list')
@login_required
def quiz_list():
    quizzes = Quiz.query.filter_by(is_active=True).all()
    quiz_data = []
    
    for quiz in quizzes:
        user_attempts = QuizAttempt.query.filter_by(
            user_id=current_user.id, quiz_id=quiz.id
        ).count()
        
        best_score = db.session.query(db.func.max(QuizAttempt.score)).filter_by(
            user_id=current_user.id, quiz_id=quiz.id, is_completed=True
        ).scalar() or 0
        
        quiz_data.append({
            'quiz': quiz,
            'attempts_taken': user_attempts,
            'can_attempt': user_attempts < quiz.max_attempts,
            'best_score': best_score,
            'total_points': quiz.get_total_points()
        })
    
    return render_template('user/quiz_list.html', quiz_data=quiz_data)

@quiz_bp.route('/start/<int:quiz_id>')
@login_required
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user can take this quiz
    user_attempts = QuizAttempt.query.filter_by(
        user_id=current_user.id, quiz_id=quiz_id
    ).count()
    
    if user_attempts >= quiz.max_attempts:
        flash('You have reached the maximum number of attempts for this quiz.', 'error')
        return redirect(url_for('quiz.quiz_list'))
    
    # Check for incomplete attempt
    incomplete_attempt = QuizAttempt.query.filter_by(
        user_id=current_user.id, quiz_id=quiz_id, is_completed=False
    ).first()
    
    if incomplete_attempt:
        # Check if time limit exceeded
        time_elapsed = (datetime.utcnow() - incomplete_attempt.start_time).total_seconds() / 60
        if time_elapsed > quiz.time_limit:
            # Auto-submit the quiz
            incomplete_attempt.end_time = datetime.utcnow()
            incomplete_attempt.is_completed = True
            incomplete_attempt.score = calculate_score(incomplete_attempt)
            db.session.commit()
            flash('Your previous attempt has been auto-submitted due to time limit.', 'warning')
            return redirect(url_for('quiz.quiz_result', attempt_id=incomplete_attempt.id))
        else:
            return redirect(url_for('quiz.take_quiz', attempt_id=incomplete_attempt.id))
    
    # Create new attempt
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        start_time=datetime.utcnow()
    )
    db.session.add(attempt)
    db.session.commit()
    
    return redirect(url_for('quiz.take_quiz', attempt_id=attempt.id))

@quiz_bp.route('/take/<int:attempt_id>')
@login_required
def take_quiz(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Verify ownership
    if attempt.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('quiz.dashboard'))
    
    if attempt.is_completed:
        return redirect(url_for('quiz.quiz_result', attempt_id=attempt_id))
    
    quiz = attempt.quiz
    questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.order_index).all()
    
    # Calculate time remaining
    time_elapsed = (datetime.utcnow() - attempt.start_time).total_seconds() / 60
    time_remaining = max(0, quiz.time_limit - time_elapsed)
    
    if time_remaining <= 0:
        # Auto-submit
        attempt.end_time = datetime.utcnow()
        attempt.is_completed = True
        attempt.score = calculate_score(attempt)
        db.session.commit()
        return redirect(url_for('quiz.quiz_result', attempt_id=attempt_id))
    
    # Get existing answers
    existing_answers = {}
    for answer in attempt.user_answers:
        if answer.selected_option_id:
            existing_answers[answer.question_id] = answer.selected_option_id
        elif answer.text_answer:
            existing_answers[answer.question_id] = answer.text_answer
    
    return render_template('user/take_quiz.html',
                         attempt=attempt,
                         quiz=quiz,
                         questions=questions,
                         time_remaining=int(time_remaining * 60),  # in seconds
                         existing_answers=existing_answers)

@quiz_bp.route('/save_answer', methods=['POST'])
@login_required
def save_answer():
    data = request.get_json()
    attempt_id = data.get('attempt_id')
    question_id = data.get('question_id')
    answer_value = data.get('answer_value')
    
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Verify ownership
    if attempt.user_id != current_user.id or attempt.is_completed:
        return jsonify({'success': False, 'message': 'Access denied'})
    
    # Find or create user answer
    user_answer = UserAnswer.query.filter_by(
        attempt_id=attempt_id, question_id=question_id
    ).first()
    
    if not user_answer:
        user_answer = UserAnswer(
            attempt_id=attempt_id,
            question_id=question_id
        )
        db.session.add(user_answer)
    
    # Update answer based on question type
    question = Question.query.get(question_id)
    if question.question_type in ['multiple_choice', 'true_false']:
        user_answer.selected_option_id = int(answer_value) if answer_value else None
        user_answer.text_answer = None
    else:  # short_answer
        user_answer.text_answer = answer_value
        user_answer.selected_option_id = None
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error saving answer'})

@quiz_bp.route('/submit/<int:attempt_id>', methods=['POST'])
@login_required
def submit_quiz(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Verify ownership
    if attempt.user_id != current_user.id or attempt.is_completed:
        flash('Access denied.', 'error')
        return redirect(url_for('quiz.dashboard'))
    
    # Complete the attempt
    attempt.end_time = datetime.utcnow()
    attempt.is_completed = True
    attempt.score = calculate_score(attempt)
    
    db.session.commit()
    
    flash('Quiz submitted successfully!', 'success')
    return redirect(url_for('quiz.quiz_result', attempt_id=attempt_id))

@quiz_bp.route('/result/<int:attempt_id>')
@login_required
def quiz_result(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Verify ownership
    if attempt.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('quiz.dashboard'))
    
    if not attempt.is_completed:
        return redirect(url_for('quiz.take_quiz', attempt_id=attempt_id))
    
    quiz = attempt.quiz
    questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.order_index).all()
    
    # Get detailed results
    question_results = []
    for question in questions:
        user_answer = UserAnswer.query.filter_by(
            attempt_id=attempt_id, question_id=question.id
        ).first()
        
        result = {
            'question': question,
            'user_answer': user_answer,
            'is_correct': user_answer.is_correct if user_answer else False
        }
        
        if question.question_type in ['multiple_choice', 'true_false']:
            correct_option = AnswerOption.query.filter_by(
                question_id=question.id, is_correct=True
            ).first()
            result['correct_option'] = correct_option
        
        question_results.append(result)
    
    total_points = quiz.get_total_points()
    percentage = (attempt.score / total_points * 100) if total_points > 0 else 0
    
    return render_template('user/quiz_result.html',
                         attempt=attempt,
                         quiz=quiz,
                         question_results=question_results,
                         total_points=total_points,
                         percentage=round(percentage, 1))

@quiz_bp.route('/history')
@login_required
def history():
    attempts = QuizAttempt.query.filter_by(
        user_id=current_user.id, is_completed=True
    ).order_by(QuizAttempt.end_time.desc()).all()
    
    return render_template('user/history.html', attempts=attempts)

def calculate_score(attempt):
    """Calculate the total score for a quiz attempt"""
    total_score = 0
    
    for user_answer in attempt.user_answers:
        question = user_answer.question
        is_correct = False
        
        if question.question_type in ['multiple_choice', 'true_false']:
            if user_answer.selected_option_id:
                selected_option = AnswerOption.query.get(user_answer.selected_option_id)
                is_correct = selected_option and selected_option.is_correct
        else:  # short_answer - for now, we'll mark as correct if there's an answer
            # In a real system, you'd want manual grading or keyword matching
            is_correct = bool(user_answer.text_answer and user_answer.text_answer.strip())
        
        user_answer.is_correct = is_correct
        if is_correct:
            total_score += question.points
    
    return total_score
