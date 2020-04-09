from wtforms import Form, TextField, PasswordField, validators
from flask import Flask, render_template, request, flash, url_for, redirect, session, jsonify
from HashingFunction import hashfunction
from flask_sqlalchemy import SQLAlchemy
from functools import wraps, partial
from sqlalchemy import DateTime
import datetime
import pymysql

app = Flask(__name__)

######################################### CONFIGRATION OF DATABSE ######################################
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:subh261096@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'subh261096'
db = SQLAlchemy(app)

#########################################     END     #############################################

######################################### DATABSE TABLES ################################################


                    ########################## USER TABLE ######################
class Users(db.Model):
    __tablename__ = 'UserData'
    VoterId = db.Column(db.String(30), primary_key=True)
    Name = db.Column(db.String(30))
    Password = db.Column(db.String(500))
    RegisterDate = db.Column(DateTime, default=datetime.datetime.utcnow)
                    ########################### END #########################


                    ######################### USER LIST ###################
class ElectionsList(db.Model):
    __tablename__ = 'Elections'
    ElectionName = db.Column(db.Integer, primary_key=True)
    ListName=db.Column(db.String(50),primary_key=True)
    OpenedAt = db.Column(DateTime, default=datetime.datetime.utcnow)
    closedAt = db.Column(DateTime,nullable=True)
                    ############################### END ##########################

class Election(db.Model):
    __tablename__ = 'UserMovie'
    List = db.Column(db.String(50),primary_key=True)
    MovieId=db.Column(db.String(30),primary_key=True)
    MovieName = db.Column(db.String(30))
    PosterUrl = db.Column(db.String(80))
    LastModifiedDate = db.Column(DateTime, default=datetime.datetime.utcnow)    

############################################## END ######################################################







######################################### REGISTRATION FORM #########################################
class RegistrationForm(Form):
    '''Child of a WTForm Form object...'''
    username = TextField('Username', [validators.Length(min=3, max=20)])
    password = PasswordField('Password', [validators.DataRequired(),
                                            validators.EqualTo('confirm',
                                                            message="Passwords must match")])
    confirm = PasswordField('Confirm Password')
######################################### END #############################################





######################################### VERIFY LOGIN #############################################
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('UnAuthorised!, Please Login First!', 'danger')
            return redirect(url_for('home'))
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
    session.pop('_flashes', None)
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():  # if the form info is valid
        username = form.username.data
        password = sha256_crypt.hash(str(form.password.data))
        data_model = UserData(Name=username, Password=password)
        save_to_database = db.session
        if(UserData.query.filter_by(Name=username).count() == 0):
            try:
                save_to_database.add(data_model)
                save_to_database.commit()
                uid = UserData.query.filter_by(Name=username).first().Id
                flash('Registered Successfully!','success')
                return redirect(url_for('login'))
            except:
                save_to_database.rollback()
                save_to_database.flush()
                flash("can't Register Now!, please try again Later..")
            return render_template('Signup.html', form=form)
        else:
            flash("User Already Exists! Please Enter Unique username!")
            return render_template('Signup.html', form=form)
    if request.method == "POST" and form.validate() == False:  # if form info is invalid
        flash('Invalid password, please try again')
        return render_template('Signup.html', form=form)
    return render_template("Signup.html")
######################################### END #########################################################







######################################### LOG IN ######################################################
@app.route('/login', methods=['GET', 'POST'])
# @already_logged_in
def login():
    if request.method == "POST":
        attempted_username = request.form['username']
        attempted_password = request.form['password']

        if (UserData.query.filter_by(Name=attempted_username).count()) == 0:
            flash("Username not found. Try a different username, or create an account.")
            return render_template("Login.html")
        data_model = UserData.query.filter_by(Name=attempted_username).first()
        try:
            if attempted_username == data_model.Name and sha256_crypt.verify(attempted_password, data_model.Password):
                session.permanent = True
                # setting session timeout
                app.permanent_session_lifetime = timedelta(minutes=5)
                session['logged_in'] = True
                session['uid'] = data_model.Id
                session['username'] = data_model.Name
                flash("Welcome %s!" % (data_model.Name),'')
                return redirect(url_for("home"))
            else:
                flash("Incorrect password, try again")
                return render_template("Login.html")
        except Exception as e:
            return str(e)
    return render_template("Login.html")

######################################### END #########################################################




@app.route('/')
def home():
    return render_template("home.html")


@app.route('/voting')
@is_logged_in
def hello_world():
    return render_template("VotingList.html")

@app.route('/results')
@is_logged_in
def results():
    return render_template("result.html")

@is_logged_in
@app.route('/submit_vote',methods=['POST'])

def submit_vote():
    voter_id=request.form.get("voter_id")
    party=request.form.get("party_name")
    mac1=hashfunction(str(party+voter_id))
    print("\n\nGenerated MAC is: "+str(mac1).upper()+'\n\n')
    return render_template("vote_submitted.html")
    

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)