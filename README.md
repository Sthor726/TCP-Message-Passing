# CSCI 4211 Programming Project Phase 1

## How to use:
The server can be initialized by running the following command: 'python server.py'
Clients can be created by running the following command: 'python client.py'

The following commands are available to the client in order to interact with the server:
* 1 - CONNECT
* 2 - SUBSCRIBE to a topic
* 3 - PUBLISH a message to a topic
* 4 - DISCONNECT

Responses from the server are returned through the terminal following the prompt 'Server: '

## Code design
The project is split into two parts, client.py and server.py

### Client
Upon creating a client, the user is prompted for its name in order to keep track of the user in the server. The client is mostly handled through a while loop that reads in the users input.
* When prompted to connect, the client initializes the socket and attempts to connect to the server using the appropriate name and port. If the user is already connected to the server, it notifies the user and doesn't attempt to connect again. 
* When prompted to subscribe, client.py prompts the user to enter a topic to subscribe to. The topic name, user name, and the command name (SUB) are then sent to the server in the following manner: {client_name}, SUB, {subject}.
* When prompted to publish, client.py prompts the user to enter a topic and a message. These are then sent to the server in the following format: {client_name}, PUB, {subject}, {msg}
* Finally, when prompted to disconnect, the client sends a DISC message to the server. The client stalls in a while loop to wait for the server to send an acknowledgement. Once the acknowledgement is received, the client disconnects from the server. If 5 seconds have passed and no acknowledgement was received, the client sends another disconnect message. client.py allows for 3 retries before forcing a disconnect from the server without receiving an acknowledgement.

Messages received from the server are sent through the receive_messages() function. This allows messages to be printed out through the terminal and for the client to set the acknowledgement received flag for disconnecting from the server.


### Server
server.py first initializes the server on port 12000 and begins listening for messages. An infinite loop is established to accept connections from clients. Once the connection is established, the server creates a new thread for each user (running handle_client) and continues listening for other connections. 

The handle_client function is called for each new thread and recieves messages from the clients. It parses the messages sent and has different actions depending on the command type (CONN, SUB, PUB, DISC).
* For a CONN message type, it acknowledges the connection, allowing for a proper connection of the client. 
* For a SUB message type, the server first checks if the subject listed is in the list of subjects set by the server. If the subject is valid, the user is added to the list of connections accociated by that subject, and the server sends an acknowledgement back to the client. If the subject is not valid, the server sends an error message to the client, notifying them that the subject is not found. If a client subscribes to a topic, the server iterates through the message history for that topic and sends all missed messages.  
* For a PUB message type, the server performs the same check for a valid subject. If the subject is valid, it appends the message to the message_history table under the proper subject. Next the server iterates through all subscribers to that topic and sends the message to each client. 
* Finally, for the DISC message type, the server sends an acknowledgement back to the client allowsing the client to disconnect.

## Completed Sections
For phase 1 of the project, all sections assigned are completed, and there are no unfinished parts.

## Workflow
I started the project by creating a basic connection between the client and the server to make sure I understood how socket programming works. Then I began working on client.py, creating an interface for user input and sending messages to the server. Next, I handled the server creating new threads for each client and sending acknowledgements back to the client. Finally, I handled the DISC command in the client in order to allow for a smooth disconnection, and I ensured that the server properly handled messages with invalid subjects.
