import socket
import random

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(('localhost', 3003))
server_socket.listen()

print("Server is running on localhost:3003")

while True:
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")
    request = client_socket.recv(1024).decode()

    if (not request) or ('favicon.ico' in request):
        client_socket.close()
        continue

    request_line = request.splitlines()[0]

    http_method, path_query, http_version = request_line.split()

    path, parameters = path_query.split('?')

    parameters = {pair.split("=")[0]: pair.split("=")[1]
                  for pair in parameters.split('&')}

    rolls = ''

    for _ in range(int(parameters['rolls'])):
        roll = random.randint(1, int(parameters['sides']))
        rolls += f"<li>Rolls: {roll}</li>"


    response_body = ("<html><head><title>Dice Roll</title></head><body>"
                     "<h1>HTTP Request Information</h1>"
                     f"<p>Request Line: {request_line}</p>"
                     f"<p>HTTP Method: {http_method}</p>"
                     f"<p>Path: {path}</p>"
                     f"<p>Parameters: {parameters}</p>"
                     f"<ul>{rolls}</ul></html>")

    response = ("HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "\r\n"
                f"{response_body}\n")

    client_socket.sendall(response.encode())
    client_socket.close()