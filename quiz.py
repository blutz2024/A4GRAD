from flask import Flask, render_template, request, redirect, url_for
import random

#http://127.0.0.1:5000/
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
                if question_text:
                    questions.append({'question': question_text, 'options': options, 'correct_answer': correct_answer})
                question_text = line[9:].strip()
                options = []
            elif line.startswith('Option:'):
                options.append(line[7:].strip())
            elif line.startswith('Answer:'):
                correct_answer = line[7:].strip()
        if question_text:
            questions.append({'question': question_text, 'options': options, 'correct_answer': correct_answer})
    return questions

def save_username(username):
    # Specify the path to the text file
    file_path = 'usernames.txt'

    # Append the username to the text file
    with open(file_path, 'a') as file:
        file.write(username + '\n')

# Route for the index page
@app.route('/', methods=['GET', 'POST'])
def index():
    total_score = None
    timer_value = None
    if request.method == 'POST':
        username = request.form['name']

        # Print the username to the host screen
        print("Username:", username)

        timer_value_str = request.form.get('timer')
        timer_value = int(timer_value_str) if timer_value_str is not None else None
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
        # Redirect to the quiz page
        return redirect(url_for('quiz', quiz_name=selected_quiz, timer_value=timer_value))

    quizzes = ['quiz1', 'quiz2']
    return render_template('index.html', quizzes=quizzes, total_score=total_score, timer_value=timer_value)

# Function to shuffle questions and options
def shuffle_questions_and_options(questions):
    random.shuffle(questions)
    for question in questions:
        random.shuffle(question['options'])

# Route for showing the quiz
@app.route('/quiz/<quiz_name>')
def quiz(quiz_name):
    questions = read_questions_from_file(quiz_name)
    shuffle_questions_and_options(questions)
    timer_value = request.args.get('timer_value')
    return render_template('show.html', questions=questions, selected_quiz=quiz_name, timer_value=timer_value)

if __name__ == '__main__':
    app.run(debug=True)
