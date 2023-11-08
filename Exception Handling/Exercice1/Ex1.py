def divEntier(x: int, y: int) -> int:
    if y == 0:
        raise ZeroDivisionError("y doit être supérieur à 0")
    if y <= 0 or x <= 0:
        raise ValueError("x et y doivent être positifs non nuls")
    if x < y:
        return 0
    else:
        return divEntier(x -y, y) + 1