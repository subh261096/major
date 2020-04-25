from wtforms import Form, TextField, PasswordField, validators
from flask import Flask, render_template, request, flash, url_for, redirect, session, jsonify
from HashingFunction import hashfunction
from flask_sqlalchemy import SQLAlchemy
from logging.config import dictConfig
from passlib.hash import sha256_crypt
from functools import wraps, partial
from sqlalchemy import DateTime
from datetime import timedelta
import datetime
import time
import pymysql

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


app = Flask(__name__)

######################################### CONFIGRATION OF DATABSE ######################################
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:subh261096@localhost:5432/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://nbjddnrtflahdi:52ab741ca2a00fa065058f7613581c5f5e8bac12f49500d4248c42ca7ef59337@ec2-18-215-99-63.compute-1.amazonaws.com:5432/d2iimlldlcqt7j'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'subh261096'
db = SQLAlchemy(app)


#########################################     END     #############################################

######################################### DATABSE TABLES ################################################


                    ########################## USER TABLE ######################
class Users(db.Model):
    __tablename__ = 'Users'
    VoterId = db.Column(db.String(30), primary_key=True)
    UserName = db.Column(db.String(30))
    Password = db.Column(db.String(500))
    IsAdmin = db.Column(db.Boolean, default=False)
    RegisterDate = db.Column(DateTime, default=datetime.datetime.utcnow)
                    ########################### END #########################   


                    ######################### USER LIST ###################
