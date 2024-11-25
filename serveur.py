import socket
import sys 
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QTextEdit
import threading



app = QApplication(sys.argv)
root = QWidget()
root.resize(300, 300)
root.setWindowTitle('Le serveur de chat')
grid = QGridLayout()
serveur_label = QLabel('Serveur')
serveur_edit = QLineEdit("localhost")
port_label = QLabel('Port')
port_edit = QLineEdit("4200")
nombre_client_label = QLabel ('Nombre de clients maximum')
nombre_client_edit = QLineEdit ('5')
btn_démarage = QPushButton('Démarrage du serveur')
btn_arrete = QPushButton('Arrêt du serveur')
text = QTextEdit('')
grid.addWidget(serveur_label,0,0)
grid.addWidget(serveur_edit,0,1)
grid.addWidget(port_label,1,0)
grid.addWidget(port_edit,1,1)
grid.addWidget(nombre_client_label,2,0)
grid.addWidget(nombre_client_edit,2,1)
grid.addWidget(btn_démarage,3,0)
grid.addWidget(text,4,0)

root.setLayout(grid)


def lancement_serveur  ():
    server_socket = socket.socket()
    server_socket.bind((serveur_edit.text(), int(port_edit.text()))) 
    server_socket.listen(int(nombre_client_edit.text()))  
    conn, address = server_socket.accept() 
    data = conn.recv(1024).decode() 
            

def démarage ():
    grid.removeWidget(btn_démarage)
    root.setLayout(grid)
    grid.addWidget(btn_arrete,3,0)
    root.setLayout(grid)
    root.show()
    Lancement_serveur = threading.Thread(target=lancement_serveur)
    Lancement_serveur.start()

def arret ():
    grid.removeWidget(btn_arrete)
    root.setLayout(grid)
    grid.addWidget(btn_démarage,3,0)
    root.setLayout(grid)
    root.show()

btn_démarage.clicked.connect(démarage)
btn_arrete.clicked.connect(arret)
root.show()
sys.exit(app.exec())

        