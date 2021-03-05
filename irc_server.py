import socket
import argparse

host = '127.0.0.1'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help = "Target port to use.", required = False, default = "")

    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, int(args.port)))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)
