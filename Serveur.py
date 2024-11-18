import socket
import threading

class serveur:
    def __init__(self,nbr_serveur,lst_port= []):
        self.lst_port = lst_port
        self.nbr_serveur = nbr_serveur
        self.liste_serveur = []
        self.thread_list = []
        self.etat = 'run'
        for i in self.lst_port:

            tmp_socket = socket.socket()
            tmp_socket.bind(("0.0.0.0",i))
            tmp_socket.listen(1) 
            self.liste_serveur.append(tmp_socket)

    def lancement_tout_les_serveurs(self):
        for serv in self.liste_serveur:
            t = threading.Thread(target=self.start_un_serveur, args=[serv])
            t.start()
            self.thread_list.append(t)

    def start_un_serveur(self, serv):
        while self.etat == 'run':
            try:
                print(1)
                conn, address = serv.accept()
                """client_thread = threading.Thread(target=self.commandeclient, args=(conn, address))
                client_thread.start()
                """
                message = 'Vous étes connecter au serveur'
                conn.send(message.encode())
                print(f"Client Connecter: {address}")
                
                    
            except Exception as e:
                print("Erreur lors de l'acceptation de la connexion :", e)
                break  


            


        
