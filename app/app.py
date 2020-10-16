from flask import Flask, render_template, send_from_directory

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello world !"


@app.route("/book/<book_name>/")
def book(book_name):
    try:
        return send_from_directory(directory="./static/data/", filename=book_name,  as_attachment=True)
    except Exception as e:
        return "error: " + str(e)

    



@app.route("/about/")
def about():
    return "This site should allow you to download data from the rapsberry pi"


if __name__ == "__main__":
    app.run(debug=True, host='192.168.1.130')
