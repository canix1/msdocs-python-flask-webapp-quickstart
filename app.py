import os
from flask import (Flask, render_template, request, jsonify, url_for)
import pandas as pd

app = Flask(__name__)

# Läs in CSV-filen med specifika parametrar
df = pd.read_csv('permissions.csv',
                 quotechar='"',            
                 encoding='utf-8',         
                 na_values=[''],           
                 dtype=str,                
                 skipinitialspace=True)    

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
    filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(query, case=False, na=False)).any(axis=1)]
    result = filtered_df.to_dict('records')
    print("Columns in data:", list(filtered_df.columns))  # Debug-utskrift
    return jsonify(result)
    

if __name__ == '__main__':
   app.run(debug=True)  # Sätt debug=True här