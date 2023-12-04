import time
import threading
import requests
import pymysql
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['POST'])
def process_request():
    pass


if __name__ == '__main__':
    app.run()
