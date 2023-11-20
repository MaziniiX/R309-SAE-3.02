def divEntier(x: int, y: int) -> int:
    """
    Cette fonction effectue une division entière de deux nombres positifs.

    Args:
        x (int): Le dividende. Doit être un nombre positif.
        y (int): Le diviseur. Doit être un nombre positif différent de zéro.

    Returns:
        int: Le résultat de la division entière de x par y.

    Raises:
        ValueError: Si x ou y sont négatifs, ou si y est égal à zéro.
    """
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
    """
    Cette fonction principale demande à l'utilisateur d'entrer deux nombres entiers, puis affiche le résultat de leur division entière.
    En cas d'erreur, un message d'erreur est affiché.
    """
    try:
        x = int(input("Entrez la valeur de x : "))
        y = int(input("Entrez la valeur de y : "))

        result = divEntier(x, y)
        print(f"Le résultat de la division entière de {x} par {y} est : {result}")

    except ValueError as ve:
        print(f"Erreur : {ve}")


if __name__ == "__main__":
    main()
