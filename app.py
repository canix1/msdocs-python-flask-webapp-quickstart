import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from azure.data.tables import TableServiceClient
from azure.core.credentials import AzureNamedKeyCredential

app = Flask(__name__)

# Azure Storage configuration
STORAGE_ACCOUNT_NAME = os.environ.get('STORAGE_ACCOUNT_NAME')
STORAGE_ACCOUNT_KEY = os.environ.get('STORAGE_ACCOUNT_KEY')
TABLE_NAME = os.environ.get('TABLE_NAME')
TABLE_NAME_2 = os.environ.get('TABLE_NAME_2')
TABLE_NAME_3 = os.environ.get('TABLE_NAME_3')
TABLE_NAME_4 = os.environ.get('TABLE_NAME_4')

# Create the credential object
credential = AzureNamedKeyCredential(STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY)

# Create the table service client
table_service = TableServiceClient(
    endpoint=f"https://{STORAGE_ACCOUNT_NAME}.table.core.windows.net",
    credential=credential
)

def query_table_data(table_name, search_query=None, filters=None):
    try:
        print(f"Querying table {table_name} with search: {search_query}")
        table_client = table_service.get_table_client(table_name=table_name)
        
        filter_conditions = []
        
        if search_query and search_query.strip():
            search_fields = [
                'Identity_ObjectID', 'userPrincipalName', 'Module', 
                'Target_Type', 'Resource_FriendlyName', 'Target_Resource', 
                'Permission_Name'
            ]
            
            field_conditions = []
            safe_query = search_query.replace("'", "''")
            
            for field in search_fields:
                if field == 'userPrincipalName':
                    # Exact match for userPrincipalName
                    field_conditions.append(f"{field} eq '{safe_query}'")
                else:
                    # Contains simulation for other fields
                    field_conditions.append(f"{field} eq '{safe_query}'")
            
            if field_conditions:
                filter_conditions.append(f"({' or '.join(field_conditions)})")
        
        if filters:
            for field, value in filters.items():
                if isinstance(value, list):
                    # Handle list of values
                    valid_values = []
                    for val in value:
                        if val and str(val).strip():
                            safe_val = str(val).replace("'", "''")
                            valid_values.append(f"{field} eq '{safe_val}'")
                    if valid_values:
                        filter_conditions.append(f"({' or '.join(valid_values)})")
                elif value and str(value).strip():
                    # Handle single value
                    safe_value = str(value).replace("'", "''")
                    filter_conditions.append(f"{field} eq '{safe_value}'")

        filter_string = ' and '.join(filter_conditions) if filter_conditions else None
        print(f"Final filter string: {filter_string}")
        
        # Query the table
        entities = list(table_client.query_entities(filter_string)) if filter_string else list(table_client.list_entities())
        
        # Convert entities to dictionaries
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
                'Backup_DateTime': entity.get('Backup_DateTime', ''),
                'Source_Table': table_name
            }
            data.append(item)
        
        print(f"Retrieved {len(data)} records from {table_name}")
        return data
        
    except Exception as e:
        print(f"Error querying Azure Table {table_name}: {str(e)}")
        return []


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/search')
def search():
    try:
        query = request.args.get('query', '')
        module_filter = request.args.getlist('modules[]')
        permission_filter = request.args.getlist('permissions[]')
        type_filter = request.args.getlist('types[]')
        
        filters = {}
        if module_filter:
            filters['Module'] = module_filter
        if permission_filter:
            filters['Permission_Name'] = permission_filter
        if type_filter:
            filters['Target_Type'] = type_filter
            
        # Define all your table names
        table_names = [
            TABLE_NAME,
            TABLE_NAME_2,
            TABLE_NAME_3,
            TABLE_NAME_4
        ]
        
        # Query all tables and combine results
        all_data = []
        for table_name in table_names:
            if table_name:  # Only query if table name exists
                table_data = query_table_data(table_name, query, filters)
                all_data.extend(table_data)
        
        print(f"Total combined records from all tables: {len(all_data)}")
        
        return jsonify(all_data)
        
    except Exception as e:
        print(f"Error in search: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)