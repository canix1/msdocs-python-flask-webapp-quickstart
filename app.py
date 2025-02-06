# app.py
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from azure.data.tables import TableServiceClient
from azure.core.credentials import AzureNamedKeyCredential

app = Flask(__name__)

# Azure Storage configuration
STORAGE_ACCOUNT_NAME = os.environ.get('STORAGE_ACCOUNT_NAME')
STORAGE_ACCOUNT_KEY = os.environ.get('STORAGE_ACCOUNT_KEY')
TABLE_NAME_1 = os.environ.get('TABLE_NAME')
TABLE_NAME_2 = os.environ.get('TABLE_NAME_2')

# Create the credential object
credential = AzureNamedKeyCredential(STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY)

# Create the table service client
table_service = TableServiceClient(
    endpoint=f"https://{STORAGE_ACCOUNT_NAME}.table.core.windows.net",
    credential=credential
)

def get_table_data(table_name):
    try:
        table_client = table_service.get_table_client(table_name=table_name)
        entities = list(table_client.list_entities())
        
        data = []
        for entity in entities:
            item = {
                'Identity_ObjectID': entity.get('Identity_ObjectID', ''),
                'userPrincipalName': entity.get('userPrincipalName', ''),
                'Module': entity.get('Module', ''),
                'Target_Type': entity.get('Target_Type', ''),
                'Resource_FriendlyName': entity.get('Resource_FriendlyName', ''),
                'Target_Resource': entity.get('Target_Resource', ''),
                'Permission_Name': entity.get('Permission_Name', ''),
                'Backup_DateTime': entity.get('Backup_DateTime', '')
            }
            data.append(item)
        
        return data
    except Exception as e:
        print(f"Error retrieving data from Azure Table {table_name}: {str(e)}")
        return []

@app.route('/')
def index():
    return render_template('index.html', 
                         TABLE_NAME_1=TABLE_NAME_1, 
                         TABLE_NAME_2=TABLE_NAME_2)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    table_name = request.args.get('table')
    
    if not table_name:
        return jsonify({"error": "Table name is required"}), 400
        
    try:
        data = get_table_data(table_name)
        
        if query:
            filtered_data = [
                item for item in data
                if any(str(value).lower().find(query) != -1 
                      for value in item.values())
            ]
        else:
            filtered_data = data
            
        return jsonify(filtered_data)
        
    except Exception as e:
        print(f"Error in search: {str(e)}")
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)