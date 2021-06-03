from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy #, or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8


def paginate_books(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * BOOKS_PER_SHELF
  end = start + BOOKS_PER_SHELF

  books = [book.format() for book in selection]
  current_books = books[start:end]

  return current_books

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  
  @app.route('/books', methods=['GET'])
  def retrieve_books():
    selection = Book.query.order_by(Book.id).all()
    current_books = paginate_books(request, selection)

    if len(current_books) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'books': current_books,
      'total_books': len(Book.query.all())
    })

  @app.route('/books/<int:book_id>', methods=['PATCH'])
  def update_book(book_id):

    body = request.get_json()

    try:
      book = Book.query.filter(Book.id == book_id).one_or_none()
      if book is None:
        abort(404)

      if 'rating' in body:
        book.rating = int(body.get('rating'))

      book.update()

      return jsonify({
        'success': True,
      })
      
    except:
      abort(400)

  @app.route('/books/<int:book_id>', methods=['DELETE'])
  def delete_book(book_id):
    try:
      book = Book.query.filter(Book.id == book_id).one_or_none()

      if book is None:
        abort(404)

      book.delete()
      selection = Book.query.order_by(Book.id).all()
      current_books = paginate_books(request, selection)

      return jsonify({
        'success': True,
        'deleted': book_id,
        'books': current_books,
        'total_books': len(Book.query.all())
      })

    except:
      abort(422)

  @app.route('/books', methods=['POST'])
  def create_book():
    body = request.get_json()

    new_title = body.get('title', None)
    new_author = body.get('author', None)
    new_rating = body.get('rating', None)

    try:
      book = Book(title=new_title, author=new_author, rating=new_rating)
      book.insert()

      selection = Book.query.order_by(Book.id).all()
      current_books = paginate_books(request, selection)

      return jsonify({
        'success': True,
        'created': book.id,
        'books': current_books,
        'total_books': len(Book.query.all())
      })

    except:
      abort(422)

  # @TODO: Review the above code for route handlers. 
  #        Pay special attention to the status codes used in the aborts since those are relevant for this task! 

  # @TODO: Write error handler decorators to handle AT LEAST status codes 400, 404, and 422. 
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found: indicates that the server can't find the\
           requested resource"
        }), 404
  
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "Unprocessable: the server understands the content type of\
           the request entity, and the syntax of the request entity is correct,\
              but it was unable to process the contained instruction"
        }), 422
  
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad request: the server cannot or will not process the\
           request due to something that is perceived to be a client error."
        }), 400

  @app.errorhandler(403)
  def forbidden(error):
    return jsonify({
        "success": False, 
        "error": 403,
        "message": "Forbidden: the server understood the request but refuses\
           to authorize it."
        }), 403
  
  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
        "success": False, 
        "error": 500,
        "message": "Internal server error: the server encountered an unexpected\
           condition that prevented it from fulfilling the request."
        }), 500
  
  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
        "success": False, 
        "error": 405,
        "message": "Method not allowed: the request method is known by the\
           server but is not supported by the target resource."
        }), 405

  # TEST: Practice writing curl requests. Write some requests that you know will error in expected ways.
  #       Make sure they are returning as expected. Do the same for other misformatted requests or requests missing data.
  #       If you find any error responses returning as HTML, write new error handlers for them. 

  return app

    