class Elections(db.Model):
    __tablename__ = 'Elections'
    ElectionName = db.Column(db.String(30), primary_key=True)
    OpenedAt = db.Column(DateTime, default=datetime.datetime.utcnow)
    ClosedAt = db.Column(DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
    IsOpen= db.Column(db.Boolean,default=False)
    Elections = db.relationship('VotingList', cascade="all,delete", backref='Elections')
                    ############################### END ##########################

class VotingList(db.Model):
    __tablename__ = 'VotingList'
    ElectionName=db.Column(db.String(30),db.ForeignKey('Elections.ElectionName'),primary_key=True)
    VoterId=db.Column(db.String(50),primary_key=True)
    PartyName=db.Column(db.String(50),nullable=False)
    MacCount=db.Column(db.Integer,nullable=False)
    PrevMac = db.Column(db.String(16),nullable=False)
    NewMac = db.Column(db.String(16), nullable=False)
    LastModifiedDate = db.Column(DateTime, default=datetime.datetime.utcnow)    

############################################## END ######################################################







######################################### REGISTRATION FORM #########################################
class RegistrationForm(Form):
    username = TextField('UserName', [validators.DataRequired(),validators.Length(min=4, max=20)])
    voterId = TextField("voterId", [validators.DataRequired(),validators.Length(min=5, max=18)])
    password = PasswordField('Password', [validators.DataRequired()])
    confirm = PasswordField('Confirm Password',[validators.EqualTo('password',
                                                            message="Passwords must match")])
######################################### END #######################################################

def CloseElection():
    time.sleep(2)
    print("he")





######################################### VERIFY LOGIN #############################################
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('UnAuthorised!, Please Login First!', 'danger')
            return redirect(url_for('login'))
    return wrap
######################################### END #######################################################

######################################### VERIFY ADMIN ##############################################


def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'IsAdmin' in session:
            return f(*args, **kwargs)
        else:
            flash('Only Admin is Allowed !!, Please Login as Admin First!', 'danger')
            return redirect(url_for('Adminlogin'))
    return wrap
######################################### END #######################################################

def already_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return f(*args, **kwargs)
        else:
            flash('Already Logged In!', 'danger')
            return redirect(url_for('home'))
            ##important indentation
    return wrap


######################################### SIGN UP #####################################################
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = RegistrationForm(request.form)

    if request.method == "POST" and form.validate():  # if the form info is valid
        username = form.username.data
        voterId = form.voterId.data
        password = sha256_crypt.hash(str(form.password.data))
        data_model = Users(UserName=username,
                        Password=password, VoterId=voterId)
        save_to_database = db.session
        if(Users.query.filter_by(UserName=username).count() == 0):
            try:
                save_to_database.add(data_model)
                save_to_database.commit()
                uid = Users.query.filter_by(UserName=username).first().VoterId
                flash('Registered Successfully!', "success")
                return redirect(url_for('login'))
            except Exception as e:
                save_to_database.rollback()
                save_to_database.flush()
                print(e)
                flash("Can't Register Now!, please try again Later..", "info")
            return render_template('Signup.html', form=form)
        else:
            flash("User Already Exists! Please Enter Unique username!", "info")
            return render_template('Signup.html', form=form)
    return render_template("Signup.html", form=form)
######################################### END #########################################################







######################################### LOG IN ######################################################
@app.route('/login', methods=['GET', 'POST'])
@already_logged_in
def login():
    if request.method == "POST":
        attempted_UserName = request.form['userName']
        attempted_password = request.form['password']

        if (Users.query.filter_by(UserName=attempted_UserName).count()) == 0:
            flash("UserName not found. Type correct UserName, or create an account.","danger")
            return render_template("Login.html")
        data_model = Users.query.filter_by(UserName=attempted_UserName).first()
        try:
            if attempted_UserName == data_model.UserName and sha256_crypt.verify(attempted_password, data_model.Password):
                session.permanent = True
                # setting session timeout
                app.permanent_session_lifetime = timedelta(minutes=5)
                session['logged_in'] = True
                session['uid'] = data_model.VoterId
                session['UserName'] = data_model.UserName
                flash("Welcome %s!" % (data_model.UserName),"success")
                return redirect(url_for("home"))
            else:
                flash("Incorrect password, try again","danger")
                return render_template("Login.html")
        except Exception as e:
            return str(e)
    return render_template("Login.html")

######################################### END #########################################################

######################################### Admin LOG IN ######################################################
@app.route('/adminlogin', methods=['GET', 'POST'])
def Adminlogin():
    if request.method == "POST":
        attempted_UserName = request.form['userName']
        attempted_password = request.form['password']

        if (Users.query.filter_by(UserName=attempted_UserName,IsAdmin=True).count()) == 0:
            flash(
                "Not Admin!! Please get Admin privileges", "danger")
            return render_template("AdminLogin.html")
        data_model = Users.query.filter_by(UserName=attempted_UserName).first()
        try:
            if attempted_UserName == data_model.UserName and sha256_crypt.verify(attempted_password, data_model.Password):
                session.permanent = True
                # setting session timeout
                app.permanent_session_lifetime = timedelta(minutes=5)
                session['logged_in'] = True
                session['IsAdmin'] = data_model.IsAdmin
                session['uid'] = data_model.VoterId
                session['UserName'] = data_model.UserName
                flash("Welcome %s!" % (data_model.UserName),"success")
                return redirect(url_for("home"))
            else:
                flash("Incorrect password, try again","danger")
                return render_template("AdminLogin.html")
        except Exception as e:
            return str(e)
    return render_template("AdminLogin.html")

######################################### END #########################################################


######################################### LOG OUT ######################################################
@app.route('/logout', methods=['GET', 'POST'])
@is_logged_in
def logout():
    session.pop('logged_in', False)
    session.pop('username', None)
    session.pop('IsAdmin',False)
    flash("You have been logged out.","success")
    return redirect(url_for('home'))
######################################### END ###########################################################

#################################### CREATE ELECTION ####################################################
@app.route('/createElection',methods=['GET','POST'])
@is_admin
def createElection():
    if request.method == "POST":
        ElectionName = request.form['ElectionName']
        InitialMac = request.form['InitialMac']
        if (Elections.query.filter_by(ElectionName=ElectionName).count() != 0):
            flash("This Election name is already present!! Please Add Current Year in Election Name !!", "danger")
            return render_template("CreateElection.html")
        else:
            data_model = Elections(ElectionName=ElectionName,IsOpen=True)
            vote_model = VotingList(ElectionName=ElectionName, VoterId=(ElectionName+"Admin"), PartyName="None",MacCount=0, PrevMac="None", NewMac=InitialMac)
            save_to_database = db.session
            try:
                save_to_database.add(data_model)
                save_to_database.add(vote_model)
                save_to_database.commit()
                flash('Election Created Successfully!',"success")
                return redirect(url_for('home'))
            except Exception as e:
                save_to_database.rollback()
                save_to_database.flush()
                print(e)
                flash("Can't Create Rights Now!, please try again Later..","info")
    return render_template("CreateElection.html")
######################################### END ###########################################################

#################################### CREATE ELECTION ####################################################
@app.route('/endElection', methods=['GET', 'POST'])
@is_admin
def endElection():
    if request.method == "POST":
        ElectionName = request.form.get("party_name")
        data_model = Elections.query.get(ElectionName)
        print(data_model)
        save_to_database = db.session
        try:
            data_model.IsOpen = False
            save_to_database.add(data_model)
            save_to_database.commit()
            flash('Election Ended Successfully!', "success")
            return redirect(url_for('home'))
        except Exception as e:
            save_to_database.rollback()
            save_to_database.flush()
            print(e)
            flash("Can't End Election Now!, please try again Later..","info")
    return render_template("EndElection.html",ElectionList=Elections.query.filter_by(IsOpen=True).all())
######################################### END ###########################################################

@app.route('/')
def home():
    return render_template("home.html", ElectionList=Elections.query.all(), ActiveElection=Elections.query.filter_by(IsOpen=True).all())


@app.route('/ElectionList')
@is_logged_in
def ElectionList():
    return render_template("ElectionList.html", ElectionList=Elections.query.all(), ActiveElection=Elections.query.filter_by(IsOpen=True).all())

@app.route('/castvote/<string:ElectionName>')
@is_logged_in
def CastVote(ElectionName):
    if(VotingList.query.filter_by(ElectionName=ElectionName, VoterId=session['uid']).count() == 0):
        return render_template("CastVote.html", ElectionName=ElectionName)
    else:
        flash("Vote Already submitted for"+str(ElectionName),"info")
        return redirect(url_for("ElectionList"))

@app.route('/submit_vote/<ElectionName>',methods=['GET','POST'])
@is_logged_in
def submit_vote(ElectionName):
    party=request.form.get("party_name")
    prevMac = party+session['uid']
    newMac = hashfunction(str(party+session['uid']),prevMac)
    last_model = VotingList.query.filter_by(ElectionName=ElectionName)[-1] # getting latest record
    new_model = VotingList(ElectionName=ElectionName, PartyName=party,MacCount=(last_model.MacCount+1),
                        VoterId=session["uid"], PrevMac=last_model.NewMac, NewMac=newMac)
    save_to_database=db.session
    try:
        save_to_database.add(new_model)
        save_to_database.commit()
        flash('Vote Submitted Successfully!', "success")
        return redirect(url_for('home'))
    except Exception as e:
        save_to_database.rollback()
        save_to_database.flush()
        print(e)
        flash("Can't End Election Now!, please try again Later..","info")
    
    return redirect(url_for("ElectionList"))

@app.route('/results')
@app.route('/results/<Election>')
@is_logged_in
def results(Election='Choose'):
    if(Election == 'Choose'):
        return render_template("results.html", VoteList=Elections.query.all(), Election=Elections.query.first())
    else:
        objects = VotingList.query.filter_by(ElectionName=Election).all()
        party = {}
        for object in objects:
            if object.PartyName in party.items():
                party[object.PartyName] += 1
            else:
                party[object.PartyName] = 1
        party.pop("None")
        print(party)
        return render_template("results.html", VoteList=Elections.query.all(), Election=Elections.query.filter_by(ElectionName=Election).first(), Listing=party)

if __name__ == '__main__':
    db.create_all()
    app.run()
    # app.run(debug=True)
