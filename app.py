from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request, Response, g
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import render_template
import jwt

app = Flask(__name__)

client = MongoClient("mongodb://jwshin:117018@13.124.249.28", 27017)
db = client.w00


def get_user(user_id):
    user = db.users.find_one({"_id": ObjectId(user_id)})

    return (
        {
            "email": user["email"],
            "name": user["name"],
            "password": user["password"],
            "description": user["description"],
        }
        if user
        else None
    )


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get("Authorization")
        if access_token is not None:
            try:
                payload = jwt.decode(access_token, "MY_SECRET_KEY", "HS256")
            except jwt.InvalidTokenError:
                payload = None

            if payload is None:
                return Response(status=401)

            user_id = payload["user_id"]
            # g: global context
            g.user_id = user_id
            g.user = get_user(user_id) if user_id else None
        else:
            return Response(status=401)

        return f(*args, **kwargs)

    return decorated_function


def get_user_by_email(email):
    return db.users.find_one({"email": email})


@app.route("/")
@login_required
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/sign-up", methods=["POST"])
def sign_up():
    form = request.form
    new_user = {
        "email": form["email"],
        "name": form["name"],
        "password": form["password"],
        "description": form["description"],
    }

    for x in new_user:
        if form[x] == "":
            raise Exception("회원가입 정보가 충분하지 않습니다.")

    if get_user_by_email(new_user["email"]):
        return "이미 사용중인 email 입니다."

    db.users.insert_one(new_user)

    return render_template("login.html")


@app.route("/sign-up-page")
def render_sign_up_page():
    return render_template("signup.html")


@app.route("/login-page")
def render_login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    credential = request.form
    email = credential["email"]
    password = credential["password"]

    row = get_user_by_email(email)
    if row == None or password != row["password"]:  # 단축 평가
        return "", 401

    user_id = str(row["_id"])
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
    }

    token = jwt.encode(payload, "MY_SECRET_KEY", "HS256")
    return jsonify({"access_token": token})


@app.route("/hello/")
@app.route("/hello/<name>")
def hello(name=None):
    return render_template("hello.html", name=name)


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
