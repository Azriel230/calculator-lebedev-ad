import socket
import os
import json
import threading

from dotenv import load_dotenv

from database import HistoryInstance


load_dotenv("./.env")
HOST = os.getenv("SERVERHOST", "127.0.0.1")
PORT = os.getenv("SERVERPORT", 65432)

class TCPServer:

    def __init__(self, host=HOST, port=int(PORT)):
        self.clients: list[socket.socket] = []
        self.host = host
        self.port = port
        self.lock = threading.Lock()
        self.running = False

    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(3)
        self.running = True
        accept_thread = threading.Thread(target=self._accept_connections)
        accept_thread.daemon = True
        accept_thread.start()

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        with self.lock:
            for client in self.clients:
                client.close()
            self.clients.clear()

    def _accept_connections(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"New connection from {addr}")
                with self.lock:
                    self.clients.append(client_socket)
            except OSError:
                break
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def send_message(self,message: str):
        dead_clients = []

        with self.lock:
            for client  in self.clients:
                try:
                    client.sendall(message.encode("utf-8"))
                except Exception as e:
                    print(f"Error sending message: {e}")
                    dead_clients.append(client)

            for client in dead_clients:
                try:
                    print(f"Removing client: {client}")
                    client.close()
                    self.clients.remove(client)
                except ValueError:
                    pass # already removed
