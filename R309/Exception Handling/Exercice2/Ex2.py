nom_fichier = "exemple.txt"

try:
    with open(nom_fichier, 'r') as fichier:
        for ligne in fichier:
            ligne = ligne.rstrip("\n\r")
            print(ligne)

except FileNotFoundError:
    print(f"Erreur : Le fichier '{nom_fichier}' n'a pas été trouvé.")

except IOError:
    print(f"Erreur d'entrée/sortie lors de la lecture du fichier '{nom_fichier}'.")

except PermissionError:
    print(f"Erreur : Vous n'avez pas la permission d'accéder au fichier '{nom_fichier}'.")

except FileExistsError:
    print(f"Erreur : Le fichier '{nom_fichier}' existe déjà (ce qui ne devrait pas arriver ici).")

finally:
    print("Fin du programme.")
