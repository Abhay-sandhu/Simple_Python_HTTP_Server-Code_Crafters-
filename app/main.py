# Uncomment this to pass the first stage
import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, addr = server_socket.accept() # wait for client
    data = conn.recv(1024)
    print('recieved_data:', data.decode('utf-8'))
    request = data.decode('utf-8').splitlines()[0]
    if request == 'GET / HTTP/1.1':
        response = (
            "HTTP/1.1 200 OK\r\n\r\n"
        )
    else:
        response = (
            "HTTP/1.1 404 Not Found\r\n\r\n"
        )
    conn.sendall(response.encode('utf-8'))
    conn.close()
if __name__ == "__main__":
    main()
