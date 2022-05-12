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


# write 이동
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


# /post : 포스팅 조회값 불러오기
@app.route("/get_posts", methods=['GET'])
def get_posts ():
    try:
        # 포스팅 목록 받아오기
        posts = list(db.writes.find({}).sort("date", -1).limit(12))  # 포스트 전체 목록증 최근순으로 12개만 가져오는 코드
        for post in posts:
            post["_id"] = str(post["_id"])  # 포스트 작성한 id를 문자열로 바꿔준다.
        return jsonify({"result": "success", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 이건 포스트 하나만 가져오는 함수
@app.route("/get_post", methods=['GET'])
def get_post ():
    token_receive = request.cookies.get('mytoken')
    post_id_receive = request.form['post_id_give']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅 목록 받아오기
        post_id = str(post_id_receive)
        post = list(db.writes.find_one({"post_id": post_id}))
        post["_id"] = str(post["_id"])  # 포스트 작성한 id를 문자열로 바꿔준다.
        post["count_heart"] = db.likes.count_documents({"post_id": post["_id"]})
        post["heart_by_me"] = bool(
            db.likes.find_one({"post_id": post["_id"], "username": payload['id']}))
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "post": post})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/update_like", methods=['POST'])
def update_like ():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# /comments : 댓글 올리기
@app.route("/post/comment_up", methods=["POST"])
def comment_post ():
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰을 넘겨주지 않아도 토큰리시브(쿠키스)로 항상 가져올 수 있다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        user_info = db.users.find_one({"username": payload["id"]})
        date_receive = request.form["date_give"]
        comment_receive = request.form['comment_give']

        doc = {
            "username": user_info["username"],
            'comment': comment_receive,
            "date": date_receive
        }
        db.comments.insert_one(doc)

        return jsonify({'msg': '댓글 작성 완료!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect('/post')


# /comments : 댓글 값 조회하기
@app.route("/post/comment_search", methods=["GET"])
def comment_get ():
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰을 넘겨주지 않아도 토큰리시브(쿠키스)로 항상 가져올 수 있다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        comment_list = list(db.comments.find({}, {'_id': False}))

        return jsonify({'comments': comment_list})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect('/post')

# 여기까지 코드 작성 #

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
