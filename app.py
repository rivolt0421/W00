from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
  
@app.route("/signup")
def sign_up():
    return render_template('signup.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)
  
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)