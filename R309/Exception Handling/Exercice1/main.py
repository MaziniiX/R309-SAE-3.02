from Ex1 import *

if __name__ == '__main__':
    flag = False # flag fait guise de signal d'erreur (initialisé a False)
    while not flag:
        try:
            x = int(input("x: "))
            y = int(input("y: "))
        except ValueError:
            print("Erreur de saisie")
        else:
            flag = True
    try:
        a = divEntier(x, y)
    except ValueError as err:
        print(err)
    else:
        print(a)