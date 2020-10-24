import os
from flask import Flask, render_template, send_from_directory, request, url_for, redirect
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


def fetch_books_by_name(name):

    # SELECT title, author_sort FROM books
    # SELECT sort from authors
    # PRAGMA table_info(authors)

    conn = sqlite3.connect(os.path.join(
        app.config['BOOK_LOCATION'], "metadata.db"))

    files = []

    results = conn.execute(
        """SELECT path from books where title LIKE "%{0}%"; """.format(name))
    for row in results:
        path = row[0]
        path_data = path.split("/")
        author_folder = path_data[0]
        book_folder = path_data[1]

        author_folder_dir = os.path.join(
            app.config['BOOK_LOCATION'], author_folder)

        book_dir = os.path.join(author_folder_dir, book_folder)
        book_folder_content = os.listdir(book_dir)

        for file in book_folder_content:
            if len(file) > 4 and file[-5:] == ".epub":
                files.append({"book_name": quote(file),
                              "book_folder": quote(book_folder),
                              "book_author": quote(author_folder)
                              })

    return files
    # now we have the list of author name


def get_author_names():
    return AUTHORS

# HOME PAGE


@app.route('/')
def index():
    return render_template("home.html")

# GETTING EVERY AUTHOR


@app.route('/authors/page/<page>')
def authors_pages(page):
    page = int(page)

    author_names = get_author_names()

    filtered_author_names = author_names[page *
                                         NUMBER_ITEM_PER_PAGE:(page+1) * NUMBER_ITEM_PER_PAGE]

    max_page = len(author_names) // NUMBER_ITEM_PER_PAGE - 1

    previous_page = max(page - 1, 0)
    next_page = min(page + 1, max_page)

    return render_template("author.html", authors=filtered_author_names, previous_page=previous_page, next_page=next_page, unquote=unquote)


# GETTING AUTHOR FILTERED BY SEARCH

@app.route('/reload/', methods=['POST'])
def reload():
    global AUTHORS
    AUTHORS = get_author_folders()
    return redirect('/authors/page/0', code=302)


@app.route('/authors/search/', methods=['POST'])
def search():
    data = request.form
    search_keyword = data["search"].lower().strip()

    author_names = get_author_names()

    if len(search_keyword) == 0:
        return render_template("author.html", authors=[], unquote=unquote)

    # we know that we have a non empty search word here
    if search_keyword[0] == "@":
        search_keyword_book = search_keyword[1:]
        print("searching", search_keyword_book)

        author_name = "Auteurs multiples?"

        files = fetch_books_by_name(search_keyword_book)

        return render_template("author_book.html", author=author_name,  books=files, unquote=unquote)

    else:
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
                              "book_folder": quote(book_folder),
                              "book_author": quote(author_name)
                              })

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

    # fetch_books_by_name("an")

    # INIT CACE
    AUTHORS = get_author_folders()
    #AUTHORS = [str(i) for i in range(30)]

    app.run(debug=True, host=app.config["IP_ADDRESS"])
