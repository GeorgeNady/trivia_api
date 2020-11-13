import os
from random import randint
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
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

    # => DONE
    CORS(app, resources={r'/api/*': {'origins': '*'}})

    # => DONE
    @app.after_request
    def after_request(response):
        """
        headers setup
        """
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type-Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
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

    # => DONE
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        delete specific question depend on question's id
        """
        question = Question.query.filter(Question.id == question_id)\
            .one_or_none()

        if question is None:
            abort(404)

        question.delete()

        return jsonify({
            'success': True,
            'deleted question': question_id
        })

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
                    questions = Question.query.\
                        filter(Question.category == category['id'])\
                        .all()
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

            if question_count == 0:
                abort(404)

            random_question = formatted_question[randint(0, question_count)]
        except Exception:
            abort(404)

        return jsonify({
            'success': True,
            'question': random_question
        })

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
