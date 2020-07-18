import os
import json
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # set up CORS, allowing all origins
    cors = CORS(app, resources={"/": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        '''
        Sets access control.
        '''
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/hello')
    def hello():
        '''
        Test Api.
        '''
        return jsonify({
            'message': "Hello, welcome to trivia API"
            })

    @app.route('/categories')
    def get_categories():
        '''
        Handles GET requests for getting all categories.
        '''
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        # format it as required by ui
        return_json = {category['id']: category['type'] for category
                       in formatted_categories}
        return jsonify({
            'success': True,
            'categories': return_json
            })

    # utility for paginating questions
    def pagination(request, data):
        page = request.args.get('page', 1, int)
        start = (page-1)*10
        end = start+10
        formatted_data = [p.format() for p in data]
        current_data = formatted_data[start:end]
        # abort 404 if no data found
        if len(current_data) == 0:
            abort(404)
        return current_data

    @app.route('/questions')
    def get_questions():
        '''
        Handles GET requests for getting all questions.
        '''
        # get all questions and paginate
        questions = Question.query.all()
        output_data = pagination(request, questions)

        # get all categories
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        # format it as required by ui
        return_json = {category['id']: category['type'] for category
                       in formatted_categories}
        return jsonify({
            'success': True,
            'questions': output_data,
            'total_questions': len(questions),
            'categories': return_json,
            'current_category': output_data[0]['category']
            })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        '''
        Handles DELETE requests for deleting a question by id.
        '''
        # get the question by id
        question = Question.query.get(question_id)
        # abort 404 if no question found
        if question is None:
            abort(422)

        question.delete()

        return jsonify({
            'success': True,
            'deleted_question': question_id
            })

    @app.route('/questions', methods=['POST'])
    def create_question():
        '''
        Handles POST requests for creating new questions and
        searching questions.
        '''
        indata = json.loads(request.data)
        question = indata.get('question', '')
        answer = indata.get('answer', '')
        category = indata.get('category', '')
        difficulty = indata.get('difficulty', '')
        search = indata.get('searchTerm', None)
        # if search term exist in request body
        if search:
            # filter question titles based on search term
            questions = Question.query.filter(
                Question.question.ilike("%"+search+"%")).all()
            # paginate
            output_data = pagination(request, questions)
            return jsonify({
                'success': True,
                'questions': output_data,
                'total_questions': len(questions),
                'current_category': questions[0].category
                })
        else:
            # else create new question
            try:
                # check if either is not present in request body
                if ((question == '') or (answer == '') or (difficulty == '')
                        or (category == '')):
                    abort(400)
                # create new question object
                new_question = Question(question=question, answer=answer,
                                        category=category,
                                        difficulty=difficulty)
                new_question.insert()
            except Exception as e:
                abort(400)
            return jsonify({
                'success': True,
                'inserted_question': question
                })

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        '''
        Handles GET requests for getting questions based on category.
        '''
        # first check if category does exist or not
        category = Category.query.filter_by(id=category_id).one_or_none()
        if (category is None):
            abort(400)
        # get all questions of current category
        questions = Question.query.filter(
            Question.category == category_id).all()
        output_data = pagination(request, questions)
        return jsonify({
            'success': True,
            'questions': output_data,
            'total_questions': len(questions),
            'current_category': category.type
            })

    @app.route('/quizzes', methods=['POST'])
    def get_random_question():
        '''
        Handles POST requests for playing quiz.
        '''
        indata = json.loads(request.data)

        # abort 400 if category isn't found
        if indata is None or 'quiz_category' not in indata.keys():
            return abort(400)

        category = indata.get('quiz_category', None)
        previous_questions = indata.get('previous_questions', [])

        # load questions all questions if "ALL" is selected
        if category['id'] == 0:
            questions = Question.query.all()
        # load questions for given category
        else:
            questions = Question.query.filter(
                Question.category == category['id']).all()

        # ids of all questions
        questions_ids = [question.id for question in questions]
        # ids of all questions minus previous questions ids
        valid_ids = [x for x in questions_ids if x not in previous_questions]

        # if not found
        if len(valid_ids) == 0:
            return jsonify({
                'success': False,
                'question': None,
                'category': category['id']
                })

        return_id = random.choice(valid_ids)

        random_question = Question.query.get(return_id)

        return jsonify({
            'success': True,
            'question': random_question.format(),
            'category': category['id']
            })

    '''
    Error handlers for all expected errors
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            'error': 404,
            "message": "not found the given resource"
            }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            'error': 422,
            "message": "Unprocessable"
            }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad Request"
            }), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
            }), 500

    return app
