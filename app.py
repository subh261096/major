from flask import Flask,render_template,request
from HashingFunction import hashfunction

app = Flask(__name__)


@app.route('/')
@app.route('/voting')
def hello_world():
    return render_template("VotingList.html")

@app.route("/login")


@app.route('/submit_vote',methods=['POST'])
def submit_vote():
    voter_id=request.form.get("voter_id")
    party=request.form.get("party_name")
    mac1=hashfunction(str(party+voter_id))
    print("\n\nGenerated MAC is: "+str(mac1).upper()+'\n\n')
    return render_template("vote_submitted.html")
    

if __name__ == '__main__':
    app.run(debug=True)