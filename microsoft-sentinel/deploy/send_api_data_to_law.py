import urllib.request
import urllib.error
import json
import base64
import hmac
import hashlib
import datetime
import argparse
import sys
import os
import configparser
import re

def read_graphql_file(file_path):
    """
    Read a GraphQL query from a file
    
    Parameters:
    file_path (str): Path to the GraphQL query file
    
    Returns:
    str: The GraphQL query
    """
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: GraphQL file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading GraphQL file: {str(e)}")
        sys.exit(1)

def extract_variables_from_query(query):
    """
    Extract required variables from a GraphQL query
    
    Parameters:
    query (str): GraphQL query string
    
    Returns:
    list: List of variable names
    """
    # Look for variable definitions in the query
    # This regex matches variables defined in the query like ($varName: Type!)
    matches = re.findall(r'\$(\w+)(?:\s*:\s*[^,)]+)', query)
    return matches

def load_config(config_file):
    """
    Load configuration from a file
    
    Parameters:
    config_file (str): Path to the config file
    
    Returns:
    dict: Configuration as a dictionary
    """
    try:
        if config_file.endswith('.json'):
            with open(config_file, 'r') as file:
                return json.load(file)
        else:
            config = configparser.ConfigParser()
            config.read(config_file)
            
            # Convert ConfigParser object to dict
            result = {}
            for section in config.sections():
                result[section] = {}
                for key, value in config[section].items():
                    # Try to parse JSON values (for nested structures)
                    try:
                        result[section][key] = json.loads(value)
                    except json.JSONDecodeError:
                        result[section][key] = value
            
            return result
    except FileNotFoundError:
        print(f"Error: Config file not found: {config_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading config file: {str(e)}")
        sys.exit(1)

def invoke_graphql_api(api_url, query, variables=None, headers=None):
    """
    Function specifically for GraphQL API calls
    
    Parameters:
    api_url (str): GraphQL endpoint URL
    query (str): GraphQL query or mutation
    variables (dict, optional): Variables for the GraphQL query
    headers (dict, optional): HTTP headers to include in the request
    
    Returns:
    dict: The GraphQL API response
    """
    if headers is None:
        headers = {}
    
    # Prepare GraphQL payload
    payload = {
        "query": query
    }
    
    if variables:
        payload["variables"] = variables
    
    # Convert payload to JSON string and encode
    body = json.dumps(payload).encode('utf-8')
    
    # GraphQL always uses POST method with application/json content type
    headers["Content-Type"] = "application/json"
    
    try:
        request = urllib.request.Request(
            url=api_url,
            data=body,
            headers=headers,
            method="POST"  # GraphQL always uses POST
        )
        
        with urllib.request.urlopen(request) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data) if response_data else None
            
            # Check for GraphQL-specific errors
            if result and 'errors' in result:
                print(f"GraphQL errors: {json.dumps(result['errors'], indent=2)}")
            
            return result
            
    except urllib.error.HTTPError as e:
        print(f"API call failed: HTTP Error {e.code} - {e.reason}")
        # Try to read error response
        try:
            error_data = e.read().decode('utf-8')
            print(f"Error response: {error_data}")
        except:
            pass
        return None
    except urllib.error.URLError as e:
        print(f"API call failed: URL Error - {e.reason}")
        return None
    except Exception as e:
        print(f"API call failed: {str(e)}")
        return None

