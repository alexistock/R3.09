import socket
import sys
import threading
import datetime
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QFileDialog


class Client(threading.Thread):
    def __init__(self, host: str, chemin_fichier: str, extension: str, update_callback: object, update_timer_callback: object):
        """
        Constructeur de la classe Client.

        :param host: Adresse IP du serveur
        :type host: str
        :param chemin_fichier: Chemin du fichier à envoyer
        :type chemin_fichier: str
        :param extension: Extension du fichier
        :type extension: str
        :param update_callback: Fonction de callback pour mettre à jour les messages
        :type update_callback: callable
        :param update_timer_callback: Fonction de callback pour mettre à jour le timer
        :type update_timer_callback: callable
        """
        super().__init__()

        self.host = host  # Adresse IP du serveur
        self.chemin_fichier = chemin_fichier  # Chemin vers le fichier local
        self.extension = extension  # Extension du fichier
        self.update_callback = update_callback  # Callback pour afficher des messages
        self.update_timer_callback = update_timer_callback  # Callback pour mettre à jour le timer
        self.liste_des_serveur = []  # Liste des serveurs et ports extraits du fichier de config
        self.socket = None  # Socket client initialisé
        self.start_time = None  # Temps de début du transfert
        self.end_time = None  # Temps de fin du transfert
        self.timer_running = False  # Indicateur pour savoir si le timer est actif
        self.timer_thread = None  # Thread dédié à l'actualisation du timer


    def run(self):
        """
        Méthode principale exécutée lors du démarrage du thread.
        """
        try:
            self.update_callback(f"Tentative de connexion au serveur")
            print(self.host)
            self.liste_serveur()  # Chargement de la liste des serveurs
            print(self.liste_des_serveur)
            if self.host in self.liste_des_serveur:  # Vérifie si l'IP est dans la liste des serveurs
                port = int(self.liste_des_serveur[self.liste_des_serveur.index(self.host) + 1])  # Récupération du port associé
                self.socket = socket.socket()  # Création du socket client
                
                try:
                    self.socket.connect((self.host, port))  # Connexion au serveur
                except ConnectionRefusedError as e:  # Gestion spécifique de l'erreur de connexion refusée
                    self.update_callback("Le serveur a refusé la connexion ou n'est pas accesible . Voici d'autres IP disponibles :")
                    
                    # Affichage des autres IP disponibles
                    for i in range(0, len(self.liste_des_serveur), 2):
                        ip, port = self.liste_des_serveur[i], self.liste_des_serveur[i + 1]
                        if ip != self.host:  # Exclure l'IP actuelle
                            self.update_callback(f"- IP : {ip}, Port : {port}")
                    return  # Arrête l'exécution après avoir listé les autres IP
                
                self.start_timer()  # Démarrage du timer
                self.envoyer_programme(self.chemin_fichier, self.extension)  # Envoi du fichier au serveur
            else:
                self.update_callback("IP non présente dans le fichier de configuration")
        except Exception as e:
            self.update_callback(f"Erreur réseau : {str(e)}")
        finally:
            if self.socket:
                self.socket.close()  # Fermeture du socket
            self.stop_timer()  # Arrêt du timer


    def envoyer_programme(self, fichier: str, extension_fichier: str):
        """
        Envoie le fichier spécifié au serveur, ligne par ligne.

        :param fichier: Chemin du fichier
        :type fichier: str
        :param extension_fichier: Extension du fichier
        :type extension_fichier: str
        """
        try:
            # Réception du message initial du serveur
            message_initial = self.socket.recv(1024).decode()
            self.update_callback(message_initial)

            # Vérification de l'erreur "Essayez plus tard"
            if "Erreur : Essayez plus tard" in message_initial:
                self.update_callback("Le serveur est occupé. Voici d'autres IP disponibles :")
                
                # Affichage des autres IP disponibles
                for i in range(0, len(self.liste_des_serveur), 2):
                    ip, port = self.liste_des_serveur[i], self.liste_des_serveur[i + 1]
                    if ip != self.host:  # Exclure l'IP actuelle
                        self.update_callback(f"- IP : {ip}, Port : {port}")
                return  # Arrête l'envoi après avoir listé les autres IP

            # Lecture du fichier local
            with open(fichier, 'r') as programme:
                lignes = programme.readlines()

            # Envoi des données au serveur
            self.socket.send((extension_fichier + "\n").encode())
            reponse = self.socket.recv(1024).decode()
            if "Erreur" in reponse:
                self.update_callback(reponse)
                return

            self.socket.send((str(len(lignes)) + "\n").encode())
            self.socket.recv(1024)  # Confirmation

            for ligne in lignes:
                self.socket.send(ligne.encode())
                self.socket.recv(1024)

            # Réception du résultat final
            resultat = self.socket.recv(1024).decode()
            self.update_callback(f"Résultat reçu : {resultat}")
            self.socket.send("message recu".encode())
        except Exception as erreur:
            self.update_callback(f"Erreur lors de l'envoi : {str(erreur)}")



    def liste_serveur(self):
        """
        Lit le fichier de configuration pour extraire les IPs et ports des serveurs.
        """
        try:
            with open("config/config.txt", "r") as fichier_config:
                for ligne in fichier_config:
                    ip, port = ligne.strip().split('|')
                    self.liste_des_serveur.append(ip)
                    self.liste_des_serveur.append(port)
        except FileNotFoundError:
            self.update_callback("Erreur : Le fichier de configuration 'config.txt' est introuvable.")
        except Exception as e:
            self.update_callback(f"Erreur de lecture du fichier de configuration : {str(e)}")

    def start_timer(self):
        """
        Démarre le timer pour mesurer le temps d'exécution.
        """
        self.start_time = datetime.datetime.now()
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self.update_timer)
        self.timer_thread.start()

    def stop_timer(self):
        """
        Arrête le timer.
        """
        self.timer_running = False
        self.end_time = datetime.datetime.now()

    def update_timer(self):
        """
        Met à jour le timer tant qu'il est actif.
        """
        while self.timer_running:
            elapsed = (datetime.datetime.now() - self.start_time).seconds
            self.update_timer_callback(elapsed)


