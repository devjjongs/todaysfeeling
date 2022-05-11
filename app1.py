from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

from pymongo import MongoClient
from datetime import datetime

client = MongoClient('13.125.6.243', 27017, username="test", password="test")
db = client.dbsparta_Todays_Vibe


# 여기부터 코드 작성

@app.route('/')
def home ():
    return render_template('/index.html')

@app.route('/post')
def post ():
    return render_template('/post.html')

@app.route("/writing", methods=["POST"])
def post_upload():
    # token_receive = requestuest.cookies.get('mytoken')
    # try:
        # payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # user_info = db.users.find_one({"username": payload["id"]})
        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
        weather_receive = request.form['weather_give']
        word_receive = request.form['word_give']
        tag_receive = request.form['tag_give']

        file = request.files['file_give']
        extension = file.filename.split('.')[-1]
        filename = f'file-{mytime}'
        save_to = f'static/images/{filename}.{extension}'

        file.save(save_to)

        # 사용자 ID 추가하는 기능 필요

        doc = {
            # 'username': user_info["username"],
            'today': mytime,
            'weather': weather_receive,
            'word': word_receive,
            'tag': tag_receive,
            'file': f'{filename}.{extension}'
        }

        db.writes.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅이 완료되었습니다.'})
    # except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
    #     return redirect(url_for("home"))

# 여기까지 코드 작성

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)