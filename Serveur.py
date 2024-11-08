import socket


class Serveur:
    def __init__(self, port):
        self.__port = port
        self.current_client = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", port))
        self.server_socket.listen(5)  
        self.etat = 'run'
    
    @property
    def port(self):
        return self.__port
    
    @port.setter
    def port(self, nouveau_port):
        self.__port = nouveau_port

    def detection(self):
        while self.etat == 'run':
            try:
                conn, address = self.server_socket.accept()
                """client_thread = threading.Thread(target=self.commandeclient, args=(conn, address))
                client_thread.start()
                """
                message = 'Vous étes connecter au serveur'
                conn.send(message.encode())
                print(f"Client Connecter: {address}")
                
                    
            except Exception as e:
                print("Erreur lors de l'acceptation de la connexion :", e)
                break  

if __name__ == "__main__":
    port = int(input('Entrer le numéro de port du serveur '))    
    serveur = Serveur(port)
    print(f"Serveur en écoute sur le port {port}")
    serveur.detection()
    