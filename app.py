import os
import random
import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from models import Question, Answer, Topic, Subtopic


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}

    if request.method == "POST":
        # get input
        try:
            url = request.form['url']
            r = requests.get(url)
            print(r.text)

        except requests.ConnectionError:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )

    return render_template('index.html', errors=errors, results=results)


@app.route('/<q_id>')
def display_question(q_id):
    return "The question is {}.".format(q_id)


@app.route('/questions/new', methods=['GET', 'POST'])
def new_question():
    results = {}
    errors = []
    if request.method == 'POST':
        try:
            # Save answer before to get its id
            answer = Answer(request.form['answer'])
            db.session.add(answer)
            db.session.commit()

            desc = request.form['description']
            image = request.form['image']
            subtopic = request.form['subtopic']

            q = Question(desc, image, answer.id, subtopic)

            db.session.add(q)
            db.session.commit()

        except requests.ConnectionError:
            errors.append(
                "Unable to process your input"
            )

    return render_template(
        'add_question.html', errors=errors, results=results
    )


@app.route('/topics/new', methods=['GET', 'POST'])
def new_topic():
    errors = []
    results = {}
    if request.method == 'POST':

        try:
            name = request.form['name']
            description = request.form['description']

            t = Topic(name, description)

            db.session.add(t)
            db.session.commit()

        except requests.ConnectionError:
            errors.append("Unable to process your input")

    return render_template('add_topic.html', errors=errors, results=results)


@app.route('/subtopics/new', methods=['GET', 'POST'])
def new_subtopic():
    errors = []
    results = {}
    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']
            topic = request.form['topic']

            st = Subtopic(name, description, topic)

            db.session.add(st)
            db.session.commit()

        except requests.ConnectionError:
            errors.append("Unable to process your input")

    return render_template('add_subtopic.html', errors=errors, results=results)


# displaying questions
@app.route('/questions/all', methods=['GET', 'POST'])
def display_questions():
    errors = []
    results = {}

    try:
        questions = Question.query.all()

        for q in questions:
            answer = Answer.query.filter_by(id=q.id).first()
            results[q.description] = answer.answer

    except ConnectionError:
        errors.append("Unable to fetch from database")

    return render_template('display_questions.html', errors=errors, results=results)

# random questions
@app.route('/questions/random/<subtopic_id>', methods=['GET', 'POST'])
def random_questions(subtopic_id):
    errors = []
    results = {}
    try:
        questions = Question.query.filter_by(subtopic=subtopic_id).all()

        q = random.randint(0, len(questions)-1)

        results['topic'] = questions[q].subtopic
        results['question'] = questions[q].description
        results['answer'] = Answer.query.filter_by(id=questions[q].answer).first()

    except ConnectionError:
        errors.append("Unable to fetch from database")

    return render_template('topic_question.html', errors=errors, results=results)


if __name__ == '__main__':

    app.run()

