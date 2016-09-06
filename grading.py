#!/bin/env python3

from flask import Flask, redirect, render_template, request, Response
from unitchecker import UnitChecker
from pprint import pformat

app = Flask(__name__)
app.debug = True

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/test', methods=['POST'])
def test():
  org = request.form['org']
  repo = request.form['repo']
  password = request.form['password']
  if password != None and org != None and repo != None and org != '' and repo != '' and request.form['password'] == 'helloworld!':
    uc = UnitChecker()
    prs = uc.process_git(org, repo)
    def generator():
      for pr in prs:
        result = uc.process_pullrequest(pr, repo)
        yield result
    #return render_template('results.html', results=results, org=org, repo=repo)
    return Response(stream_template('results.html', results=generator(), org=org, repo=repo))
  else:
    return redirect('http://www.nyan.cat/', code=302)

if __name__ == "__main__":
  app.run(debug=True)
