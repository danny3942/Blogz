from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:SecureServer@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'abc123'

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(120))
    blogz = db.relationship('Blog' , backref='Blog.user_id', primaryjoin='User.id==Blog.user_id')

    def __init__(self , name , passw):
        self.username = name
        self.password = passw

    def get_blogz(self):
        return self.blogz

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))
    user_id = db.Column(db.Integer , db.ForeignKey(User.id))

    def __init__(self, name , body , user):
        self.title = name
        self.body = body
        self.user_id = user
    
    def get_title(self):
        return self.title

    def get_body(self):
        return self.body

@app.route('/', methods=['POST', 'GET'])
def index():

    users = User.query.all()
    return render_template('index.html' , users=users , ind=True)


@app.route('/all')
def all():
    users = User.query.all()
    blogz = Blog.query.all()
    return render_template('all.html', users=users, blogs=blogz)


@app.route('/post')
def post():

    post = Blog.query.filter_by(id=request.args.get('id')).first()
    user = User.query.filter_by(id=post.user_id).first()
    return render_template('post.html', user=user, blog=post)

@app.route('/blog' , methods=['POST' , 'GET'])
def blog():

    blogz = Blog.query.all()
    return render_template('blogz.html' , blogs=blogz)

@app.route('/user')
def userblog():
    usr = User.query.filter_by(id=request.args.get('id')).first()
    blogz = Blog.query.filter_by(user_id=usr.id).all()
    return render_template('blogpage.html', blogs=blogz , user=usr)


@app.route('/newpost' , methods=['POST' , 'GET'])
def blogpost():
    if request.method=='GET':
        if 'user' in session:
            usr = User.query.filter_by(id=request.args.get('u')).first()
            return render_template('newpost.html' , id=usr.id , username=usr.username)
        else:
            return redirect('/login')
    elif request.method=='POST':
        name = request.form['title']
        body = request.form['body']
        usr = User.query.filter_by(id=request.form['id']).first()
        if name != '' and body != '' and not(name is None or body is None):

            entry = Blog(name , body , usr.id)
            db.session.add(entry)
            db.session.commit()
            blogz = Blog.query.all()
            return redirect('/user?id=' + str(usr.id))
        else:
            return render_template('newpost.html' , id=usr.id , username=usr.username, err=True, mssg="Title and Content cannot be empty!")

    return redirect('/')

@app.route("/login" , methods=['POST' , 'GET'])
def login():

    if request.method == 'POST':
        name = request.form['username']
        passw = request.form['password']
        usr = User.query.filter_by(username=name).first()
        if name != "" and passw != '' and not(name is None or passw is None):
            if usr.password == passw:
                session['user'] = usr.username
                return render_template('index.html' , id=usr.id , username=usr.username, loggedin=True)
            else:
                return render_template('login.html' , err=True, mssg="Username or Password is incorrect!")
        else:
            return render_template('login.html', err=True, mssg="Username and password required!")
    else:    
        return render_template('login.html')


@app.route('/logout' , methods=['POST' , 'GET'])
def logout():
    if 'user' in session:
        del session['user']
    
    return redirect('/')


@app.route("/register" , methods=['POST' , 'GET'])
def register():
    eru = False
    erp = False
    erv = False
    eru_mssg = ""
    erv_mssg = ""
    erp_mssg = ""
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        ver = request.form['verify']
        if username == password:
            eru = True
            eru_mssg+= "Username and Password cannot match! "

        if ver != password:
            erv = True
            erv_mssg+= "Passwords must match! "

        if len(password) < 3 or len(password) > 25:
            erp = True
            erp_mssg+= "Password must be between 3 and 25 characters! "

        if len(username) < 3 or len(username) > 25:
            eru = True
            eru_mssg+= "username must be between 3 and 25 characters! "

        if eru or erv or erp:
            return render_template('register.html', errv=erv, erru=eru, errp=erp, mssg1=eru_mssg, mssg2=erv_mssg, mssg3=erp_mssg)
        else:
            new_user = User(username , password)
            db.session.add(new_user)
            db.session.commit()
            user = User.query.filter_by(username=username).first()
            return render_template('login.html' , new=True , username=user.username , id=user.id)
    else:
        return render_template('register.html')



if __name__ == '__main__':
    app.run()