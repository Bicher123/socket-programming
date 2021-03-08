import socket
import argparse 
import threading
import os
from random_username.generate import generate_username

PORT = 8080
SERVER = "127.0.0.1"

# list of clients and their nicknames ... list of tuples ==> [(nickname,client)]
clients = []
usernames=[]

# when a message is received send back the message to all channels
def send_received_message(msg):
    for client in clients:       
        client.send(msg)

def handle_client(client):
    while True:
        try:
            # send the message received to all users
            msg = client.recv(1024).decode('utf-8')
            if msg=="DISCONNECT":
                client.send("-CLOSE-".encode('utf-8'))
                remove_client(client)
            if msg[0:4] == 'NICK':
                m = msg.split()
                old_nickname = m[1]
                new_nickname = m[2]
                if(m[2] not in usernames):
                    client.send(f'NICK {new_nickname}'.encode('utf-8'))
                    i = usernames.index(old_nickname)
                    usernames[i]=new_nickname
                    send_received_message(f'#global<:::>{old_nickname} has changed nickname to {new_nickname}'.encode('utf-8'))
                else:
                    client.send(f'#global<:::>The new nickname provided is already in use.'.encode('utf-8'))
            else:
                send_received_message(msg.encode('utf-8'))
        except:
            # remove the client
            remove_client(client) 
            break

def remove_client(client):
    index=0
    for c in clients:
        if c == client:
            client.close()
            clients.remove(c)
            x=usernames[index] 
            # notify all user that cleint has left
            print(f"{x} has left the channel")
            send_received_message(f'#global<:::>-- {x} has left the channel -- '.encode('utf-8'))
            usernames.remove(x)   
        index+=1
    if(len(usernames)<1):
        print("no more client ... exiting")
        os._exit(0)
    
    
def start():
    # initialize socket
    server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind to port and server
    server.bind((SERVER, int(args.port)))
    print("[STARTING] starting the server")
    server.listen()
    print(f"[LISTENING] listen to server: {SERVER}")
    while True:
        # accept connection and set a client and the address
        client, address = server.accept()                           
        print(f"Connected with {address}")

        rand_name = generate_username(2)
        while rand_name[0] in usernames:
           rand_name = generate_username(2)
        client.send(f'NICK {rand_name[0]}'.encode('utf-8'))
        print(f"{rand_name[0]} has successfully joined the channel")
        
        # append client and usernames
        clients.append(client)
        usernames.append(rand_name[0])
        
        # notify everyone that client has joined the channel
        send_received_message(f"#global<:::>{rand_name[0]} joined the channel".encode('utf-8'))

        # handle client in a thread
        client_thread = threading.Thread(target=handle_client, args=(client,))
        client_thread.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help = "Target port to use.", required = False, default = "")
    args = parser.parse_args()
    
    start()
    
        