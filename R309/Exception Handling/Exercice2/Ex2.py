nom_fichier = "exemple.txt"

try:
    """
    Cette partie du code tente d'ouvrir un fichier en mode lecture et d'imprimer chaque ligne.
    """
    with open(nom_fichier, 'r') as fichier:
        for ligne in fichier:
            ligne = ligne.rstrip("\n\r")
            print(ligne)

except FileNotFoundError:
    """
    Cette exception est levée si le fichier spécifié n'est pas trouvé.
    """
    print(f"Erreur : Le fichier '{nom_fichier}' n'a pas été trouvé.")

except IOError:
    """
    Cette exception est levée en cas d'erreur d'entrée/sortie lors de la lecture du fichier.
    """
    print(f"Erreur d'entrée/sortie lors de la lecture du fichier '{nom_fichier}'.")

except PermissionError:
    """
    Cette exception est levée si le programme n'a pas la permission d'accéder au fichier spécifié.
    """
    print(f"Erreur : Vous n'avez pas la permission d'accéder au fichier '{nom_fichier}'.")

except FileExistsError:
    """
    Cette exception est levée si le fichier spécifié existe déjà. Cependant, cela ne devrait pas se produire ici car nous ouvrons le fichier en mode lecture.
    """
    print(f"Erreur : Le fichier '{nom_fichier}' existe déjà (ce qui ne devrait pas arriver ici).")

finally:
    """
    Cette partie du code est exécutée à la fin du programme, qu'une exception soit levée ou non.
    """
    print("Fin du programme.")
