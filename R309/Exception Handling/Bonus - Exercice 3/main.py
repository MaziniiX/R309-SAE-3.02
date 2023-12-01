import csv

class Article:
    TVA = 0.20  # Taux de TVA (20%)

    def __init__(self, nom, code_barre, prix_ht):
        self.set_nom(nom)
        self.set_code_barre(code_barre)
        self.set_prix_ht(prix_ht)

    def set_nom(self, nom):
        self.nom = str(nom)

    def set_code_barre(self, code_barre):
        self.code_barre = str(code_barre)

    def set_prix_ht(self, prix_ht):
        prix_ht = float(prix_ht)
        if prix_ht <= 0:
            raise ValueError("Le prix hors taxe doit être supérieur à zéro.")
        self.prix_ht = prix_ht

    def get_nom(self):
        return self.nom

    def get_code_barre(self):
        return self.code_barre

    def get_prix_ht(self):
        return self.prix_ht

    def changer_prix(self, nouveau_prix):
        self.set_prix_ht(nouveau_prix)

    def prix_ttc(self):
        return self.prix_ht * (1 + self.TVA)


class Stock:
    def __init__(self):
        self.articles = {}

    def taille(self):
        return len(self.articles)

    def ajout(self, article):
        if article.get_code_barre() in self.articles:
            raise ValueError("Un article avec le même code barre est déjà en stock.")
        self.articles[article.get_code_barre()] = article

    def recherche_par_code_barre(self, code_barre):
        if code_barre not in self.articles:
            raise ValueError("L'article n'est pas en stock.")
        return self.articles[code_barre]

    def recherche_par_nom(self, nom):
        for article in self.articles.values():
            if article.get_nom() == nom:
                return article
        raise ValueError("L'article n'est pas en stock.")

    def supprime_par_code_barre(self, code_barre):
        if code_barre not in self.articles:
            raise ValueError("L'article n'est pas en stock.")
        del self.articles[code_barre]

    def supprime_par_nom(self, nom):
        article = self.recherche_par_nom(nom)
        del self.articles[article.get_code_barre()]

    def charger_depuis_csv(self, fichier_csv):
        with open(fichier_csv, 'r') as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                nom, code_barre, prix_ht = row
                article = Article(nom, code_barre, prix_ht)
                self.ajout(article)

    def sauvegarder_dans_csv(self, fichier_csv):
        with open(fichier_csv, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            for article in self.articles.values():
                writer.writerow([article.get_nom(), article.get_code_barre(), article.get_prix_ht()])


# Tests unitaires
import unittest

class TestStock(unittest.TestCase):
    def test_ajout_et_taille(self):
        stock = Stock()
        self.assertEqual(stock.taille(), 0)

        article1 = Article("Article1", "123456", 10.0)
        stock.ajout(article1)
        self.assertEqual(stock.taille(), 1)

        article2 = Article("Article2", "789012", 15.0)
        stock.ajout(article2)
        self.assertEqual(stock.taille(), 2)

    def test_recherche_par_code_barre(self):
        stock = Stock()
        article1 = Article("Article1", "123456", 10.0)
        stock.ajout(article1)

        article2 = stock.recherche_par_code_barre("123456")
        self.assertEqual(article2.get_nom(), "Article1")

        with self.assertRaises(ValueError):
            stock.recherche_par_code_barre("789012")

    def test_recherche_par_nom(self):
        stock = Stock()
        article1 = Article("Article1", "123456", 10.0)
        stock.ajout(article1)

        article2 = stock.recherche_par_nom("Article1")
        self.assertEqual(article2.get_code_barre(), "123456")

        with self.assertRaises(ValueError):
            stock.recherche_par_nom("Article2")

    def test_supprime_par_code_barre(self):
        stock = Stock()
        article1 = Article("Article1", "123456", 10.0)
        stock.ajout(article1)

        stock.supprime_par_code_barre("123456")
        self.assertEqual(stock.taille(), 0)

        with self.assertRaises(ValueError):
            stock.supprime_par_code_barre("789012")

    def test_supprime_par_nom(self):
        stock = Stock()
        article1 = Article("Article1", "123456", 10.0)
        stock.ajout(article1)

        stock.supprime_par_nom("Article1")
        self.assertEqual(stock.taille(), 0)

        with self.assertRaises(ValueError):
            stock.supprime_par_nom("Article2")

    def test_charger_et_sauvegarder_csv(self):
        stock = Stock()
        stock.charger_depuis_csv("stock_test.csv")
        self.assertEqual(stock.taille(), 2)

        stock.sauvegarder_dans_csv("stock_sauvegarde_test.csv")

        stock_vide = Stock()
        stock_vide.charger_depuis_csv("stock_sauvegarde_test.csv")
        self.assertEqual(stock_vide.taille(), 2)


if __name__ == "__main__":
    unittest.main()
