from flask import Flask, request, redirect, render_template, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', "blog" , "index"]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/")
def index():
    users = User.query.all()
    return render_template("index.html", users=users)

@app.route("/login", methods=['POST', 'GET'])
def login():
    username = ""
    password = ""
    if request.method== 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            flash("User does not exist. Please sign up for an account.")
            return redirect("/signup")
        if existing_user and existing_user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            flash("Invalid password")
            return render_template('login.html')

    return render_template('login.html')

@app.route("/logout")
def logout():
    del session['username']
    return redirect('/blog')

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    username = ""
    password = ""
    verify = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if not username:
            flash("Please enter a username")
            return render_template("signup.html")
        elif len(username) < 3:
            flash("Invalid username. Must be at least 3 characters.")
            return render_template("signup.html")
        elif not password:
            flash("Please enter a password")
            return render_template("signup.html")
        elif len(password) < 3:
            flash("Invalid password. Must be at least 3 characters.")
            return render_template("signup.html")
        elif not verify:
            flash("Please verify your password")
            return render_template("signup.html")
        elif verify != password:
            flash("Error. Passwords do not match.")
            return render_template("signup.html")
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash ("Username already exists. Please choose a different username.")
            return redirect("/newpost")
        
    return render_template("signup.html")

@app.route("/blog", methods=['POST', 'GET'])
def blog():
    blogs = Blog.query.all()
    users = User.query.all()
    title = "title"
    body = "body"
    if 'id' in request.args:
        blog_id = request.args.get('id')
        for blog in blogs:
            if int(blog_id) == blog.id:
                title = blog.title
                body = blog.body
                owner_id = blog.owner_id
                owner = User.query.filter_by(id=owner_id).first()
                username = owner.username
                return render_template('post.html', title=title, body=body, username=username, owner_id=owner_id)
    elif 'user' in request.args:
        user_id = request.args.get('user')
        user = User.query.filter_by(id=user_id).first()
        blogs = user.blogs
        return render_template('singleuser.html', user=user, blogs=blogs)
    else:
        return render_template("blog.html", heading="What a time to be a blog", blogs=blogs, users=users)

@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    title = ""
    body = ""
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'GET':
        return render_template("newpost.html", heading="New Blog Entry")
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if not title and not body:
            flash("Please enter a title for your blog")
            flash("Please enter a body for your blog")
            return render_template("newpost.html", heading="New Blog Entry")
        elif not title:
            flash("Please enter a title for your blog")
            return render_template("newpost.html", heading="New Blog Entry", body=body)
        elif not body:
            flash("Please enter content for your blog")
            return render_template("newpost.html", heading="New Blog Entry", title=title)
        else:
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            blogs = Blog.query.all()
            post = blogs[-1]
            post_id = post.id
            return redirect(url_for('blog', id=post_id))

    return render_template("newpost.html", heading="New Blog Entry", title=title)

if __name__ == '__main__':
    app.run()
