import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

import pandas as pd

app = Flask(__name__)


@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    # Sök i alla kolumner
    filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(query, case=False)).any(axis=1)]
    return jsonify(filtered_df.to_dict('records'))


if __name__ == '__main__':
   app.run()
