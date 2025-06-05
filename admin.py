from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, BooleanField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange
from models import User, Quiz, Question, AnswerOption, QuizAttempt, UserAnswer
from app import db
from utils import admin_required
import csv
from io import StringIO
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

class AnswerOptionForm(FlaskForm):
    option_text = StringField('Option Text', validators=[DataRequired()])
    is_correct = BooleanField('Correct Answer')

class QuestionForm(FlaskForm):
    question_text = TextAreaField('Question Text', validators=[DataRequired()])
    question_type = SelectField('Question Type', choices=[
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer')
    ], validators=[DataRequired()])
    points = IntegerField('Points', validators=[DataRequired(), NumberRange(min=1)], default=1)
    options = FieldList(FormField(AnswerOptionForm), min_entries=2, max_entries=6)

class QuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    time_limit = IntegerField('Time Limit (minutes)', validators=[DataRequired(), NumberRange(min=1)], default=30)
    max_attempts = IntegerField('Maximum Attempts', validators=[DataRequired(), NumberRange(min=1)], default=1)
    is_active = BooleanField('Active', default=True)
    questions = FieldList(FormField(QuestionForm), min_entries=1)
    submit = SubmitField('Save Quiz')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get statistics
    total_users = User.query.filter_by(is_admin=False).count()
    total_quizzes = Quiz.query.count()
    total_attempts = QuizAttempt.query.count()
    completed_attempts = QuizAttempt.query.filter_by(is_completed=True).count()
    
    # Recent activity
    recent_attempts = QuizAttempt.query.order_by(QuizAttempt.start_time.desc()).limit(5).all()
    active_quizzes = Quiz.query.filter_by(is_active=True).all()
    
    # Quiz statistics
    quiz_stats = []
    for quiz in active_quizzes:
        attempts = QuizAttempt.query.filter_by(quiz_id=quiz.id, is_completed=True).all()
        avg_score = sum(a.score for a in attempts) / len(attempts) if attempts else 0
        quiz_stats.append({
            'quiz': quiz,
            'attempts': len(attempts),
            'avg_score': round(avg_score, 1)
        })
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_quizzes=total_quizzes,
                         total_attempts=total_attempts,
                         completed_attempts=completed_attempts,
                         recent_attempts=recent_attempts,
                         quiz_stats=quiz_stats)

@admin_bp.route('/create_quiz', methods=['GET', 'POST'])
@login_required
@admin_required
def create_quiz():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        time_limit = int(request.form.get('time_limit', 30))
        max_attempts = int(request.form.get('max_attempts', 1))
        is_active = bool(request.form.get('is_active'))
        
        quiz = Quiz(
            title=title,
            description=description,
            created_by=current_user.id,
            time_limit=time_limit,
            max_attempts=max_attempts,
            is_active=is_active
        )
        db.session.add(quiz)
        db.session.flush()  # To get the quiz ID
        
        # Process questions
        question_count = int(request.form.get('question_count', 0))
        for i in range(question_count):
            question_text = request.form.get(f'question_{i}_text')
            question_type = request.form.get(f'question_{i}_type')
            points = int(request.form.get(f'question_{i}_points', 1))
            
            if question_text:
                question = Question(
                    quiz_id=quiz.id,
                    question_text=question_text,
                    question_type=question_type,
                    points=points,
                    order_index=i
                )
                db.session.add(question)
                db.session.flush()
                
                # Process answer options
                if question_type in ['multiple_choice', 'true_false']:
                    option_count = int(request.form.get(f'question_{i}_option_count', 0))
                    correct_option_index = request.form.get(f'question_{i}_correct')
                    
                    for j in range(option_count):
                        option_text = request.form.get(f'question_{i}_option_{j}_text')
                        # Check if this option is the correct one
                        is_correct = (correct_option_index is not None and int(correct_option_index) == j)
                        
                        if option_text:
                            option = AnswerOption(
                                question_id=question.id,
                                option_text=option_text,
                                is_correct=is_correct
                            )
                            db.session.add(option)
        
        try:
            db.session.commit()
            flash('Quiz created successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating quiz. Please try again.', 'error')
    
    return render_template('admin/create_quiz.html')

@admin_bp.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        quiz.title = request.form.get('title')
        quiz.description = request.form.get('description')
        quiz.time_limit = int(request.form.get('time_limit', 30))
        quiz.max_attempts = int(request.form.get('max_attempts', 1))
        quiz.is_active = bool(request.form.get('is_active'))
        
        try:
            db.session.commit()
            flash('Quiz updated successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating quiz. Please try again.', 'error')
    
    return render_template('admin/edit_quiz.html', quiz=quiz)

@admin_bp.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
@login_required
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    try:
        db.session.delete(quiz)
        db.session.commit()
        flash('Quiz deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting quiz. Please try again.', 'error')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/manage_users')
@login_required
@admin_required
def manage_users():
    users = User.query.filter_by(is_admin=False).all()
    user_stats = []
    
    for user in users:
        attempts = QuizAttempt.query.filter_by(user_id=user.id).count()
        completed = QuizAttempt.query.filter_by(user_id=user.id, is_completed=True).count()
        avg_score = db.session.query(db.func.avg(QuizAttempt.score)).filter_by(
            user_id=user.id, is_completed=True
        ).scalar() or 0
        
        user_stats.append({
            'user': user,
            'attempts': attempts,
            'completed': completed,
            'avg_score': round(avg_score, 1)
        })
    
    return render_template('admin/manage_users.html', user_stats=user_stats)

@admin_bp.route('/results')
@login_required
@admin_required
def results():
    quiz_id = request.args.get('quiz_id')
    user_id = request.args.get('user_id')
    
    query = QuizAttempt.query.filter_by(is_completed=True)
    
    if quiz_id:
        query = query.filter_by(quiz_id=quiz_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    attempts = query.order_by(QuizAttempt.end_time.desc()).all()
    quizzes = Quiz.query.all()
    users = User.query.filter_by(is_admin=False).all()
    
    return render_template('admin/results.html', 
                         attempts=attempts, 
                         quizzes=quizzes, 
                         users=users,
                         selected_quiz=quiz_id,
                         selected_user=user_id)

@admin_bp.route('/export_results')
@login_required
@admin_required
def export_results():
    quiz_id = request.args.get('quiz_id')
    
    query = QuizAttempt.query.filter_by(is_completed=True)
    if quiz_id:
        query = query.filter_by(quiz_id=quiz_id)
    
    attempts = query.order_by(QuizAttempt.end_time.desc()).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['User', 'Quiz', 'Score', 'Total Points', 'Percentage', 'Duration (minutes)', 'Completed At'])
    
    # Write data
    for attempt in attempts:
        total_points = attempt.quiz.get_total_points()
        percentage = (attempt.score / total_points * 100) if total_points > 0 else 0
        duration = attempt.get_duration()
        
        writer.writerow([
            attempt.user.username,
            attempt.quiz.title,
            attempt.score,
            total_points,
            round(percentage, 1),
            round(duration, 1),
            attempt.end_time.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=quiz_results.csv'
    
    return response

@admin_bp.route('/toggle_user_status/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    # For now, we don't have an active/inactive status, but we could add it
    flash(f'User {user.username} status updated.', 'success')
    return redirect(url_for('admin.manage_users'))
