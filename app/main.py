# Uncomment this to pass the first stage
import socket
import re

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server is listening on port 4221...")

    conn, addr = server_socket.accept() # wait for client
    print(f"Accepted connection from {addr}")

    data = conn.recv(1024)
    print('Received data:', data.decode('utf-8'))

    request = data.decode('utf-8').splitlines()[0]
    print('Request line:', request)

    pattern = re.compile(r"GET /echo/(\S+) HTTP/1\.1")
    match = pattern.search(request)

    if request == 'GET / HTTP/1.1':
        response = "HTTP/1.1 200 OK\r\n\r\n"
   
    elif match:
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(match.group(1))}\r\n\r\n{match.group(1)}"

    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
    
    conn.sendall(response.encode('utf-8'))
    print('response sent')

    conn.close()
    print(f"Connection with {addr} closed")

if __name__ == "__main__":
    main()
