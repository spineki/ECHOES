import os
from flask import Flask, render_template, send_from_directory, request, url_for
from flask.helpers import send_file
from urllib.parse import unquote, quote
import sqlite3


app = Flask(__name__)
app.config.from_pyfile('./config/config.cfg')

# VARIABLES -------------------------------------
# Cached data
AUTHORS = []
BOOKS = []

# Database
conn = sqlite3.connect(os.path.join(
    app.config['BOOK_LOCATION'], "metadata.db"))


# page displaying
NUMBER_ITEM_PER_PAGE = 5


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

def get_author_folders():
    return os.listdir(app.config['BOOK_LOCATION'])

def get_author_names():
    return AUTHORS

# HOME PAGE
@app.route('/')
def index():
    return render_template("home.html")

# GETTING EVERY AUTHOR
@app.route('/authors/')
def authors():
    #onlyfiles = [f for f in listdir(app.config['BOOK_LOCATION']) if isfile(join(app.config['BOOK_LOCATION'], f))]
    author_names = get_author_names()
    return render_template("author.html", authors=author_names, unquote=unquote)

# GETTING AUTHOR FILTERED BY SEARCH
@app.route('/authors/search/', methods=['POST'])
def search():
    data = request.form
    search_keyword = data["search"].lower()

    author_names = get_author_names()

    filtered_author_names = []
    for author_name in author_names:
        if search_keyword in author_name.lower():
            filtered_author_names.append(author_name)

    return render_template("author.html", authors=filtered_author_names, unquote=unquote)


# GETTING EVERY BOOK FROM ONE AUTHOR
@app.route('/authors/<author_name>/')
def author(author_name):
    #onlyfiles = [f for f in listdir(app.config['BOOK_LOCATION']) if isfile(join(app.config['BOOK_LOCATION'], f))]
    author_name = unquote(author_name)

    author_folder_dir = os.path.join(app.config['BOOK_LOCATION'], author_name)

    books_folder = os.listdir(author_folder_dir)

    files = []
    for book_folder in books_folder:
        book_dir = os.path.join(author_folder_dir, book_folder)
        book_folder_content = os.listdir(book_dir)

        for file in book_folder_content:
            if len(file) > 4 and file[-5:] == ".epub":
                files.append({"book_name": quote(file),
                              "book_folder": quote(book_folder)})

    return render_template("author_book.html", author=author_name,  books=files, unquote=unquote)

# GETTING A BOOK
@app.route('/authors/<author_name>/<book_folder>/<book_name>')
def book(author_name, book_folder, book_name):
    author_name = unquote(author_name)
    book_folder = unquote(book_folder)
    book_name = unquote(book_name)

    try:
        return send_from_directory(directory=os.path.join(app.config['BOOK_LOCATION'], author_name, book_folder), filename=book_name,  as_attachment=True)
    except Exception as e:
        return "error: " + str(e)


if __name__ == "__main__":

    # INIT CACE
    AUTHORS = get_author_folders()


    app.run(debug=True, host=app.config["IP_ADDRESS"])
