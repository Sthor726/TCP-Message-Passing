import socket
import threading

subjects = ["WEATHER", "NEWS"]

clients = {}
client_subscriptions = {}
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
                clients[client_name] = connection
                if client_name not in client_subscriptions:
                    client_subscriptions[client_name] = {"subjects": set(), "queue": {subject: [] for subject in subjects}}
                connection.send("CONN_ACK".encode('utf-8'))
                print(f"CONN_ACK for {client_name}")

            elif action == "SUB":
                subject = parts[2]
                if subject in subjects:
                    # Add the subscription to the client's list
                    client_subscriptions[client_name]["subjects"].add(subject)
                    connection.send("SUB_ACK".encode('utf-8'))  # Acknowledge subscription first
                    print(f"{client_name} subscribed to {subject}")

                    # Deliver past messages for the subject
                    if subject in message_history:
                        for past_msg in message_history[subject]:
                            connection.send(f"\nPast Message for {subject}: {past_msg}".encode('utf-8'))

                    # Deliver queued messages for the subject
                    for msg in client_subscriptions[client_name]["queue"][subject]:
                        connection.send(f"\nWhile Offline: [{subject}], Message: {msg}".encode('utf-8'))

                    client_subscriptions[client_name]["queue"][subject] = []  # Clear queue after delivery
                else:
                    connection.send("ERROR: Subscription Failed - Subject Not Found".encode('utf-8'))

            elif action == "PUB":
                subject = parts[2]
                msg = parts[3] if len(parts) > 3 else ""
                if subject in subjects:
                    message_history[subject].append(msg) 
                    for subscriber_name, details in client_subscriptions.items():
                        if subject in details["subjects"]:
                            if subscriber_name in clients: 
                                clients[subscriber_name].send(f"[{subject}] {msg}".encode('utf-8'))
                            else: 
                                details["queue"][subject].append(msg)
                    connection.send("\nMessage published.".encode('utf-8'))
                else:
                    connection.send("ERROR: Subject Not Found".encode('utf-8'))

            elif action == "RECONNECT":
                if client_name in client_subscriptions:
                    clients[client_name] = connection
                    connection.send("RECONNECT_ACK".encode('utf-8'))
                    print(f"RECONNECT_ACK for {client_name}")
                    for subject in client_subscriptions[client_name]["subjects"]:
                        for msg in client_subscriptions[client_name]["queue"][subject]:
                            connection.send(f"\nQueued Topic: [{subject}], Message: {msg}".encode('utf-8'))
                        client_subscriptions[client_name]["queue"][subject] = []
                    print(f"{client_name} reconnected and received queued messages.")
                else:
                    connection.send("ERROR: RECONNECT Failed - Client Not Found".encode('utf-8'))

            elif action == "DISC":
                print(f"DISC_ACK for {client_name}")
                connection.send("DISC_ACK".encode('utf-8'))
                break

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            break

    if client_name:
        clients.pop(client_name, None)
        print(f"Client {client_name} disconnected.")
    connection.close()



server_port = 12000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', server_port))
server_socket.listen()
print(f"Server listening on port {server_port}")

while True:
    connection, addr = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(connection, addr))
    client_thread.start()
