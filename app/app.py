import os
from typing import Dict, List
from flask import Flask, render_template, send_from_directory, request, url_for, redirect
from flask.helpers import send_file
from urllib.parse import unquote, quote
import sqlite3

from scripts.fourtoutici import get_download_page_links, download_file

app = Flask(__name__)
app.config.from_pyfile('./config/config.cfg')

# Flask helpers


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

# Database fetching


def fetch_books_by_name(name) -> List[Dict[str, str]]:

    # SELECT title, author_sort FROM books
    # SELECT sort from authors
    # PRAGMA table_info(authors)
    # needed because of tread problems
    conn = sqlite3.connect(os.path.join(
        app.config['BOOK_LOCATION'], "metadata.db"))

    files = []

    results = conn.execute(
        """SELECT path from books where title LIKE "%{0}%"; """.format(name))
    for row in results:
        try:
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
        except Exception as e:
            print("error with")
            print(row)
            print(str(e))

    return files
    # now we have the list of author name


def fetch_books_by_sort(author_sort: str) -> List[Dict[str, str]]:
    # needed because of tread problems
    conn = sqlite3.connect(os.path.join(
        app.config['BOOK_LOCATION'], "metadata.db"))

    files = []

    print(author_sort)

    results = conn.execute(
        """SELECT path from books where author_sort LIKE "{0}"; """.format(author_sort))
    for row in results:
        try:
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
        except Exception as e:
            print("error with")
            print(row)
            print(str(e))

    return files
    # now we have the list of author name


def fetch_author_by_name(name) -> List[Dict[str, str]]:

    # needed because of tread problems
    conn = sqlite3.connect(os.path.join(
        app.config['BOOK_LOCATION'], "metadata.db"))

    files = []
    results = conn.execute(
        """SELECT name, sort from authors where name LIKE "%{0}%";""".format(name))

    for row in results:
        try:
            author_name = row[0]
            author_sort = row[1]
            files.append(
                {
                    "author_name": quote(author_name),
                    "author_sort": quote(author_sort)
                }
            )
        except Exception as e:
            print("error with")
            print(row)
            print(str(e))
    return files

# HOME PAGE


@app.route('/')
def index():
    return render_template("search.html")

# searches


@app.route('/search/book/', methods=['GET'])
def search_book():
    """
    function to search book having the given name
    """

    data = request.args
    search_book_name: str = data.get("keyword", default=None)
    search_author_sort: str = data.get('sort', default=None, type=str)

    books = []

    # looking directly for book name
    if search_author_sort is None:
        search_book_name = search_book_name.lower().strip()
        books = fetch_books_by_name(search_book_name)
    else:

        books = fetch_books_by_sort(unquote(search_author_sort))

    results = [
        {
            "title": book["book_name"] + " : " + book["book_author"],
            "link":  "/download/?author_name={0}&book_folder={1}&book_name={2}".format(book['book_author'], book['book_folder'], book['book_name'])
        }

        for book in books]

    return render_template("results.html", results=results, unquote=unquote, len=len)


@app.route('/search/author/', methods=['GET'])
def search_author():
    """
    function to search author having the given name
    """

    data = request.args
    search_keyword: str = data["keyword"].lower().strip()

    authors = fetch_author_by_name(search_keyword)

    results = [
        {
            "title": author["author_name"],
            "link":  "/search/book/?sort={0}".format(author['author_sort'])
        }
        for author in authors]

    return render_template("results.html", results=results, unquote=unquote, len=len)


@app.route('/search/fourtoutici/', methods=['GET'])
def search_fourtoutici():
    """
    function to search things on fourtoutici having the given name
    """

    data = request.args
    search_keyword: str = data["keyword"].lower().strip()

    searches, error_code = get_download_page_links(search_keyword)

    results = [
        {
            "title": search["title"],
            "link":  "/download-fourtoutici/?title={0}&directory={1}".format(quote(search["title"]), quote(search["directory"]))
        }
        for search in searches]

    return render_template("results.html", results=results, unquote=unquote, len=len)


@app.route('/download-fourtoutici/', methods={"GET"})
def download_fourtoutici():

    data = request.args

    title = data["title"]
    directory = data["directory"]

    output_dir = os.path.join(app.root_path, 'downloads')

    final_path = download_file(
        title=title, directory=directory, output_dir=output_dir)

    print(final_path)
    return send_file(filename_or_fp=final_path,  as_attachment=True)

    # ---------------------------------------------------------------------------------

    # GETTING AUTHOR FILTERED BY SEARCH


@app.route('/download/')
def download():
    data = request.args

    author_name = unquote(data["author_name"])
    book_folder = unquote(data["book_folder"])
    book_name = unquote(data["book_name"])

    try:
        return send_from_directory(directory=os.path.join(app.config['BOOK_LOCATION'], author_name, book_folder), filename=book_name,  as_attachment=True)
    except Exception as e:
        return "error: " + str(e)


if __name__ == "__main__":

    # fetch_books_by_name("an")

    # INIT CACE
    # AUTHORS = get_author_folders()
    #AUTHORS = [str(i) for i in range(30)]

    app.run(debug=True, host=app.config["IP_ADDRESS"])
