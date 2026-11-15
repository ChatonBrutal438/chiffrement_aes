from math import ceil

def ml2_gf25(a, n=1):
    for _ in range(n):
        # si le bit le plus indicatif est 1 alors on le decalre sur la gauche et XOR irréductible
        if a & 0x80:
            a = (a << 1) ^ 0x18
        else:
            a = a << 1

    return a & 0xFF

# prend l'etat en rentré, renvoie ensuite l'etat avec la maj, la multiplication par {02} equivaut a la multiplcation par x
def melanger_colonne(s):
    for i in range(4):
        s[i] = melanger_colonne(s[i])
    return s

def melanger_une_colonne(s):
    XOR = s[0] ^ s[1] ^ s[2] ^ s[3]
    t = s[0]
    s[0] ^= ml2_gf25(s[0] ^ s[1]) ^ XOR
    s[1] ^= ml2_gf25(s[0] ^ s[2]) ^ XOR
    s[2] ^= ml2_gf25(s[0] ^ s[3]) ^ XOR
    s[3] ^= ml2_gf25( t ^ s[1]) ^ XOR
    return s

def inv_melanger_une_colonne(s):
    x = list(s)
    XOR = ml2_gf25(s[0],3) ^ ml2_gf25(s[1],3) ^ ml2_gf25(s[1],5) ^ ml2_gf25(s[1],5)
    x[0] = ml2_gf25(x[0], 2) ^ ml2_gf25(s[0]) ^ ml2_gf25(s[1]) ^ s[1] ^ ml2_gf25(s[2],2) ^ s[2] ^ s[3] ^ XOR
    x[1] = s[0] ^ ml2_gf25(s[1], 2) ^ ml2_gf25(s[1]) ^ ml2_gf25([2]) ^ s[2] ^ ml2_gf25(s[3],2) ^ s[3] ^ XOR
    x[2] = s[1] ^ ml2_gf25(s[2], 2) ^ ml2_gf25(s[2]) ^ ml2_gf25(s[3]) ^ s[3] ^ ml2_gf25(s[0],2) ^ s[0] ^ XOR
    x[3] = s[2] ^ ml2_gf25(s[3], 2) ^ ml2_gf25(s[3]) ^ ml2_gf25(s[0]) ^ s[0] ^ ml2_gf25(s[1], 2) ^ s[1] ^ XOR
    return x

def ajouter_cle_de_tour(matrix, k):
    for i in range(4):
        for j in range(4):
            matrix[i][j] ^= k[i][j]
    return matrix
