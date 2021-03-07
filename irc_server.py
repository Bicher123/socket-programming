import socket
import argparse 
import threading
HEADER = 64
PORT = 8080
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
list_of_clients =[]
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        list_of_clients.append(conn)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if not msg:
                break
            broadcast(msg.encode(FORMAT), conn)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{addr}] {msg}")
            
    conn.close()

def broadcast(message,conn):
    for client in list_of_clients:
        if client!=conn:
            try:
                client.send(message)
            except:
                client.close()
                remove(client)
               
def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)             

def start(s):
    
    s.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = s.accept()
        list_of_clients.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help = "Target port to use.", required = False, default = "")

    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((SERVER, int(args.port)))
        print("[STARTING] server is starting...")
        start(s)