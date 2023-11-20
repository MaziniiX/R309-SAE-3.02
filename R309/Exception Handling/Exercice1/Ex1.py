def divEntier(x: int, y: int) -> int:
    if x < 0 or y < 0:
        raise ValueError("Les nombres doivent être positifs")
    if y == 0:
        raise ValueError("Le diviseur (y) ne peut pas être zéro")
    if x < y:
        return 0
    else:
        x = x - y
        return divEntier(x, y) + 1


def main():
    try:
        x = int(input("Entrez la valeur de x : "))
        y = int(input("Entrez la valeur de y : "))

        result = divEntier(x, y)
        print(f"Le résultat de la division entière de {x} par {y} est : {result}")

    except ValueError as ve:
        print(f"Erreur : {ve}")


if __name__ == "__main__":
    main()
