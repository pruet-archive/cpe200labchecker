#!/bin/env python3

from flask import Flask
from flask import render_template
from flask import request
from unitchecker import UnitChecker
from pprint import pformat
from flask import Response

app = Flask(__name__)
app.debug = True

#def stream_template(template_name, **context):

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/test', methods=['POST'])
def test():
  if request.form['password'] == 'helloworld!':
    uc = UnitChecker()
    org = request.form['org']
    repo = request.form['repo']
    results = uc.process_git(org, repo)
    return render_template('results.html', results=results, org=org, repo=repo)
  else:
    return 'you shouldn\'t be here'

#if __name__ == "__main__":
#  app.run(debug=True)
