# Uncomment this to pass the first stage
import socket
import threading
import os
import argparse
import gzip
import io

def main():
    """
    Starts a simple HTTP server that serves files from the specified directory.
    
    The server listens on localhost port 4221 and creates a new thread to handle each incoming client connection. The `handle_client` function is responsible for processing the client request and sending the appropriate response.
    
    The server can be stopped by pressing Ctrl+C.
    """
        
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    
    # Parse command-line arguments
    
    parser = argparse.ArgumentParser(description="Simple HTTP Server")
    parser.add_argument("--directory", type=str, default="/tmp", help="Directory to serve files from (default: /tmp)")
    args = parser.parse_args()
    directory = args.directory

    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 4221), reuse_port=False)
    print("Server is listening on port 4221...")

    # Loop for receiving connections
    try:
        while True:

            # wait for client
            conn, addr = server_socket.accept() 
            
            # create a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(conn, addr, directory))
            
            # start the thread
            client_thread.start()

    except KeyboardInterrupt:
        print("\nServer is shutting down...")
    finally:
        server_socket.close()


def parse_request(data):
    """
    Parses an HTTP request from the given data.
    
    Args:
        data (bytes): The raw HTTP request data.
    
    Returns:
        dict: A dictionary containing the parsed request information, including:
            - method (str): The HTTP method (e.g. 'GET', 'POST').
            - path (str): The requested path.
            - version (str): The HTTP version (e.g. 'HTTP/1.1').
            - req_content_header (dict): A dictionary of the request headers, with keys and values lowercased.
            - req_content_body (str): The request body as a string.
    """
    try:
        headers, body = data.split(b'\r\n\r\n', 1)
    except ValueError:
        headers, body = data, b""

    header_lines = headers.decode('utf-8').splitlines()
    request_line = header_lines[0]
    method, path, version = request_line.split(" ")
    content_header = header_lines[1:]

    content_header_dict = {header.split(": ")[0].lower(): header.split(": ")[1] for header in content_header if ": " in header}

    return {
       'method': method,
       'path': path,
       'version': version,
       'req_content_header': content_header_dict,
       'req_content_body': body.decode('utf-8')
    }


def create_response(version, code, code_message, content_header={}, content_body=None):
    """
    Creates an HTTP response string with the given version, status code, status message, optional headers, and optional content body.
    
    Args:
        version (str): The HTTP version (e.g. 'HTTP/1.1').
        code (int): The HTTP status code (e.g. 200, 404).
        code_message (str): The HTTP status message (e.g. 'OK', 'File Not Found').
        content_header (dict, optional): A dictionary of additional HTTP headers to include in the response.
        content_body (str, optional): The content body to include in the response.
    
    Returns:
        str: The complete HTTP response string.
    """ 
    headers = f"{version} {code} {code_message}\r\n"
    
    if content_header:
        for key, value in content_header.items():
            headers += f"{key}: {value}\r\n"
    
    if content_body is not None:
        headers += f"Content-Length: {len(content_body)}\r\n"

    headers += "\r\n"
    
    if content_body is not None:
        response = headers + content_body
    else:
        response = headers
    
    return response



def handle_client(conn, addr, directory):
    """
    Handles an incoming client connection, parsing the request and generating an appropriate response.
   
    Args:
       conn (socket.socket): The socket connection to the client.
       addr (tuple): The address of the client.
       directory (str): The directory to serve files from.
   
    Returns:
        None
   """ 
    print(f"Accepted connection from {addr}")

    # receive data
    data = conn.recv(1024)
    print('Received data:', data.decode('utf-8'))

    # request parsed into dictionary
    request_dict = parse_request(data)
    
    method = request_dict['method']
    path = request_dict['path']
    version = request_dict['version']
    req_content_header = request_dict['req_content_header']
    req_content_body = request_dict['req_content_body']

    response = ""

    # GET '/' response
    if method == 'GET' and path == '/' :
        response = create_response(version, 200, 'OK')
    
    # GET '/echo/' response
    elif method == 'GET' and path.startswith('/echo/'):
        content_encoding = req_content_header.get('accept-encoding', '')
        echo_content_header = {'Content-Type': 'text/plain'}
        echo_text = path[6:]
        if 'gzip' in content_encoding:
            echo_text = gzip.compress(echo_text.encode('utf-8')).decode('utf-8')
            echo_content_header['Content-Encoding'] = 'gzip'
        response = create_response(version, 200, 'OK', content_header=echo_content_header, content_body=echo_text)

    
    # GET '/user-agent' response
    elif method == 'GET' and path.startswith('/user-agent'):
        user_agent = req_content_header.get('user-agent', 'No User-Agent header found')
        response = create_response(version, 200, 'OK', 
                                   content_header={'Content-Type': 'text/plain'}, 
                                   content_body=user_agent
                                   )
   
    # GET '/files/' response
    elif method == 'GET' and path.startswith('/files/'): 
        filename = path[7:] # >> /files/<file_name>
        file_path = os.path.join(directory,filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'rb') as file:
                file_content = file.read()
            response = create_response(version, 200, 'OK',
                                       content_header={'Content-Type': 'application/octet-stream'},
                                       content_body=file_content.decode('utf-8')
                                       )
        else:
            # requested File does not Exist
            response = create_response(version, 404, 'File Not Found')

    # POST '/files/' response
    elif method == 'POST' and path.startswith('/files/'):
        filename = path[7:] # >> /files/<file_name>
        file_path = os.path.join(directory,filename)
        file_content = req_content_body
        with open(file_path, 'w') as file:
            file.write(file_content)
        response = create_response(version, 201, 'Created')
    
    # invalid Method response
    elif method not in ['GET', 'POST']:
        response = create_response(version, 405, 'Method Not Allowed')
    
    # invalid Path response
    else:
        response = create_response(version, 404, 'Not Found')


    # send response
    conn.sendall(response.encode('utf-8'))
    print('response sent')

    # close connection
    conn.close()
    print(f"Connection with {addr} closed")


if __name__ == "__main__":
    main()
