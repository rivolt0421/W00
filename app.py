from datetime import datetime, timedelta
from functools import wraps
from unittest import result
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
            "progress": user["progress"],
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


def find_user_by_email(email):
    return db.users.find_one({"email": email})


@app.route("/")
@login_required
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/users", methods=["GET"])
def get_user_by_email():
    args = request.args
    email = args.get("email")
    user = find_user_by_email(email)

    if user is None:
        return "", 404

    payload = {
        "email": user["email"],
        "name": user["name"],
    }

    return jsonify(payload)


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

    new_user["progress"] = []

    if find_user_by_email(new_user["email"]):
        return "이미 사용중인 email 입니다."

    db.users.insert_one(new_user)

    return render_template("login.html")


@app.route("/sign-up", methods=["GET"])
def render_sign_up_page():
    return render_template("signup.html")


@app.route("/login", methods=["GET"])
def render_login_page():
    return render_template("login.html")


@app.route("/projects", methods=["GET"])
def render_prj_dashboard():
    projects = [
        {"aa": 1, "bb": 2},
        {"aa": 11, "bb": 12},
    ]
    return render_template("prj_dashboard.html", projects=projects)


@app.route("/projects", methods=["POST"])
def create_project():
    project = request.json

    if project["name"] == "":
        return "프로젝트 제목이 없습니다.", 400

    if project["members"].__len__() == 0:
        return "프로젝트 팀원이 존재하지 않습니다.", 400

    members = project["members"]
    members_without_duplicate = set(map(lambda m: m["email"], members))

    if members.__len__() != members_without_duplicate.__len__():
        return "", 400

    for member in members:
        user = find_user_by_email(member["email"])
        if user is None:
            return "", 400

    result = db.projects.insert_one(project)
    project_id = result.inserted_id

    for member in members:
        user = find_user_by_email(member["email"])
        user_id = str(user["_id"])
        progress_data = {
            "projectId": project_id,
            "solvedPosts": [],
            "solved": False,
        }
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"progress": progress_data}},
        )

    return jsonify({"result": "success"})


@app.route("/create-project", methods=["GET"])
def render_create_prj_page():
    return render_template("create_project.html")


@app.route("/login", methods=["POST"])
def login():
    credential = request.form
    email = credential["email"]
    password = credential["password"]

    row = find_user_by_email(email)
    if row == None or password != row["password"]:  # 단축 평가
        return "", 401  # Unauthorized

    user_id = str(row["_id"])
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
    }

    token = jwt.encode(payload, "MY_SECRET_KEY", "HS256")
    return jsonify({"access_token": token})


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
