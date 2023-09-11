import json
from flask import Flask, request
from flask_cors import CORS, cross_origin
from stage2project import getEmails
app = Flask(__name__)

cors = CORS(app)


@app.route('/')
def index():
    return 'Hello world'

@app.route('/get-emails', methods=['POST'])
@cross_origin()
def get_emails():

    print(request.data)
    credentials = json.loads(request.data)
    return getEmails(credentials)
app.run()