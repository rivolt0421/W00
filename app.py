from datetime import datetime, timedelta
from functools import wraps
from os import access
from unittest import result
from flask import Flask, jsonify, request, Response, g ,redirect, url_for 
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import render_template
from bs4 import BeautifulSoup

import jwt
import requests


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

def get_post(post_id):
    post = db.posts.find_one({"_id" : ObjectId(post_id)})

    return (
        {
            "url": post["url"],
            "project": post["project"],
            "reasons": post["reasons"],
            "quizs": post["quizs"],
        }
        if post
        else None
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.args.get('token')
        if access_token is not None:
            try:
                payload = jwt.decode(access_token, "MY_SECRET_KEY", "HS256")
            except jwt.InvalidTokenError:
                payload = None

            if payload is None:
                return redirect(url_for('login'))

            user_id = payload["user_id"]
            # g: global context
            g.user_id = user_id
            g.user = get_user(user_id) if user_id else None
        else:
            return redirect(url_for('login'))

        return f(*args, **kwargs)

    return decorated_function


def find_user_by_email(email):
    return db.users.find_one({"email": email})

@app.route("/post/<post_id>", methods=['GET'])
#@login_required
def post_detail(post_id):
    post = db.posts.find_one({"_id" : ObjectId(post_id)})
    url = post['url']
    reasons = post['reasons']
    quizs = post['quizs']
    return render_template("post.html", url=url, reasons=reasons, quizs=quizs)
def get_project(pjt_id):
    project = db.projects.find_one({"_id": ObjectId(pjt_id)})

    return (
        {
            "name": project["name"],
            "members": project["members"],
            "posts": project["posts"]
        }
        if project
        else None
    )

def get_post(post_id):
    post = db.posts.find_one({"_id": ObjectId(post_id)})

    return (
        {
            "post_id": post_id,
            "url": post["url"],
            "project": post["project"],
            "reasons": post["reasons"],
            "quizs": post["quizs"]
        }
        if post
        else None
    )
 
def do_scrap(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html5lib')
    img = soup.select_one('meta[property="og:image"]')
    title = soup.select_one('meta[property="og:title"]')
    
    if title is None :
        title = soup.select_one('title').text
    else :
        title = title['content']

    if img is None :
        img = ""
    else :
        img = img['content'].strip()

    return( 
        {   
            "img": img,
            "title": title
        }
    )    


@app.route("/modify/<post_id>", methods=['GET'])
#@login_required
def post_modify(post_id):
    post = db.posts.find_one({"_id" : ObjectId(post_id)})
    url = post['url']
    reasons = post['reasons']
    quizs = post['quizs']
    return render_template("post-modify.html", url=url, reasons=reasons, quizs=quizs)
    
@app.route("/")
@login_required
def hello_world():
    # return "hello"
    return render_template("hello.html")


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

@app.route("/checkToken", methods=["GET"])
def check_token():
    return "hello"

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route("/login", methods=["GET"])
def render_login_page():
    return render_template("login.html")


@app.route("/projects", methods=["GET"])
@login_required
def render_prj_dashboard():
  # 쿼리스트링으로 검증 아니면 메인
    # token = request.args.get('token')

    projects = [
        {"aa": 1, "bb": 2},
        {"aa": 11, "bb": 12},
    ]

    return render_template("dashboard.html" , projects=projects)


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
    credential = request.json
    email = credential["email"]
    password = credential["password"]

    row = find_user_by_email(email)
    if row == None or password != str(row["password"]):  # 단축 평가
        return "", 401  # Unauthorized

    user_id = str(row["_id"])
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
    }

    token = jwt.encode(payload, "MY_SECRET_KEY", "HS256")
    
    return jsonify({"access_token": token})

@app.route("/post-dashboard", methods=["GET"])
def render_post_dashboard():
    pjt_id = "632a9ff17cdffa2611dbfb2c"
    project = get_project(pjt_id)
    pjt_name = project["name"]
    members = project["members"]
    posts = project["posts"]
    post_metas = []

    for post_id in posts:
        post = get_post(post_id)
        url = post["url"]

        url_meta = do_scrap(url)
        img = url_meta["img"]
        title = url_meta["title"]

        post_meta = {
            "post_id" : post_id,
            "url" : url,
            "img" : img,
            "title" : title
        }
        post_metas.append(post_meta)
        # user progress 추가 필요

    return render_template("post-dashboard.html", post_metas = post_metas, pjt_name = pjt_name, members = members)

@app.route("/post-form", methods=["GET"])
def render_post_form():
    return render_template("post-form.html")


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
