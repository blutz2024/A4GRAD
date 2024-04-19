import logging
from flask import Flask, render_template, request, redirect, url_for
import datetime
import random

# Configure logging to print to console and write to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("quiz.log"),
        logging.StreamHandler()
    ])

app = Flask(__name__, template_folder='templates')

def read_questions_from_file(quiz_name):
    questions = []
    with open(f'{quiz_name}.txt', 'r') as file:
        question_text = ''
        options = []
        correct_answer = ''
        for line in file:
            line = line.strip()
            if line.startswith('Question:'):
                if question_text:  # If previous question exists, add it to questions list
                    questions.append({'question': question_text, 'options': options, 'correct_answer': correct_answer})
                question_text = line[9:].strip()  # Extract question text after 'Question:'
                options = []  # Reset options list for new question
            elif line.startswith('Option:'):
                options.append(line[7:].strip())  # Extract option text after 'Option:'
            elif line.startswith('Answer:'):
                correct_answer = line[7:].strip()  # Extract correct answer text after 'Answer:'
        # Add last question to questions list
        if question_text:
            questions.append({'question': question_text, 'options': options, 'correct_answer': correct_answer})
    return questions

def log_attempt(user_name, quiz_name, total_score):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        logging.info(f"{timestamp} - User: {user_name}, Quiz: {quiz_name}, Score: {total_score}")
    except Exception as e:
        logging.error(f"Error occurred while logging attempt: {e}")

# Route for the index page
@app.route('/', methods=['GET', 'POST'])
def index():
    total_score = None
    timer_value = None  # Initialize timer_value variable
    if request.method == 'POST':
        user_name = request.form.get('name')
        timer_value_str = request.form.get('timer')
        timer_value = int(
            timer_value_str) if timer_value_str is not None else None  # Get timer value from form and convert to int if not None
        selected_quiz = request.form.get('quiz')
        quiz_data = {}
        questions = read_questions_from_file(selected_quiz)
        total_questions = len(questions)
        correct_answers = 0
        for question in questions:
            selected_answer = request.form.get(question['question'])
            quiz_data[question['question']] = selected_answer
            if selected_answer == question['correct_answer']:
                correct_answers += 1
        total_score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0

        # Log the attempt
        log_attempt(user_name, selected_quiz, total_score)

        # Redirect to the quiz page after logging
        return redirect(url_for('quiz', quiz_name=selected_quiz, timer_value=timer_value))

    quizzes = ['quiz1', 'quiz2']
    return render_template('index.html', quizzes=quizzes, total_score=total_score, timer_value=timer_value)  # Pass timer_value to the template

# Function to shuffle questions and options
def shuffle_questions_and_options(questions):
    random.shuffle(questions)  # Shuffle the list of questions
    for question in questions:
        random.shuffle(question['options'])  # Shuffle the options for each question

# Route for showing the quiz
@app.route('/quiz/<quiz_name>')
def quiz(quiz_name):
    questions = read_questions_from_file(quiz_name)
    shuffle_questions_and_options(questions)  # Shuffle questions and options
    timer_value = request.args.get('timer_value')  # Get timer value from query parameter
    return render_template('show.html', questions=questions, selected_quiz=quiz_name, timer_value=timer_value)  # Pass timer_value to the template

if __name__ == '__main__':
    app.run(debug=True)
