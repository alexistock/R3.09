def divEntier(x: int, y: int) -> int: 
    if y == 0 :
        raise ValueError("la valeur de y ne peux pas etre 0")
    if y  < 0 or x < 0:
        raise ValueError("la valeur de x et y ne peux pas etre negative") 
    else:
        if x < y: #si x est inefrieur a y le code retourne  0
            return 0
        else: #sinon on enleve la valeur de y a x et on rappelle la fonction avec la nouvelle valeur de x et nous rajoutons 1 a la valeur du retour de la fonctioons
            x = x - y
            return divEntier(x, y) + 1 

        
def main ():
    try:
        x = int(input("Entrer la valeur de x (entier): "))
        y = int(input("Entrer la valeur de y (entier): "))
    except ValueError as err: #on utilise value error pour gerer les erreur de valeur que l'utilisateur peux generer
         print(f"Erreur: {err}")
    else:
        print(divEntier(x,y))

main()