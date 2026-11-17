import os
import secrets
from chiffrement_aes import chiffrer, mode_compteur

TAILLE_NONCE = 4
TAILLE_IV = 8

def cle_valide(cle):
    if len(cle) != 64:
        return False
    for caractere in cle:
        if caractere not in "0123456789abcdef":
            return False
    return True

def generer_cle():
    return secrets.token_hex(32)

def sauvegarder_cle(cle, chemin):
    with open(chemin, "w") as f:
        f.write(cle)

def lire_cle(saisie):
    saisie = saisie.strip().strip('"')
    if os.path.isfile(saisie):
        with open(saisie, "r") as f:
            cle = f.read().strip().lower()
    else:
        cle = saisie.lower()
    if not cle_valide(cle):
        return None
    return cle


def octets_vers_hexa(octets):
    return octets.hex()

def hexa_vers_octets(texte):
    return bytes.fromhex(texte)

def chiffrer_fichier(chemin_entree, chemin_sortie, cle):
    with open(chemin_entree, "rb") as f:
        contenu = f.read()

    nonce = secrets.token_hex(TAILLE_NONCE)
    iv = secrets.token_hex(TAILLE_IV)

    if len(contenu) == 0:
        chiffre = ""
    else:
        chiffre = mode_compteur(octets_vers_hexa(contenu), cle, iv, nonce)

    with open(chemin_sortie, "wb") as f:
        f.write(hexa_vers_octets(nonce + iv))
        f.write(hexa_vers_octets(chiffre))

def dechiffrer_fichier(chemin_entree, chemin_sortie, cle):
    with open(chemin_entree, "rb") as f:
        contenu = f.read()

    taille_entete = TAILLE_NONCE + TAILLE_IV
    if len(contenu) < taille_entete:
        raise ValueError("ce fichier est trop petit pour être un fichier chiffré")

    nonce = octets_vers_hexa(contenu[:TAILLE_NONCE])
    iv = octets_vers_hexa(contenu[TAILLE_NONCE:taille_entete])
    chiffre = contenu[taille_entete:]

    if len(chiffre) == 0:
        clair = ""
    else:
        clair = mode_compteur(octets_vers_hexa(chiffre), cle, iv, nonce)

    with open(chemin_sortie, "wb") as f:
        f.write(hexa_vers_octets(clair))

def demander_cle():
    saisie = input("Clé (chemin d'un fichier .cle ou 64 caractères hexa) : ")
    cle = lire_cle(saisie)
    if cle is None:
        print("Clé invalide : il faut 64 caractères hexa (0-9, a-f).")
    return cle

def demander_fichier():
    chemin = input("Fichier : ").strip().strip('"')
    if not os.path.isfile(chemin):
        print("Ce fichier n'existe pas.")
        return None
    return chemin

def menu():
    while True:
        print()
        print("===== AES-256 =====")
        print("1. Générer une clé")
        print("2. Chiffrer un fichier")
        print("3. Déchiffrer un fichier")
        print("5. Quitter")
        choix = input("Choix : ").strip()

        if choix == "1":
            cle = generer_cle()
            chemin = input("Nom du fichier pour la clé (ex : ma_cle.cle) : ").strip() or "ma_cle.cle"
            sauvegarder_cle(cle, chemin)
            print("Clé sauvegardée dans", chemin)
            print("Garde-la bien : sans elle, impossible de déchiffrer.")

        elif choix == "2":
            chemin = demander_fichier()
            if chemin is None:
                continue
            cle = demander_cle()
            if cle is None:
                continue
            sortie = chemin + ".aes"
            print("Chiffrement en cours...")
            chiffrer_fichier(chemin, sortie, cle)
            print("Fichier chiffré :", sortie)

        elif choix == "3":
            chemin = demander_fichier()
            if chemin is None:
                continue
            cle = demander_cle()
            if cle is None:
                continue
            if chemin.endswith(".aes"):
                base, extension = os.path.splitext(chemin[:-4])
                sortie = base + "_dechiffre" + extension
            else:
                sortie = chemin + ".dechiffre"
            print("Déchiffrement en cours...")
            try:
                dechiffrer_fichier(chemin, sortie, cle)
                print("Fichier déchiffré :", sortie)
            except ValueError as erreur:
                print("Erreur :", erreur)

        elif choix == "5":
            print("Au revoir !")
            break

        else:
            print("Choix invalide, tape un nombre entre 1 et 5.")


if __name__ == "__main__":
    menu()
