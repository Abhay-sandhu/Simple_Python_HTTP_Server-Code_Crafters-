# Uncomment this to pass the first stage
import socket
import re
import threading
import os
import argparse

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    
    # Parse command-line arguments
    
    parser = argparse.ArgumentParser(description="Simple HTTP Server")
    parser.add_argument("--directory", type=str, default="/tmp", help="Directory to serve files from (default: /tmp)")
    args = parser.parse_args()
    directory = args.directory

    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server is listening on port 4221...")

    # Loop for receiving connections
    while True:

        # wait for client
        conn, addr = server_socket.accept() 
        
        # create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(conn, addr, directory))
        
        # start the thread
        client_thread.start()

    


def handle_client(conn, addr, directory):
   
    print(f"Accepted connection from {addr}")

    # receive data
    data = conn.recv(1024)
    print('Received data:', data.decode('utf-8'))

    # request line
    request = data.decode('utf-8').splitlines()[0]
    print('Request line:', request)

    # echo pattern and match
    echo_pattern = re.compile(r"GET /echo/(\S+) HTTP/1\.1")
    match_echo = echo_pattern.search(request)

    # user agent pattern and match
    u_agent_pattern = re.compile(r"GET /user-agent HTTP/1\.1")
    match_user_agent = u_agent_pattern.search(request)

    # files pattern and match
    files_pattern = re.compile(r"GET /files/(\S+) HTTP/1\.1")
    match_file = files_pattern.search(request)

    # POST files pattern and match
    post_files_pattern = re.compile(r"POST /files/(\S+) HTTP/1\.1")
    match_post_file = post_files_pattern.search(request)


    # Server_response
    if request == 'GET / HTTP/1.1': # root response

        response = "HTTP/1.1 200 OK\r\n\r\n"
    

    elif match_echo: # echo response

        encoding_pattern = re.compile(r"[Aa]ccept-[Ee]ncoding: (\S+)")
        match_encoding = encoding_pattern.search(data.decode('utf-8'))
        if match_encoding is not None and match_encoding.group(1) in ["gzip"]:
            response = (f"HTTP/1.1 200 OK\r\n"
                        f"Content-Encoding: {match_encoding.group(1)}\r\n"
                        f"Content-Type: text/plain\r\n"
                        f"Content-Length: {len(match_echo.group(1))}\r\n"
                        f"\r\n"
                        f"{match_echo.group(1)}"
                        )
        else:
            response = (f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: text/plain\r\n"
                    f"Content-Length: {len(match_echo.group(1))}\r\n"
                    f"\r\n"
                    f"{match_echo.group(1)}"
                    )


    elif match_user_agent: # user agent response

        user_agent_pattern = re.compile(r"[Uu]ser-[Aa]gent: (\S+)")
        match_u_agent = user_agent_pattern.search(data.decode('utf-8'))
        response = (f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: text/plain\r\n"
                    f"Content-Length: {len(match_u_agent.group(1))}\r\n"
                    f"\r\n"
                    f"{match_u_agent.group(1)}"
                    )


    elif match_file: # files response

        filename = match_file.group(1)
        file_path = os.path.join(directory,filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                file_content = file.read()
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: application/octet-stream\r\n"
                f"Content-Length: {len(file_content)}\r\n"
                f"\r\n"
                f"{file_content}"
            )
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"


    elif match_post_file: # post files response

        filename = match_post_file.group(1)
        file_path = os.path.join(directory,filename)

        file_content = data.decode('utf-8').splitlines()[-1]
        with open(file_path, 'w') as file:
            file.write(file_content)
        response = "HTTP/1.1 201 Created\r\n\r\n"

        
    else: # 'not found' response

        response = "HTTP/1.1 404 Not Found\r\n\r\n"
    
    # send response
    conn.sendall(response.encode('utf-8'))
    print('response sent')

    # close connection
    conn.close()
    print(f"Connection with {addr} closed")


if __name__ == "__main__":
    main()
