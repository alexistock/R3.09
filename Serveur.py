import os
import socket
import subprocess
import threading
import sys


class Serveur:
    def __init__(self, port=1002):
        """
        Initialise un serveur TCP capable d'exécuter des programmes.

        :param port: Port d'écoute du serveur (par défaut 1001)
        :type port: int
        """
        self.port = port
        self.socket = socket.socket()  # Création du socket serveur
        self.socket.bind(('0.0.0.0', self.port))  # Associer le socket à toutes les interfaces réseau
        self.socket.listen(5)  # Mettre le socket en mode écoute avec un backlog de 5
        self.serveur_occupe = False  # Indique si le serveur est en cours de traitement
        print(f"Serveur démarré sur le port {self.port}")

    def executer_programme(self, programme, extension):
        """
        Exécute un programme selon son extension et renvoie le résultat.

        :param programme: Contenu du programme à exécuter
        :type programme: str
        :param extension: Extension du fichier (py, c, js)
        :type extension: str
        :return: Résultat de l'exécution ou message d'erreur
        :rtype: str
        """
        nom_fichier_temp = f"programme.{extension}"  # Nom du fichier temporaire
        try:
            # Crée et écrit dans le fichier temporaire
            with open(nom_fichier_temp, 'w') as fichier:
                fichier.write(programme)

            # Exécution selon l'extension
            if extension == 'py':
                resultat_execution = subprocess.run(
                    ["python", nom_fichier_temp],
                    capture_output=True,
                    text=True
                )
            elif extension == 'c':
                resultat_compilation = subprocess.run(
                    ["gcc", nom_fichier_temp, "-o", "programme_temp"],
                    capture_output=True,
                    text=True
                )
                if resultat_compilation.returncode != 0:
                    return f"Erreur de compilation C : {resultat_compilation.stderr}"
                resultat_execution = subprocess.run(
                    ["./programme_temp"],
                    capture_output=True,
                    text=True
                )
            elif extension == 'js':
                resultat_execution = subprocess.run(
                    ["node", nom_fichier_temp],
                    capture_output=True,
                    text=True
                )
            else:
                return "Extension non supportée."

            # Retourne le résultat de l'exécution ou les erreurs
            return resultat_execution.stdout or resultat_execution.stderr
        except Exception as e:
            return f"Erreur d'exécution : {str(e)}"
        finally:
            # Nettoyer les fichiers temporaires
            if os.path.exists(nom_fichier_temp):
                os.remove(nom_fichier_temp)
            if extension == 'c' and os.path.exists("programme_temp"):
                os.remove("programme_temp")

    def gerer_client(self, connexion, adresse):
        """
        Gère une connexion client et traite une demande d'exécution de programme.

        :param connexion: Objet de socket pour le client
        :param adresse: Adresse du client
        :type adresse: tuple
        """
        if self.serveur_occupe:
            connexion.send("Erreur : Serveur occupé, réessayez plus tard.".encode())
            connexion.close()
            return

        self.serveur_occupe = True
        try:
            print(f"Connexion acceptée de {adresse}")
            connexion.send("Envoie du Programme".encode())  # Invitation à envoyer le programme

            extension = connexion.recv(1024).decode().strip()  # Récupère l'extension
            connexion.send(b"OK")  # Accusé de réception

            nb_lignes = int(connexion.recv(1024).decode().strip())  # Récupère le nombre de lignes
            connexion.send(b"OK")

            programme = ""
            for _ in range(nb_lignes):
                ligne = connexion.recv(1024).decode()  # Récupère chaque ligne du programme
                programme += ligne
                connexion.send(b"OK")  # Accusé de réception pour chaque ligne

            resultat = self.executer_programme(programme, extension)  # Exécute le programme
            connexion.send((resultat or "Aucun résultat produit.").encode())  # Envoie le résultat au client

            confirmation = connexion.recv(1024).decode()  # Confirmation de réception par le client
            if confirmation == "message recu":
                print("Résultat envoyé avec succès.")
        except Exception as e:
            print(f"Erreur avec le client {adresse} : {str(e)}")
        finally:
            self.serveur_occupe = False
            connexion.close()

    def demarrer(self):
        """
        Démarre le serveur et accepte les connexions client.
        """
        print("En attente de connexions...")
        while True:
            connexion, adresse = self.socket.accept()  # Accepte une connexion client
            threading.Thread(target=self.gerer_client, args=(connexion, adresse), daemon=True).start()


if __name__ == '__main__':
    # Analyse des arguments pour définir le port
    if len(sys.argv) > 2:
        print("Erreur : Trop d'arguments. Utilisation : python serveur.py [port]")
        sys.exit(1)

    if len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])
            serveur = Serveur(port)
        except ValueError:
            print("Erreur : Le port doit être un nombre entier.")
            sys.exit(1)
    else:
        serveur = Serveur()  # Utilise le port par défaut

    try:
        serveur.demarrer()
    except KeyboardInterrupt:
        print("\nServeur arrêté.")
        serveur.socket.close()
        sys.exit(0)
