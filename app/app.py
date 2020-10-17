import os
from flask import Flask, render_template, send_from_directory, request
from flask.helpers import send_file
from urllib.parse import unquote, quote

app = Flask(__name__)
app.config.from_pyfile('./config/config.cfg')


def get_author_folders():
    return os.listdir(app.config['BOOK_LOCATION'])


@app.route('/')
def index():
    return render_template("home.html")


@app.route('/authors/search/', methods=['POST'])
def search():
    data = request.form

    search = data["search"].lower()

    folders = get_author_folders()

    filtered_folders = []
    for folder in folders:
        if search in folder.lower():
            filtered_folders.append(folder)

    return render_template("author.html", authors=filtered_folders, unquote=unquote)


@app.route('/authors/')
def authors():
    #onlyfiles = [f for f in listdir(app.config['BOOK_LOCATION']) if isfile(join(app.config['BOOK_LOCATION'], f))]

    folders = get_author_folders()

    return render_template("author.html", authors=folders, unquote=unquote)


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


@app.route('/authors/<author_name>/<book_folder>/<book_name>')
def book(author_name, book_folder, book_name):
    author_name = unquote(author_name)
    book_folder = unquote(book_folder)
    book_name = unquote(book_name)

    try:
        return send_from_directory(directory=os.path.join(app.config['BOOK_LOCATION'], author_name, book_folder), filename=book_name,  as_attachment=True)
    except Exception as e:
        return "error: " + str(e)


@app.route("/about/")
def about():
    return "This site should allow you to download data from the rapsberry pi"


if __name__ == "__main__":
    app.run(debug=True, host=app.config["IP_ADDRESS"])
