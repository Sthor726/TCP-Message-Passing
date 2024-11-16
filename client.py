import socket
import threading

server_name = 'localhost'
server_port = 12000

client_socket = None
running = True
disconnect_ack_received = False
subscription_ack_received = False

def receive_messages():
    global running, disconnect_ack_received
    while running:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"\nServer: {message}")
                if message == "DISC_ACK":
                    disconnect_ack_received = True
                    break
                elif message == "SUB_ACK":
                    global subscription_ack_received
                    subscription_ack_received = True
            else:
                break
        except socket.timeout:
            continue
        except Exception as e:
            print("Error receiving message from server:", e)
            break

client_name = input("Enter your name: ")

try:
    while running:
        print("\nCommands:")
        print("1 - CONNECT")
        print("2 - SUBSCRIBE to a topic")
        print("3 - PUBLISH a message to a topic")
        print("4 - DISCONNECT")
        
        command = input("Choose a command (1-4): ")

        if command == "1":  # CONNECT
            if client_socket is None:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((server_name, server_port))
                client_socket.settimeout(5)
                receive_thread = threading.Thread(target=receive_messages, daemon=True)
                receive_thread.start()
                message = f"{client_name}, CONN"
                client_socket.send(message.encode('utf-8'))
                print("Connected to the server.")
            else:
                print("Already connected to the server.")

        elif command == "2":  # SUBSCRIBE
            if client_socket:
                subject = input("Enter the subject to subscribe to (WEATHER/NEWS): ").upper()
                message = f"{client_name}, SUB, {subject}"
                subscription_ack_received = False

                retry_count = 0
                max_retries = 3

                while not subscription_ack_received and retry_count < max_retries:
                    client_socket.send(message.encode('utf-8'))
                    try:
                        client_socket.settimeout(5)
                        data = client_socket.recv(1024).decode('utf-8')
                        if data == "SUB_ACK":
                            subscription_ack_received = True
                            print(f"Subscribed to {subject} successfully.")
                    except socket.timeout:
                        retry_count += 1
                        print(f"No acknowledgment received. Retrying subscription ({retry_count}/{max_retries})...")
                
                if not subscription_ack_received:
                    print(f"Failed to subscribe to {subject} after {max_retries} attempts.")
            else:
                print("You must connect to the server first.")

        elif command == "3":  # PUBLISH
            if client_socket:
                subject = input("Enter the subject to publish to (WEATHER/NEWS): ").upper()
                msg = input("Enter the message to publish: ")
                message = f"{client_name}, PUB, {subject}, {msg}"
                client_socket.send(message.encode('utf-8'))
            else:
                print("You must connect to the server first.")

        elif command == "4":  # DISCONNECT
            if client_socket:
                message = f"{client_name}, DISC"
                disconnect_ack_received = False
                client_socket.send(message.encode('utf-8'))

                retry_count = 0
                max_retries = 3

                while not disconnect_ack_received and retry_count < max_retries:
                    try:
                        client_socket.settimeout(5)
                        data = client_socket.recv(1024).decode('utf-8')
                        if data == "DISC_ACK":
                            disconnect_ack_received = True
                            print("Server acknowledged disconnect.")
                    except socket.timeout:
                        retry_count += 1
                        print("No acknowledgment received. Retrying disconnect...")
                        client_socket.send(message.encode('utf-8'))

                client_socket.close()
                client_socket = None
                print("Disconnected from server.")
            else:
                print("You are not connected to the server.")

        else:
            print("Invalid command. Please choose a number between 1 and 4.")

except KeyboardInterrupt:
    print("\nClient disconnected.")

if client_socket:
    client_socket.close()
print("Client program ended.")
