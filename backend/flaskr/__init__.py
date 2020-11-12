
import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from random import randint
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    """
    :return app
    """
    # create and configure the app => DONE
    app = Flask(__name__)
    setup_db(app)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    # => DONE
    CORS(app, resources={r'/api/*': {'origins': '*'}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    => DONE
    '''
    # => DONE
    @app.after_request
    def after_request(response):
        """
        headers setup
        """
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type-Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    def paginate_models(request, selection):
        """

        :param [request, selection: all selected records from the model]
        :return the paginated records from the models
        """
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        models = [model.format() for model in selection]
        current_models = models[start:end]
        return current_models

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    # => DONE
    @app.route('/categories')
    def get_all_categories():
        """

        :return ['success_state', 'list_of_categories']
        """
        categories = Category.query.order_by(Category.id).all()
        # categories don't need a pagination
        # current_categories = paginate_models(request, categories)

        if categories is None:
            abort(404)

        categories_list = []
        for category in categories:
            categories_list.append(category.type)

        return jsonify({
            'success': True,
            'categories': categories_list,
        })

    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
  
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    # => DONE
    @app.route('/questions')
    def get_all_questions():
        """
        :return json object for all questions
        """
        questions = Question.query.order_by(Question.id).all()

        if questions is None:
            abort(404)

        questions_list = paginate_models(request, questions)

        return jsonify({
            'success': True,
            'questions': questions_list,
            'questions count': Question.query.all().count()
        })

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
  
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    # => DONE
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        delete specific question depend on question's id
        """
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        question.delete()

        return jsonify({
            'success': True,
            'deleted question': question_id
        })

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
  
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    # => DONE
    @app.route('/questions', methods=['POST'])
    def add_new_question():
        """
        add a new question
        """
        data = request.get_json()
        new_question = Question(
            data['question'],
            data['answer'],
            data['category'],
            data['difficulty']
        )

        try:
            new_question.insert()
        except Exception.args:
            abort(404)

        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_models(request, questions)

        return jsonify({
            'success': True,
            'created': new_question.id,
            'questions': current_questions,
            'total_questions': len(questions)
        })

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
  
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    # => DONE
    @app.route('/questions/search', methods=['post'])
    def search_for_question():
        """
        search for a question based on terms
        """
        data = request.get_json()
        search_term = data.get('search_term', None)
        questions = Question.query.filter(
            Question.question.ilike('%' + search_term + '%')
        ).all()
        questions_count = len(questions)

        if questions_count == 0:
            abort(404)

        formatted_question = [question.format() for question in questions]

        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        categories_list = []
        for category in categories:
            categories_list.append(
                category.type
            )

            return jsonify({
                'success': True,
                'questions': formatted_question,
                'total_questions': questions_count,
                'current_category': categories_list
            })

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
  
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    # => DONE
    @app.route('/categories/<int:category_id>/questions')
    def questions_based_on_category(category_id):
        """
        questions_based_on_category
        """
        questions = Question.query.filter_by(category=category_id).all()

        if questions is None:
            abort(404)

        paginated_questions = paginate_models(request, questions)

        if len(paginated_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(questions),
            'current_category': category_id
        })

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
  
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 

    '''
    # => DONE
    @app.route('/quiz', methods=['POST'])
    def play():
        """
        play quiz
        """
        global random_question

        data = request.get_json()
        previous_questions = data.get('previous_questions', None)
        category = data.get('quiz_category', None)

        try:
            if not previous_questions:
                if not category:
                    questions = Question.query.filter(Question.category == category['id']).all()
                else:
                    questions = Question.query.all()
            else:
                if category:
                    questions = Question.query.filter(
                        Question.category == category['id']).filter(
                        Question.id.notin_(previous_questions)).all()
                else:
                    questions = Question.query.filter(
                        Question.id.notin_(previous_questions)).all()
            formatted_question = [question.format()for question in questions]
            question_count = len(formatted_question)

            if question_count ==0:
                abort(404)

            random_question = formatted_question[randint(0, len(formatted_question))]
        except Exception:
            abort(404)

        return jsonify({
            'success': True,
            'question': random_question
        })

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    => DONE
    '''
    @app.errorhandler(422)
    def unprocessable(error):
        """
        :return unprocessable in json format
        """
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(404)
    def not_found(error):
        """
        :return not_found in json format
        """
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'not found'
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        """
        :return bad_request in json format
        """
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        """
        :return method_not_allowed in json format
        """
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    return app
