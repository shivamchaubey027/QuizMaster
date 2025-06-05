// Quiz Taking JavaScript Functionality

class QuizApp {
    constructor() {
        this.currentQuestion = 1;
        this.totalQuestions = 0;
        this.timeRemaining = 0;
        this.timerInterval = null;
        this.attemptId = null;
        this.csrfToken = null;
        this.autoSaveTimeout = null;
        this.answers = {};
        
        this.init();
    }
    
    init() {
        // Get quiz data from meta tag
        const metaTag = document.querySelector('meta[name="quiz-data"]');
        if (metaTag) {
            this.attemptId = metaTag.dataset.attemptId;
            this.timeRemaining = parseInt(metaTag.dataset.timeRemaining);
            this.csrfToken = metaTag.dataset.csrfToken;
        }
        
        // Initialize quiz state
        this.totalQuestions = document.querySelectorAll('.question-card').length;
        this.setupEventListeners();
        this.updateProgress();
        this.startTimer();
        this.loadExistingAnswers();
    }
    
    setupEventListeners() {
        // Navigation buttons
        document.getElementById('prev-btn')?.addEventListener('click', () => this.previousQuestion());
        document.getElementById('next-btn')?.addEventListener('click', () => this.nextQuestion());
        
        // Question navigator buttons
        document.querySelectorAll('.question-nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const questionNum = parseInt(e.target.dataset.question);
                this.goToQuestion(questionNum);
            });
        });
        
        // Submit quiz button
        document.getElementById('submit-quiz-btn')?.addEventListener('click', () => this.showSubmitModal());
        
        // Answer inputs
        this.setupAnswerListeners();
        
        // Auto-save on visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.saveCurrentAnswer();
            }
        });
        
        // Save on page unload
        window.addEventListener('beforeunload', () => {
            this.saveCurrentAnswer();
        });
    }
    
    setupAnswerListeners() {
        // Radio buttons and checkboxes
        document.querySelectorAll('input[type="radio"]').forEach(input => {
            input.addEventListener('change', (e) => {
                const questionId = e.target.dataset.questionId;
                if (questionId) {
                    this.handleAnswerChange(questionId, e.target.value);
                }
            });
        });
        
        // Text areas
        document.querySelectorAll('textarea[data-question-id]').forEach(textarea => {
            textarea.addEventListener('input', (e) => {
                const questionId = e.target.dataset.questionId;
                if (questionId) {
                    // Debounce auto-save for text inputs
                    clearTimeout(this.autoSaveTimeout);
                    this.autoSaveTimeout = setTimeout(() => {
                        this.handleAnswerChange(questionId, e.target.value);
                    }, 1000);
                }
            });
            
            // Save immediately on blur
            textarea.addEventListener('blur', (e) => {
                const questionId = e.target.dataset.questionId;
                if (questionId) {
                    clearTimeout(this.autoSaveTimeout);
                    this.handleAnswerChange(questionId, e.target.value);
                }
            });
        });
    }
    
    handleAnswerChange(questionId, value) {
        this.answers[questionId] = value;
        this.saveAnswer(questionId, value);
        this.updateNavigatorButton(this.currentQuestion);
        this.updateAnsweredCount();
    }
    
    saveAnswer(questionId, value) {
        if (!this.attemptId || !this.csrfToken) return;
        
        fetch('/quiz/save_answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            },
            body: JSON.stringify({
                attempt_id: this.attemptId,
                question_id: questionId,
                answer_value: value
            })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                console.error('Failed to save answer:', data.message);
                this.showNotification('Failed to save answer', 'error');
            }
        })
        .catch(error => {
            console.error('Error saving answer:', error);
        });
    }
    
    saveCurrentAnswer() {
        const currentCard = document.querySelector(`#question-${this.currentQuestion}`);
        if (!currentCard) return;
        
        // Save radio button answers
        const radioInput = currentCard.querySelector('input[type="radio"]:checked');
        if (radioInput) {
            const questionId = radioInput.dataset.questionId;
            this.handleAnswerChange(questionId, radioInput.value);
        }
        
        // Save text answers
        const textArea = currentCard.querySelector('textarea[data-question-id]');
        if (textArea) {
            const questionId = textArea.dataset.questionId;
            this.handleAnswerChange(questionId, textArea.value);
        }
    }
    
    loadExistingAnswers() {
        // Radio buttons
        document.querySelectorAll('input[type="radio"]:checked').forEach(input => {
            const questionId = input.dataset.questionId;
            if (questionId) {
                this.answers[questionId] = input.value;
            }
        });
        
        // Text areas
        document.querySelectorAll('textarea[data-question-id]').forEach(textarea => {
            const questionId = textarea.dataset.questionId;
            if (questionId && textarea.value.trim()) {
                this.answers[questionId] = textarea.value;
            }
        });
        
        this.updateAllNavigatorButtons();
        this.updateAnsweredCount();
    }
    
    nextQuestion() {
        if (this.currentQuestion < this.totalQuestions) {
            this.saveCurrentAnswer();
            this.goToQuestion(this.currentQuestion + 1);
        }
    }
    
    previousQuestion() {
        if (this.currentQuestion > 1) {
            this.saveCurrentAnswer();
            this.goToQuestion(this.currentQuestion - 1);
        }
    }
    
    goToQuestion(questionNum) {
        if (questionNum < 1 || questionNum > this.totalQuestions) return;
        
        // Hide current question
        document.querySelector(`#question-${this.currentQuestion}`)?.style.setProperty('display', 'none');
        
        // Show target question
        const targetQuestion = document.querySelector(`#question-${questionNum}`);
        if (targetQuestion) {
            targetQuestion.style.setProperty('display', 'block');
        }
        
        this.currentQuestion = questionNum;
        this.updateProgress();
        this.updateNavigationButtons();
        this.updateNavigatorButtons();
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    updateProgress() {
        const progressBar = document.getElementById('quiz-progress-bar');
        const currentQuestionSpan = document.getElementById('current-question');
        
        if (progressBar) {
            const progress = (this.currentQuestion / this.totalQuestions) * 100;
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }
        
        if (currentQuestionSpan) {
            currentQuestionSpan.textContent = this.currentQuestion;
        }
    }
    
    updateNavigationButtons() {
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        
        if (prevBtn) {
            prevBtn.disabled = this.currentQuestion === 1;
        }
        
        if (nextBtn) {
            if (this.currentQuestion === this.totalQuestions) {
                nextBtn.style.display = 'none';
            } else {
                nextBtn.style.display = 'block';
                nextBtn.disabled = false;
            }
        }
    }
    
    updateNavigatorButtons() {
        document.querySelectorAll('.question-nav-btn').forEach(btn => {
            const questionNum = parseInt(btn.dataset.question);
            btn.classList.remove('current');
            
            if (questionNum === this.currentQuestion) {
                btn.classList.add('current');
            }
        });
    }
    
    updateNavigatorButton(questionNum) {
        const btn = document.getElementById(`nav-btn-${questionNum}`);
        if (!btn) return;
        
        // Check if question is answered
        const questionCard = document.querySelector(`#question-${questionNum}`);
        if (!questionCard) return;
        
        const isAnswered = this.isQuestionAnswered(questionCard);
        
        btn.classList.remove('answered');
        if (isAnswered) {
            btn.classList.add('answered');
        }
    }
    
    updateAllNavigatorButtons() {
        for (let i = 1; i <= this.totalQuestions; i++) {
            this.updateNavigatorButton(i);
        }
    }
    
    isQuestionAnswered(questionCard) {
        // Check radio buttons
        const radioChecked = questionCard.querySelector('input[type="radio"]:checked');
        if (radioChecked) return true;
        
        // Check text areas
        const textArea = questionCard.querySelector('textarea[data-question-id]');
        if (textArea && textArea.value.trim()) return true;
        
        return false;
    }
    
    updateAnsweredCount() {
        const answeredCountSpan = document.getElementById('answered-count');
        if (!answeredCountSpan) return;
        
        let answeredCount = 0;
        for (let i = 1; i <= this.totalQuestions; i++) {
            const questionCard = document.querySelector(`#question-${i}`);
            if (questionCard && this.isQuestionAnswered(questionCard)) {
                answeredCount++;
            }
        }
        
        answeredCountSpan.textContent = answeredCount;
    }
    
    startTimer() {
        if (this.timeRemaining <= 0) return;
        
        this.updateTimerDisplay();
        
        this.timerInterval = setInterval(() => {
            this.timeRemaining--;
            this.updateTimerDisplay();
            
            // Warning when 5 minutes remaining
            if (this.timeRemaining === 300) {
                this.showNotification('5 minutes remaining!', 'warning');
                document.getElementById('timer-display')?.classList.add('timer-warning');
            }
            
            // Warning when 1 minute remaining
            if (this.timeRemaining === 60) {
                this.showNotification('1 minute remaining!', 'danger');
            }
            
            // Auto-submit when time is up
            if (this.timeRemaining <= 0) {
                clearInterval(this.timerInterval);
                this.autoSubmitQuiz();
            }
        }, 1000);
    }
    
    updateTimerDisplay() {
        const timerText = document.getElementById('timer-text');
        if (!timerText) return;
        
        const minutes = Math.floor(this.timeRemaining / 60);
        const seconds = this.timeRemaining % 60;
        
        timerText.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // Add warning class when less than 5 minutes
        const timerDisplay = document.getElementById('timer-display');
        if (this.timeRemaining <= 300 && timerDisplay) {
            timerDisplay.classList.add('timer-warning');
        }
    }
    
    showSubmitModal() {
        this.saveCurrentAnswer();
        this.updateAnsweredCount();
        
        const modal = new bootstrap.Modal(document.getElementById('submitModal'));
        modal.show();
    }
    
    autoSubmitQuiz() {
        this.saveCurrentAnswer();
        this.showNotification('Time is up! Submitting quiz automatically...', 'warning');
        
        // Submit the form
        const form = document.querySelector('form[action*="submit"]');
        if (form) {
            form.submit();
        } else {
            // Fallback: redirect to submit URL
            window.location.href = `/quiz/submit/${this.attemptId}`;
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Initialize quiz app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.quiz-container')) {
        new QuizApp();
    }
});

// Prevent accidental page refresh
window.addEventListener('beforeunload', (e) => {
    if (document.querySelector('.quiz-container')) {
        e.preventDefault();
        e.returnValue = 'Are you sure you want to leave? Your progress will be saved, but the timer will continue.';
    }
});
