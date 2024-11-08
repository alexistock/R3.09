import socket
class Client:
    def __init__(self, ip='127.0.0.1', port=1028):
        self.client_socket = socket.socket()
        self.ip = ip
        self.port = port

    def connect(self):
        try:
            self.client_socket.connect((self.ip, self.port))
            print(f"Connecté au serveur {self.ip} sur le port {self.port}")
        except Exception as e:
            print("Erreur de connexion au serveur :", e)
    
    def message_recu(self):
        data = self.client_socket.recv(1024).decode()
        print("Réponse du serveur:", data)
    def p(self):
        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.client_socket.close()
            
            print("Deconnection")
if __name__ == "__main__":

    ip = input("Entrez l'adresse IP du serveur (par défaut: 127.0.0.1): ") or "127.0.0.1"
    port = int(input("Entrez le port du serveur (par défaut: 1028): ") or 1028)
    client = Client(ip, port)
    client.connect()
    client.message_recu()
    client.p()
    