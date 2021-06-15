from flask import Flask, render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import date, datetime
from werkzeug.utils import secure_filename
import json
import os
import math



local_server=True
with open("config.json",'r') as c:
    params=json.load(c)["params"]



app = Flask(__name__)
app.config['UPLOAD_FOLDER']=params['upload_location']
app.secret_key = params['secretcode']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME='beingamanullah9@gmail.com',
    MAIL_PASSWORD='jhklfeazadyzqxgn'

)
mail=Mail(app)
if (local_server):


    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_url"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_url"]

db = SQLAlchemy(app)

class Contacts(db.Model):
    Sno= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    mail = db.Column(db.String(120), unique=False, nullable=False)
    phone_num = db.Column(db.String(12),nullable=True)
    message = db.Column(db.String(500), unique=False, nullable=False)
    
class Posts(db.Model):
    Sno= db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(21),nullable=False)
    title = db.Column(db.String(120), unique=False, nullable=False)
    content = db.Column(db.String(200),nullable=True)
    date = db.Column(db.String(12), nullable=True)

@app.route("/delete/<string:Sno>",methods=['GET','POST'])
def delete(Sno):
    if 'user' in session and session['user']==params['admin_user']:
        post=Posts.query.filter_by(Sno=Sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect("/dashboard")
        
            

@app.route("/edit/<string:Sno>",methods=['GET','POST'])
def edit(Sno):
    if 'user' in session and session['user']==params['admin_user']:
        if request.method=='POST':
            box_title=request.form.get('title')
            new_slug=request.form.get('slug')
            new_content=request.form.get('content')
            date=datetime.now()

            if Sno=='0':
                post=Posts(title=box_title,slug=new_slug,content=new_content,date=date)
                db.session.add(post)
                db.session.commit()
            else: 
                post=Posts.query.filter_by(Sno=Sno).first()
                post.title=box_title
                post.slug=new_slug
                post.content=new_content
                post.date=date
                db.session.commit()
                return redirect('/edit/'+Sno)
        post=Posts.query.filter_by(Sno=Sno).first()
        return render_template('edit.html',params=params,post=post)



@app.route("/logout",methods=['GET','POST'])
def logout():
    session.pop("user")
    return redirect("/dashboard")

@app.route("/uploader",methods=['GET','POST'])
def uploader():
    if 'user' in session and session['user']==params['admin_user']:
        if request.method=="POST":
            f=request.files['file']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "YOUR FILE UPLOADED SUCCESSFULLY"




@app.route('/dashboard',methods=['GET','POST'])
def dashboard():   
    if 'user' in session and session['user']==params['admin_user']:
        posts=Posts.query.all()
        return render_template("dashboard.html",params=params,posts=posts)
    if request.method=='POST':
        username= request.form.get('uname')
        password= request.form.get('pass')
        if (username==params['admin_user'] and password==params['admin_pass']):
            posts=Posts.query.all()
            session['user']=username
            return render_template("dashboard.html",params=params,posts=posts)
        #redirect to admin page
    else:
        return render_template('login.html',params=params)
    
  
    
    
    
    
@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)
    
    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)


@app.route('/about')
def about():

    return render_template('about.html',params=params)


@app.route('/contact',methods=['GET','POST'])
def contact():
    if(request.method=='POST'):
        '''add entry to the database'''
        name=request.form.get("name")
        mobile=request.form.get("mobile")
        email=request.form.get("email")
        Message=request.form.get("msg")

        entry=Contacts(name=name,phone_num=mobile,mail=email,message=Message)
        db.session.add(entry)
        db.session.commit()
        mail.send_message("hey! new message from"+name,sender=email,recipients=[params["gmail_user"]],
        body=Message +"\n"+mobile)

    return render_template('contact.html',params=params)

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    
    return render_template('post.html',params=params,post=post)


app.run(debug=True)
