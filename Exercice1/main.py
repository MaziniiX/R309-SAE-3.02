from Ex1 import *

if __name__ == '__main__':
    try:
        x = int(input("x: "))
        y = int(input("y: "))
        divEntier(x, y)
    except ValueError:
        print("Valeur incorrecte")
    else:
        print(res)
