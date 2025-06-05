// Admin Panel JavaScript Functionality

class QuizBuilder {
    constructor() {
        this.questionCount = 1;
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.updateQuestionCounter();
    }
    
    setupEventListeners() {
        // Add question buttons
        document.getElementById('add-question-btn')?.addEventListener('click', () => this.addQuestion());
        document.getElementById('add-question-bottom')?.addEventListener('click', () => this.addQuestion());
        
        // Remove question buttons (event delegation)
        document.addEventListener('click', (e) => {
            if (e.target.closest('.remove-question-btn')) {
                this.removeQuestion(e.target.closest('.question-card'));
            }
        });
        
        // Question type change (event delegation)
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('question-type-select')) {
                this.handleQuestionTypeChange(e.target);
            }
        });
        
        // Add/remove option buttons (event delegation)
        document.addEventListener('click', (e) => {
            if (e.target.closest('.add-option-btn')) {
                this.addOption(e.target.closest('.answer-options-container'));
            }
            if (e.target.closest('.remove-option-btn')) {
                this.removeOption(e.target.closest('.option-item'));
            }
        });
        
        // Form submission
        document.getElementById('quiz-form')?.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
            }
        });
    }
    
    addQuestion() {
        const container = document.getElementById('questions-container');
        const questionIndex = this.questionCount;
        
        const questionHtml = this.createQuestionHTML(questionIndex);
        
        const questionDiv = document.createElement('div');
        questionDiv.className = 'question-card mb-4';
        questionDiv.dataset.questionIndex = questionIndex;
        questionDiv.innerHTML = questionHtml;
        
        container.appendChild(questionDiv);
        
        this.questionCount++;
        this.updateQuestionCounter();
        this.updateQuestionNumbers();
        this.showRemoveButtons();
        
        // Scroll to new question
        questionDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    removeQuestion(questionCard) {
        if (this.questionCount <= 1) {
            alert('At least one question is required.');
            return;
        }
        
        if (confirm('Are you sure you want to remove this question?')) {
            questionCard.remove();
            this.questionCount--;
            this.updateQuestionCounter();
            this.updateQuestionNumbers();
            this.updateQuestionCount();
            this.hideRemoveButtonsIfNeeded();
        }
    }
    
    createQuestionHTML(index) {
        return `
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-light">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-question-circle text-primary me-2"></i>
                            Question <span class="question-number">${index + 1}</span>
                        </h6>
                        <button type="button" class="btn btn-outline-danger btn-sm remove-question-btn">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <label class="form-label">Question Text *</label>
                        <textarea class="form-control" name="question_${index}_text" rows="3" 
                                  placeholder="Enter your question here..." required></textarea>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Question Type *</label>
                                <select class="form-select question-type-select" name="question_${index}_type" required>
                                    <option value="multiple_choice">Multiple Choice</option>
                                    <option value="true_false">True/False</option>
                                    <option value="short_answer">Short Answer</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Points *</label>
                                <input type="number" class="form-control" name="question_${index}_points" 
                                       value="1" min="1" max="10" required>
                            </div>
                        </div>
                    </div>
                    
                    <div class="answer-options-container">
                        <label class="form-label">Answer Options *</label>
                        <input type="hidden" name="question_${index}_option_count" class="option-count" value="4">
                        
                        <div class="options-list">
                            ${this.createMultipleChoiceOptions(index)}
                        </div>
                        
                        <button type="button" class="btn btn-outline-primary btn-sm add-option-btn">
                            <i class="fas fa-plus me-1"></i>Add Option
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    createMultipleChoiceOptions(questionIndex) {
        return `
            <div class="option-item mb-2">
                <div class="input-group">
                    <div class="input-group-text">
                        <input class="form-check-input" type="radio" 
                               name="question_${questionIndex}_correct" value="0">
                    </div>
                    <input type="text" class="form-control" 
                           name="question_${questionIndex}_option_0_text" 
                           placeholder="Option A" required>
                    <button type="button" class="btn btn-outline-danger remove-option-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            
            <div class="option-item mb-2">
                <div class="input-group">
                    <div class="input-group-text">
                        <input class="form-check-input" type="radio" 
                               name="question_${questionIndex}_correct" value="1">
                    </div>
                    <input type="text" class="form-control" 
                           name="question_${questionIndex}_option_1_text" 
                           placeholder="Option B" required>
                    <button type="button" class="btn btn-outline-danger remove-option-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            
            <div class="option-item mb-2">
                <div class="input-group">
                    <div class="input-group-text">
                        <input class="form-check-input" type="radio" 
                               name="question_${questionIndex}_correct" value="2">
                    </div>
                    <input type="text" class="form-control" 
                           name="question_${questionIndex}_option_2_text" 
                           placeholder="Option C" required>
                    <button type="button" class="btn btn-outline-danger remove-option-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            
            <div class="option-item mb-2">
                <div class="input-group">
                    <div class="input-group-text">
                        <input class="form-check-input" type="radio" 
                               name="question_${questionIndex}_correct" value="3">
                    </div>
                    <input type="text" class="form-control" 
                           name="question_${questionIndex}_option_3_text" 
                           placeholder="Option D" required>
                    <button type="button" class="btn btn-outline-danger remove-option-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    createTrueFalseOptions(questionIndex) {
        return `
            <div class="option-item mb-2">
                <div class="input-group">
                    <div class="input-group-text">
                        <input class="form-check-input" type="radio" 
                               name="question_${questionIndex}_correct" value="0">
                    </div>
                    <input type="text" class="form-control" 
                           name="question_${questionIndex}_option_0_text" 
                           value="True" readonly required>
                    <button type="button" class="btn btn-outline-danger remove-option-btn" disabled>
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            
            <div class="option-item mb-2">
                <div class="input-group">
                    <div class="input-group-text">
                        <input class="form-check-input" type="radio" 
                               name="question_${questionIndex}_correct" value="1">
                    </div>
                    <input type="text" class="form-control" 
                           name="question_${questionIndex}_option_1_text" 
                           value="False" readonly required>
                    <button type="button" class="btn btn-outline-danger remove-option-btn" disabled>
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    handleQuestionTypeChange(selectElement) {
        const questionCard = selectElement.closest('.question-card');
        const questionIndex = questionCard.dataset.questionIndex;
        const questionType = selectElement.value;
        const optionsContainer = questionCard.querySelector('.answer-options-container');
        const optionsList = optionsContainer.querySelector('.options-list');
        const addButton = optionsContainer.querySelector('.add-option-btn');
        const optionCountInput = optionsContainer.querySelector('.option-count');
        
        // Clear existing options
        optionsList.innerHTML = '';
        
        if (questionType === 'multiple_choice') {
            optionsList.innerHTML = this.createMultipleChoiceOptions(questionIndex);
            addButton.style.display = 'block';
            optionCountInput.value = '4';
            optionsContainer.style.display = 'block';
        } else if (questionType === 'true_false') {
            optionsList.innerHTML = this.createTrueFalseOptions(questionIndex);
            addButton.style.display = 'none';
            optionCountInput.value = '2';
            optionsContainer.style.display = 'block';
        } else if (questionType === 'short_answer') {
            optionsContainer.style.display = 'none';
            optionCountInput.value = '0';
        }
    }
    
    addOption(optionsContainer) {
        const optionsList = optionsContainer.querySelector('.options-list');
        const questionCard = optionsContainer.closest('.question-card');
        const questionIndex = questionCard.dataset.questionIndex;
        const currentOptions = optionsList.querySelectorAll('.option-item').length;
        
        if (currentOptions >= 6) {
            alert('Maximum 6 options allowed per question.');
            return;
        }
        
        const optionIndex = currentOptions;
        const optionLetters = ['A', 'B', 'C', 'D', 'E', 'F'];
        
        const optionHtml = `
            <div class="option-item mb-2">
                <div class="input-group">
                    <div class="input-group-text">
                        <input class="form-check-input" type="radio" 
                               name="question_${questionIndex}_correct" value="${optionIndex}">
                    </div>
                    <input type="text" class="form-control" 
                           name="question_${questionIndex}_option_${optionIndex}_text" 
                           placeholder="Option ${optionLetters[optionIndex]}" required>
                    <button type="button" class="btn btn-outline-danger remove-option-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
        
        optionsList.insertAdjacentHTML('beforeend', optionHtml);
        
        // Update option count
        const optionCountInput = optionsContainer.querySelector('.option-count');
        optionCountInput.value = currentOptions + 1;
    }
    
    removeOption(optionItem) {
        const optionsContainer = optionItem.closest('.answer-options-container');
        const optionsList = optionsContainer.querySelector('.options-list');
        const currentOptions = optionsList.querySelectorAll('.option-item').length;
        
        if (currentOptions <= 2) {
            alert('At least 2 options are required.');
            return;
        }
        
        optionItem.remove();
        
        // Update option count
        const optionCountInput = optionsContainer.querySelector('.option-count');
        optionCountInput.value = currentOptions - 1;
        
        // Renumber remaining options
        this.renumberOptions(optionsContainer);
    }
    
    renumberOptions(optionsContainer) {
        const questionCard = optionsContainer.closest('.question-card');
        const questionIndex = questionCard.dataset.questionIndex;
        const optionItems = optionsContainer.querySelectorAll('.option-item');
        const optionLetters = ['A', 'B', 'C', 'D', 'E', 'F'];
        
        optionItems.forEach((item, index) => {
            const radio = item.querySelector('input[type="radio"]');
            const textInput = item.querySelector('input[type="text"]');
            
            if (radio) {
                radio.name = `question_${questionIndex}_correct`;
                radio.value = index;
            }
            
            if (textInput) {
                textInput.name = `question_${questionIndex}_option_${index}_text`;
                if (textInput.placeholder.startsWith('Option')) {
                    textInput.placeholder = `Option ${optionLetters[index]}`;
                }
            }
        });
    }
    
    updateQuestionNumbers() {
        const questionCards = document.querySelectorAll('.question-card');
        questionCards.forEach((card, index) => {
            const questionNumber = card.querySelector('.question-number');
            if (questionNumber) {
                questionNumber.textContent = index + 1;
            }
            
            // Update form field names
            this.updateFieldNames(card, index);
        });
    }
    
    updateFieldNames(questionCard, newIndex) {
        const oldIndex = questionCard.dataset.questionIndex;
        questionCard.dataset.questionIndex = newIndex;
        
        // Update all form field names
        const fields = questionCard.querySelectorAll('[name*="question_"]');
        fields.forEach(field => {
            field.name = field.name.replace(`question_${oldIndex}_`, `question_${newIndex}_`);
        });
        
        // Update radio button names for correct answers
        const radioButtons = questionCard.querySelectorAll('input[type="radio"]');
        radioButtons.forEach(radio => {
            if (radio.name.includes('_correct')) {
                radio.name = `question_${newIndex}_correct`;
            }
        });
    }
    
    updateQuestionCounter() {
        const counter = document.getElementById('question-counter');
        if (counter) {
            counter.textContent = this.questionCount;
        }
        this.updateQuestionCount();
    }
    
    updateQuestionCount() {
        const input = document.getElementById('question_count');
        if (input) {
            input.value = this.questionCount;
        }
    }
    
    showRemoveButtons() {
        if (this.questionCount > 1) {
            document.querySelectorAll('.remove-question-btn').forEach(btn => {
                btn.style.display = 'block';
            });
        }
    }
    
    hideRemoveButtonsIfNeeded() {
        if (this.questionCount === 1) {
            document.querySelectorAll('.remove-question-btn').forEach(btn => {
                btn.style.display = 'none';
            });
        }
    }
    
    validateForm() {
        const title = document.getElementById('title').value.trim();
        if (!title) {
            alert('Quiz title is required.');
            return false;
        }
        
        // Validate each question
        const questionCards = document.querySelectorAll('.question-card');
        for (let i = 0; i < questionCards.length; i++) {
            const card = questionCards[i];
            const questionText = card.querySelector('textarea[name*="_text"]').value.trim();
            
            if (!questionText) {
                alert(`Question ${i + 1} text is required.`);
                return false;
            }
            
            const questionType = card.querySelector('select[name*="_type"]').value;
            
            if (questionType === 'multiple_choice' || questionType === 'true_false') {
                // Check if at least one correct answer is selected
                const correctRadio = card.querySelector('input[name*="_correct"]:checked');
                if (!correctRadio) {
                    alert(`Please select the correct answer for Question ${i + 1}.`);
                    return false;
                }
                
                // Check if all options have text
                const optionInputs = card.querySelectorAll('input[name*="_option_"][name*="_text"]');
                for (let option of optionInputs) {
                    if (!option.value.trim()) {
                        alert(`All options for Question ${i + 1} must have text.`);
                        return false;
                    }
                }
            }
        }
        
        return true;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('quiz-form')) {
        new QuizBuilder();
    }
});

// Utility functions for admin interface
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

function showLoading(element) {
    if (element) {
        element.classList.add('loading');
        element.disabled = true;
    }
}

function hideLoading(element) {
    if (element) {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

// Auto-save functionality for forms
function setupAutoSave(formSelector, saveUrl) {
    const form = document.querySelector(formSelector);
    if (!form) return;
    
    let saveTimeout;
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                saveFormData(form, saveUrl);
            }, 2000);
        });
    });
}

function saveFormData(form, url) {
    const formData = new FormData(form);
    
    fetch(url, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Changes saved automatically', 'success');
        }
    })
    .catch(error => {
        console.error('Auto-save failed:', error);
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}
