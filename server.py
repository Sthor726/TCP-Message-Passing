import socket
import threading

subjects = ["WEATHER", "NEWS"]

subscriptions = {subject: set() for subject in subjects}
clients = {}
message_history = {subject: [] for subject in subjects}


def handle_client(connection, addr):
    client_name = None
    print(f"Client connected from {addr}")

    while True:
        try:
            message = connection.recv(1024).decode('utf-8')
            if not message:
                break

            parts = message.split(", ")
            client_name = parts[0]
            action = parts[1]

            if action == "CONN":
                #format: <client_name>, CONN
                clients[client_name] = connection 
                connection.send("CONN_ACK".encode('utf-8'))
                print("CONN_ACK")

            elif action == "SUB":
                #format: <client_name>, SUB, <subject>
                subject = parts[2]
                if subject in subjects:
                    subscriptions[subject].add(connection)
                    connection.send("SUB_ACK".encode('utf-8'))
                    print("SUB_ACK")
                    for msg in message_history[subject]:
                        connection.send(f"\nTopic: [{subject}], Message: {msg}".encode('utf-8'))
                else:
                    connection.send("ERROR: Subscription Failed - Subject Not Found".encode('utf-8'))

            elif action == "PUB":
                #format: <client_name>, PUB, <subject>, <message>
                subject = parts[2]
                msg = parts[3] if len(parts) > 3 else ""
                if subject in subjects:
                    message_history[subject].append(msg)

                    for subscriber in subscriptions[subject]:
                        subscriber.send(f"[{subject}] {msg}".encode('utf-8'))
                    connection.send("Message published.".encode('utf-8'))
                else:
                    connection.send("ERROR: Subject Not Found".encode('utf-8'))

            elif action == "DISC":
                #format: <client_name>, DISC
                connection.send("DISC_ACK".encode('utf-8'))
                break

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            break

    if client_name:
        for subscribers in subscriptions.values():
            subscribers.discard(connection)
        del clients[client_name]
    connection.close()
    print(f"Client {addr} ({client_name}) disconnected.")

server_port = 12001
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', server_port))
server_socket.listen()
print(f"Server listening on port {server_port}")

while True:
    connection, addr = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(connection, addr))
    client_thread.start()
