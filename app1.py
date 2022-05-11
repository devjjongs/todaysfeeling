from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('13.125.6.243', 27017, username="test", password="test")
db = client.dbsparta_Todays_Vibe


# 여기부터 코드 작성

@app.route('/')
def home ():
    return render_template('index.html')

@app.route('/post')
def post ():
    return render_template('post.html')

@app.route("/writing", methods=["POST"])
def post_upload():
    # token_receive = requestuest.cookies.get('mytoken')
    try:
        # payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # user_info = db.users.find_one({"username": payload["id"]})
        date_receive = request.form['date_give']
        weather_receive = request.form['weather_give']
        word_receive = request.form['word_give']
        tag_receive = request.form['tag_give']

        doc = {
            # 'username': user_info["username"],
            'date': date_receive,
            'weather': weather_receive,
            'word': word_receive,
            'tag': tag_receive
        }

        db.writes.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅이 완료되었습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# 여기까지 코드 작성

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)