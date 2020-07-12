import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.username = 'rohit'
        self.password = 'nfs'
        self.database_path = "postgres://{}:{}@{}/{}".format(self.username, self.password,\
         'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # sample question for use in tests
        self.new_question = {
            'question': 'Who is MS Dhoni?',
            'answer': 'India Cricket team captain',
            'difficulty': 3,
            'category': 6
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_all_categories(self):

        # make request and process response
        response = self.client().get('/categories')
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)


    def test_get_questions(self):

        # make request and process response
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['current_category'])
        self.assertEqual(len(data['questions']), 10)


    def test_out_of_bound_page(self):

        # make request and process response
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found the given resource')



    def test_delete_question(self):

        # delete mock question and process response
        question_id = Question.query.first().id
        response = self.client().delete(
            '/questions/{}'.format(question_id))
        data = json.loads(response.data)

        # ensure question does not exist
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_question'], question_id)


    def test_error_delete_question(self):
        # this tests if resource has already been deleted or doen't exist

        response = self.client().delete(
            '/questions/{}'.format(200000))
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_create_question(self):

        # make request and process response
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        # asserions to ensure successful request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['inserted_question'], self.new_question['question'])

    def test_create_question(self):

        # make request and process response
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        # asserions to ensure successful request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['inserted_question'], self.new_question['question'])


    def test_create_question_with_empty_data(self):
        new_question = {
            'question': '',
            'answer': '',
            'difficulty': 1,
            'category': 1
        }

        # make request and process response
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')

    def test_search_questions(self):

        request_data = {
            'searchTerm': 'who',
        }

        # make request and process response
        response = self.client().post('/questions', json=request_data)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['current_category'])

    def test_empty_search(self):

        request_data = {
            'searchTerm': '',
        }

        # make request and process response
        response = self.client().post('/questions', json=request_data)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')


    def test_error_search(self):
        request_data = {
            'searchTerm': 'advdvcwaDD',
        }

        # make request and process response
        response = self.client().post('/questions', json=request_data)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found the given resource')

    def test_get_questions_by_category(self):
        # make a request for the Sports category with id of 6
        response = self.client().get('/categories/6/questions')
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertEqual(data['current_category'], 'Sports')

    def test_error_get_questions_by_category(self):
        # request with invalid category id
        response = self.client().get('/categories/3435435/questions')
        data = json.loads(response.data)

        # Assertions to ensure 422 error is returned
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')

    def test_get_random_question(self):

        # mock request data
        request_data = {
                "quiz_category":{"id":3},
                "previous_questions":[13,14]
            }

        # make request and process response
        response = self.client().post('/quizzes', json=request_data)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['category'], 3)

        # Ensures previous questions are not returned
        self.assertNotEqual(data['question']['id'], 13)
        self.assertNotEqual(data['question']['id'], 14)


    def test_get_random_question_not_found(self):
        # mock request data
        request_data = {
                "quiz_category":{"id":3},
                "previous_questions":[13,14,15]
            }

        # make request and process response
        response = self.client().post('/quizzes', json=request_data)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], False)
        self.assertFalse(data['question'])
        self.assertEqual(data['category'], 3)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()