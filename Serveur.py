import socket
import subprocess
import threading
import sys

class Serveur:
    def __init__(self, port=1000):
        """
        Initialise le serveur, crée le socket et commence à écouter les connexions des clients.

        :param port: Le port sur lequel le serveur écoutera les connexions, par défaut 1000
        :type port: int
        """
        self.port = port
        self.socket = socket.socket()  # Création du socket serveur
        self.socket.bind(('0.0.0.0', self.port))  # Lier le socket à l'adresse et au port
        self.socket.listen(5)  # Permettre jusqu'à 5 connexions en file d'attente
        self.verrou = threading.Lock()  # Verrou pour gérer les accès simultanés
        print(f"Serveur démarré sur le port {self.port}")

    def executer_programme(self, programme, extension):
        """
        Exécute le programme reçu en fonction de son extension (Python, C, JavaScript).

        :param programme: Le code source à exécuter
        :type programme: str
        :param extension: L'extension du fichier (py, c, js)
        :type extension: str
        :return: Le résultat de l'exécution du programme (stdout ou stderr)
        :rtype: str
        """
        nom_fichier_temp = f"programme.{extension}"  # Création du fichier temporaire
        with open(nom_fichier_temp, 'w') as fichier:
            fichier.write(programme)

        try:
            # Exécution en fonction de l'extension
            if extension == 'py':
                resultat_execution = subprocess.run(["python", nom_fichier_temp], capture_output=True, text=True)
            elif extension == 'c':
                resultat_compilation = subprocess.run(["gcc", nom_fichier_temp, "-o", "programme_temp"], capture_output=True, text=True)
                if resultat_compilation.returncode != 0:
                    return f"Erreur de compilation C : {resultat_compilation.stderr}"
                resultat_execution = subprocess.run(["./programme_temp"], capture_output=True, text=True)
            elif extension == 'js':
                resultat_execution = subprocess.run(["node", nom_fichier_temp], capture_output=True, text=True)
            else:
                return "Extension non supportée."

            return resultat_execution.stdout or resultat_execution.stderr
        except Exception as e:
            return f"Erreur d'exécution : {str(e)}"

    def gerer_client(self, connexion, adresse):
        """
        Gère la connexion d'un client en recevant le programme à exécuter et en envoyant les résultats.

        :param connexion: La connexion avec le client
        :type connexion: socket.socket
        :param adresse: L'adresse du client
        :type adresse: tuple
        """
        # Utiliser le verrou pour gérer un seul client à la fois
        if not self.verrou.acquire(blocking=False):
            connexion.send("Erreur : Serveur occupé, réessayez plus tard.".encode())
            connexion.close()
            return

        try:
            print(f"Connexion acceptée de {adresse}")
            extension = connexion.recv(1024).decode().strip()
            connexion.send(b"OK")

            nb_lignes = int(connexion.recv(1024).decode().strip())
            connexion.send(b"OK")

            programme = ""
            for _ in range(nb_lignes):
                ligne = connexion.recv(1024).decode()
                programme += ligne
                connexion.send(b"OK")

            resultat = self.executer_programme(programme, extension)
            connexion.send((resultat or "Aucun résultat produit.").encode())

            confirmation = connexion.recv(1024).decode()
            if confirmation == "message recu":
                print("Résultat envoyé avec succès.")
        except Exception as e:
            print(f"Erreur avec le client {adresse} : {str(e)}")
        finally:
            self.verrou.release()
            connexion.close()

    def demarrer(self):
        """
        Lance le serveur et attend les connexions des clients.
        """
        print("En attente de connexions...")
        while True:
            connexion, adresse = self.socket.accept()
            threading.Thread(target=self.gerer_client, args=(connexion, adresse)).start()


if __name__ == '__main__':
    # Vérification des arguments passés en ligne de commande
    if len(sys.argv) > 2:
        print("Erreur : Trop d'arguments. Utilisation : python serveur.py [port]")
        sys.exit(1)

    # Si un argument est passé, utiliser ce port. Sinon, utiliser le port par défaut 1000.
    if len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])
            serveur = Serveur(port)
        except ValueError:
            print("Erreur : Le port doit être un nombre entier.")
            sys.exit(1)
    else:
        serveur = Serveur()

    # Démarrage du serveur
    try:
        serveur.demarrer()
    except KeyboardInterrupt:
        print("\nServeur arrêté.")
        serveur.socket.close()  # Fermeture du socket
        sys.exit(0)  # Terminer le programme
