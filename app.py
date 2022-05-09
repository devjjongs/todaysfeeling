from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

from pymongo import MongoClient
import certifi

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.zuy17.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta


# 여기부터 코드 작성

@app.route('/')
def home ():
    return render_template('index.html')


# 여기까지 코드 작성

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)