def invoke_general_api(api_url, http_method, headers=None, body=None):
    """
    General function to call REST APIs using urllib
    
    Parameters:
    api_url (str): The URL of the API
    http_method (str): HTTP method (GET, POST, etc.)
    headers (dict, optional): HTTP headers to include in the request
    body (str, optional): Request body for POST/PUT requests
    
    Returns:
    dict: The API response
    """
    if headers is None:
        headers = {}
    
    if body and isinstance(body, str):
        body = body.encode('utf-8')
    
    # Add content type if body is provided
    if body:
        headers["Content-Type"] = "application/json"
    
    try:
        request = urllib.request.Request(
            url=api_url,
            data=body,
            headers=headers,
            method=http_method
        )
        
        with urllib.request.urlopen(request) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data) if response_data else None
            
    except urllib.error.HTTPError as e:
        print(f"API call failed: HTTP Error {e.code} - {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"API call failed: URL Error - {e.reason}")
        return None
    except Exception as e:
        print(f"API call failed: {str(e)}")
        return None

def send_to_log_analytics(workspace_id, shared_key, log_type, json_payload):
    """
    Send data to Azure Log Analytics workspace using urllib
    
    Parameters:
    workspace_id (str): Log Analytics workspace ID
    shared_key (str): Shared key for authentication
    log_type (str): Custom log type name
    json_payload (dict): Data to send to Log Analytics
    """
    json_data = json.dumps(json_payload).encode('utf-8')
    
    api_version = '2016-04-01'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(json_data)
    
    string_to_sign = f"POST\n{content_length}\n{content_type}\nx-ms-date:{rfc1123date}\n{resource}"
    bytes_to_sign = string_to_sign.encode('utf-8')
    
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = hmac.new(decoded_key, bytes_to_sign, digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(encoded_hash).decode('utf-8')
    
    authorization = f"SharedKey {workspace_id}:{signature}"
    
    headers = {
        'Content-Type': content_type,
        'Authorization': authorization,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    
    uri = f"https://{workspace_id}.ods.opinsights.azure.com{resource}?api-version={api_version}"
    
    try:
        request = urllib.request.Request(url=uri, data=json_data, headers=headers, method="POST")
        with urllib.request.urlopen(request) as response:
            print("Data successfully sent to Log Analytics workspace.")
    except urllib.error.HTTPError as e:
        print(f"Failed to send data to Log Analytics: HTTP Error {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        print(f"Failed to send data to Log Analytics: URL Error - {e.reason}")
    except Exception as e:
        print(f"Failed to send data to Log Analytics: {str(e)}")

def parse_arguments():
    parser = argparse.ArgumentParser(description='Make API calls and send data to Log Analytics')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Standard REST API parser
    rest_parser = subparsers.add_parser('rest', help='Make a REST API call')
    rest_parser.add_argument('--api-url', required=True, help='API URL to call')
    rest_parser.add_argument('--http-method', default='GET', help='HTTP method (GET, POST, etc.)')
    rest_parser.add_argument('--headers', help='JSON string of headers')
    rest_parser.add_argument('--body', help='JSON string for request body')
    
    # GraphQL API parser
    graphql_parser = subparsers.add_parser('graphql', help='Make a GraphQL API call')
    graphql_parser.add_argument('--api-url', help='GraphQL endpoint URL')
    graphql_parser.add_argument('--query', help='GraphQL query string')
    graphql_parser.add_argument('--query-file', help='Path to a file containing the GraphQL query')
    graphql_parser.add_argument('--variables', help='JSON string of GraphQL variables')
    graphql_parser.add_argument('--headers', help='JSON string of headers')
    graphql_parser.add_argument('--config', help='Path to a config file (JSON or INI)')
    graphql_parser.add_argument('--config-section', default='graphql', help='Section in config file to use')
    
    # Common arguments for Log Analytics
    parser.add_argument('--workspace-id', help='Log Analytics workspace ID')
    parser.add_argument('--shared-key', help='Log Analytics shared key')
    parser.add_argument('--log-type', default='CustomLogType', help='Log Analytics custom log type')
    parser.add_argument('--config', help='Path to a config file (JSON or INI)')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Load general config if provided
    config = {}
    if hasattr(args, 'config') and args.config:
        config = load_config(args.config)
    
    # Process based on command
    if args.command == 'rest':
        # Parse headers if provided
        headers = {}
        if args.headers:
            try:
                headers = json.loads(args.headers)
            except json.JSONDecodeError:
                print("Error: Headers must be valid JSON")
                sys.exit(1)
        
        response = invoke_general_api(
            api_url=args.api_url, 
            http_method=args.http_method, 
            headers=headers, 
            body=args.body
        )
        
    elif args.command == 'graphql':
        # Get API URL from args or config
        api_url = args.api_url
        if not api_url and 'graphql' in config and 'api_url' in config['graphql']:
            api_url = config['graphql']['api_url']
        if not api_url:
            print("Error: GraphQL API URL is required")
            sys.exit(1)
        
        # Load GraphQL query
        query = None
        if args.query:
            query = args.query
        elif args.query_file:
            query = read_graphql_file(args.query_file)
        elif 'graphql' in config and 'query_file' in config['graphql']:
            query = read_graphql_file(config['graphql']['query_file'])
        if not query:
            print("Error: GraphQL query is required")
            sys.exit(1)
        
        # Get headers from args or config
        headers = {}
        if args.headers:
            try:
                headers = json.loads(args.headers)
            except json.JSONDecodeError:
                print("Error: Headers must be valid JSON")
                sys.exit(1)
        elif 'graphql' in config and 'headers' in config['graphql']:
            headers = config['graphql']['headers']
        
        # Get variables from args, config, or extract from query
        variables = {}
        if args.variables:
            try:
                variables = json.loads(args.variables)
            except json.JSONDecodeError:
                print("Error: Variables must be valid JSON")
                sys.exit(1)
        elif 'graphql' in config and 'variables' in config['graphql']:
            variables = config['graphql']['variables']
        else:
            # Try to extract required variables from query and get them from config
            required_vars = extract_variables_from_query(query)
            if required_vars and 'variables' in config:
                for var in required_vars:
                    if var in config['variables']:
                        variables[var] = config['variables'][var]
                    else:
                        print(f"Warning: Required variable '{var}' not found in config")
        
        # Make the GraphQL API call
        response = invoke_graphql_api(
            api_url=api_url,
            query=query,
            variables=variables,
            headers=headers
        )
    else:
        print("Error: Command is required. Use 'rest' or 'graphql'")
        sys.exit(1)
    
    # Process Log Analytics if needed
    if response:
        # Get Log Analytics details from args or config
        workspace_id = args.workspace_id
        shared_key = args.shared_key
        log_type = args.log_type
        
        if not workspace_id and 'log_analytics' in config and 'workspace_id' in config['log_analytics']:
            workspace_id = config['log_analytics']['workspace_id']
        
        if not shared_key and 'log_analytics' in config and 'shared_key' in config['log_analytics']:
            shared_key = config['log_analytics']['shared_key']
        
        if args.log_type == 'CustomLogType' and 'log_analytics' in config and 'log_type' in config['log_analytics']:
            log_type = config['log_analytics']['log_type']
        
        if workspace_id and shared_key:
            send_to_log_analytics(
                workspace_id=workspace_id,
                shared_key=shared_key,
                log_type=log_type,
                json_payload=response
            )
        else:
            print("API response received but not sending to Log Analytics (missing workspace credentials)")
            print(json.dumps(response, indent=2))