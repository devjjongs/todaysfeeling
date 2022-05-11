from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('13.125.6.243', 27017, username="test", password="test")
db = client.dbsparta_Todays_Vibe


# 여기부터 코드 작성 #

@app.route('/')
def home ():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login ():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/write')
def write ():
    return render_template('write.html')

# post 추가부분
@app.route('/post')
def detail ():
    return render_template("post.html")


# 로그인
@app.route('/sign_in', methods=['POST'])
def sign_in ():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 회원가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up ():
    # 입력받는 데이터
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # DB에 저장
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# ID 중복확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup ():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route("/writing", methods=["POST"])
def post_upload ():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
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
            'username': user_info["username"],
            'today': mytime,
            'weather': weather_receive,
            'word': word_receive,
            'tag': tag_receive,
            'file': f'{filename}.{extension}'
        }

        db.writes.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅이 완료되었습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        # return redirect(url_for("home"))
        return redirect('/')


@app.route("/get_posts", methods=['GET'])
def get_posts ():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅 목록 받아오기
        posts = list(db.writes.find({}).sort("date", -1).limit(20))  # 포스트 전체 목록증 최근순으로 20개만 가져오는 코드
        for post in posts:
            post["_id"] = str(post["_id"])  # 포스트 작성한 id를 문자열로 바꿔준다.
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 여기까지 코드 작성 #

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
