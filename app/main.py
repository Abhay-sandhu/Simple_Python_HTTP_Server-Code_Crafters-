# Uncomment this to pass the first stage
import socket
import re
import threading


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server is listening on port 4221...")

    # Loop for receiving connections
    while True:

        # wait for client
        conn, addr = server_socket.accept() 
        
        # create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        
        # start the thread
        client_thread.start()

    


def handle_client(conn, addr):
   
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
    if match_user_agent:
        user_agent_pattern = re.compile(r"User-Agent: (\S+)")
        match_u_agent = user_agent_pattern.search(data.decode('utf-8'))

    # response
    if request == 'GET / HTTP/1.1': # root response
        response = "HTTP/1.1 200 OK\r\n\r\n"
    
    elif match_echo: # echo response
        response = (f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: text/plain\r\n"
                    f"Content-Length: {len(match_echo.group(1))}\r\n"
                    f"\r\n"
                    f"{match_echo.group(1)}"
                    )
    
    elif match_user_agent: # user agent response
        response = (f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: text/plain\r\n"
                    f"Content-Length: {len(match_u_agent.group(1))}\r\n"
                    f"\r\n"
                    f"{match_u_agent.group(1)}"
                    )

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