class MainWindow(QMainWindow):
    def __init__(self):
        """
        Constructeur de la fenêtre principale.
        """
        super().__init__()
        self.setWindowTitle("Client")
        self.chemin_fichier = ""  # Chemin du fichier sélectionné

        # Initialisation des composants de l'interface utilisateur
        self.label_ip_machine = QLabel("IP Serveur")
        self.ip_machine = QLineEdit()  # Champ pour l'adresse IP
        self.erreur_ip_machine = QLabel()  # Affiche les erreurs liées à l'IP
        self.label_upload = QLabel("Sélection Programme")
        self.selection_fichier_btn = QPushButton("Fichier")  # Bouton pour sélectionner un fichier
        self.extension = QComboBox()  # Liste déroulante pour les extensions
        self.extension.addItems(["", "py", "js", "c"])
        self.selection_fichier_erreur = QLabel()  # Affiche les erreurs liées au fichier
        self.resultat_programme = QTextEdit()  # Zone pour afficher les messages
        self.resultat_programme.setReadOnly(True)
        self.bouton_upload = QPushButton("Upload")  # Bouton pour lancer l'upload
        self.label_chrono = QLabel("Temps d'exécution : 0 secondes")

        # Disposition des composants dans une grille
        self.grid = QGridLayout()
        self.grid.addWidget(self.label_ip_machine, 0, 0)
        self.grid.addWidget(self.ip_machine, 0, 1, 1, 2)
        self.grid.addWidget(self.erreur_ip_machine, 1, 0, 1, 3)
        self.grid.addWidget(self.label_upload, 2, 0)
        self.grid.addWidget(self.selection_fichier_btn, 2, 1)
        self.grid.addWidget(self.extension, 2, 2)
        self.grid.addWidget(self.selection_fichier_erreur, 3, 0, 1, 3)
        self.grid.addWidget(self.bouton_upload, 4, 0, 1, 3)
        self.grid.addWidget(self.label_chrono, 5, 0, 1, 3)
        self.grid.addWidget(self.resultat_programme, 6, 0, 1, 3)

        self.root = QWidget()
        self.root.setLayout(self.grid)
        self.setCentralWidget(self.root)

        # Connexion des boutons à leurs fonctions
        self.selection_fichier_btn.clicked.connect(self.selection_fichier)
        self.bouton_upload.clicked.connect(self.lancement_upload)



    def selection_fichier(self):
        """
        Ouvre une boîte de dialogue pour sélectionner un fichier.
        """
        chemin_du_fichier, _ = QFileDialog.getOpenFileName(self, "Explorateur de Fichiers", "", "Fichiers Python, C, JavaScript (*.py *.c *.js)")
        self.chemin_fichier = chemin_du_fichier

    def lancement_upload(self):
        """
        Vérifie les entrées et démarre un thread client pour envoyer le fichier au serveur.
        """
        ip = self.ip_machine.text()
        if not ip:
            self.erreur_ip_machine.setText("IP manquante")
            return
        if not self.chemin_fichier:
            self.selection_fichier_erreur.setText("Aucun fichier sélectionné")
            return

        client_thread = Client(ip, self.chemin_fichier, self.extension.currentText(), self.append_result, self.update_timer)
        client_thread.start()

    def append_result(self, message: str):
        """
        Ajoute un message dans la zone de texte des résultats.

        :param message: Message à afficher
        :type message: str
        """
        self.resultat_programme.append(message)

    def update_timer(self, temp_excution: int):
        """
        Met à jour l'affichage du temps écoulé.

        :param elapsed: Temps écoulé en secondes
        :type elapsed: int
        """
        self.label_chrono.setText(f"Temps d'exécution : {temp_excution} secondes")


if __name__ == '__main__':
    # Point d'entrée principal de l'application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
