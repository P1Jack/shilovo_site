from flask import Flask, render_template, redirect, url_for
from data_storage.json_operate import *

app = Flask(__name__)


@app.route('/')
def main():
    lands = get_lands()
    return render_template('index.html', lands=lands)


if __name__ == "__main__":
    app.run()
