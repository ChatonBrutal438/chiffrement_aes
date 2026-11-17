# AES-256 recodé en Python

Projet de mathématiques : implémentation à la main de l'algorithme de chiffrement **AES-256** (norme **FIPS-197** du NIST), sans bibliothèque de cryptographie, avec un menu pour chiffrer et déchiffrer des fichiers.

---

## Sommaire

1. [Fichiers du projet](#1-fichiers-du-projet)
2. [Utilisation](#2-utilisation)
3. [Principe général d'AES](#3-principe-général-daes)
4. [Les mathématiques : le corps fini GF(2⁸)](#4-les-mathématiques--le-corps-fini-gf2⁸)
5. [Les 4 étapes d'un tour](#5-les-4-étapes-dun-tour)
6. [L'expansion de clé](#6-lexpansion-de-clé)
7. [Le mode compteur (chiffrer des fichiers)](#7-le-mode-compteur-chiffrer-des-fichiers)
8. [Confusion et diffusion](#8-confusion-et-diffusion)
9. [Correspondance code ↔ notions mathématiques](#9-correspondance-code--notions-mathématiques)
10. [Tests](#10-tests)
11. [Limites](#11-limites)
12. [Références](#12-références)

---

## 1. Fichiers du projet

| Fichier | Contenu |
|---|---|
| `aes256.py` | L'algorithme AES-256 : calculs dans GF(2⁸), les 4 étapes, l'expansion de clé, le chiffrement, le déchiffrement et le mode compteur |
| `main.py` | Le menu pour générer une clé et chiffrer ou déchiffrer des fichiers |
| `README.md` | Ce document |

## 2. Utilisation

Il faut **Python 3** (aucune bibliothèque à installer).

```bash
python main.py
```

```
===== AES-256 =====
1. Générer une clé
2. Chiffrer un fichier
3. Déchiffrer un fichier
4. Tester avec l'exemple officiel (FIPS-197)
5. Quitter
```

- **1. Générer une clé** : tire 32 octets au hasard et les enregistre dans un fichier (par exemple `ma_cle.cle`).
- **2. Chiffrer un fichier** : demande le fichier et la clé (le chemin du fichier `.cle` ou les 64 caractères hexa collés). Le résultat est `nom_du_fichier.aes`.
- **3. Déchiffrer un fichier** : à partir de `photo.jpg.aes`, crée `photo_dechiffre.jpg`.
- **4. Tester** : chiffre l'exemple officiel de la norme et vérifie le résultat.

**Format d'un fichier `.aes` :**

| Octets | Contenu |
|---|---|
| 0 à 3 | NONCE (aléatoire) |
| 4 à 11 | IV (aléatoire) |
| 12 à la fin | Le contenu chiffré (même taille que le fichier d'origine) |

---

## 3. Principe général d'AES

AES est un **chiffrement par blocs symétrique** :
- **symétrique** : la même clé sert à chiffrer et à déchiffrer ;
- **par blocs** : on chiffre des blocs de **128 bits** (16 octets).

Le « 256 » d'AES-256 est la **taille de la clé** : 256 bits = 32 octets.

| | AES-128 | AES-192 | **AES-256** |
|---|---|---|---|
| Taille de la clé | 16 octets | 24 octets | **32 octets** |
| Nk (mots de clé) | 4 | 6 | **8** |
| Nr (nombre de tours) | 10 | 12 | **14** |

**L'état** : les 16 octets du bloc sont rangés dans une matrice 4×4, **colonne par colonne**. Dans le code, `etat[colonne][ligne]`.

```
octets : 00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff

état :   00 44 88 cc
         11 55 99 dd
         22 66 aa ee
         33 77 bb ff
```

**Déroulement du chiffrement :**

```
AddRoundKey (clé 0)
Tours 1 à 13 : SubBytes → ShiftRows → MixColumns → AddRoundKey
Tour 14      : SubBytes → ShiftRows → AddRoundKey      (pas de MixColumns)
```

Le **déchiffrement** applique les opérations inverses dans l'ordre inverse.

---

## 4. Les mathématiques : le corps fini GF(2⁸)

Tous les calculs d'AES se font dans un **corps fini** à 256 éléments.

### 4.1 Le corps 𝔽₂ = {0, 1}

On calcule **modulo 2** : 0 + 0 = 0, 0 + 1 = 1 et **1 + 1 = 0**.
Cette addition est exactement le **XOR** (`^` en Python).

On dit que 𝔽₂ est **de caractéristique 2** : pour tout a, a + a = 0.

### 4.2 Un octet = un polynôme

Chaque bit d'un octet est un coefficient d'un polynôme de **𝔽₂[x]** (polynômes à coefficients dans 𝔽₂) :

```
0x57 = 0101 0111  ↦  x⁶ + x⁴ + x² + x + 1
```

### 4.3 Le polynôme irréductible

```
m(x) = x⁸ + x⁴ + x³ + x + 1      (0x11B)
```

m(x) est **irréductible** : on ne peut pas l'écrire comme produit de deux polynômes de degré plus petit. C'est l'équivalent d'un **nombre premier** pour les polynômes.

### 4.4 Le corps de Galois GF(2⁸)

On calcule avec les polynômes **modulo m(x)**, c'est-à-dire qu'on garde le **reste de la division euclidienne** par m(x) :

```
GF(2⁸) = 𝔽₂[x] / (m(x))      (anneau quotient)
```

**Théorème :** si m(x) est irréductible, l'anneau quotient 𝔽₂[x]/(m(x)) est un **corps**. Tout élément non nul y a donc un **inverse**.

> Analogie : ℤ/7ℤ (les entiers modulo 7). Comme 7 est premier, chaque entier non nul a un inverse modulo 7.

GF(2⁸) contient **2⁸ = 256 éléments**, exactement autant que de valeurs possibles pour un octet.

### 4.5 L'addition = XOR

On additionne les polynômes terme à terme, avec les coefficients modulo 2 :

```
  0x57 = 0101 0111     x⁶ + x⁴ + x² + x + 1
+ 0x83 = 1000 0011     x⁷ + x + 1
= 0xD4 = 1101 0100     x⁷ + x⁶ + x⁴ + x²
```

- (GF(2⁸), +) est un **groupe abélien**.
- Chaque élément est **son propre opposé** : a + a = 0, donc **soustraire = additionner**.

### 4.6 La multiplication par x (fonction `multiplier_par_2`)

Multiplier par x (c'est-à-dire par `0x02`) **décale** les coefficients d'un degré (`<< 1`).
Si le bit de poids fort valait 1, un terme en x⁸ apparaît et il faut le **réduire modulo m(x)**. Comme m(x) = 0 dans le corps :

```
x⁸ = x⁴ + x³ + x + 1 = 0001 1011 = 0x1B
```

(le signe − disparaît, car −1 = 1 dans 𝔽₂). On fait donc un **XOR avec `0x1B`**.

**Exemples :**

```
0x57 × 2 : 0101 0111 → 1010 1110 = 0xAE                (bit de poids fort = 0, pas de réduction)
0xAE × 2 : 1010 1110 → 0101 1100 = 0x5C, puis ⊕ 0x1B = 0x47   (bit de poids fort = 1, réduction)
```

Le paramètre `n` de la fonction répète l'opération : `n=2` → ×4, `n=3` → ×8.

### 4.7 La multiplication générale

**Exemple de la norme :** `0x57 × 0x83`

```
(x⁶ + x⁴ + x² + x + 1)(x⁷ + x + 1)
  = x¹³ + x¹¹ + x⁹ + x⁸ + x⁶ + x⁵ + x⁴ + x³ + 1

reste de la division par m(x) : x⁷ + x⁶ + 1 = 0xC1
```

**Méthode de calcul :** on décompose le deuxième nombre en puissances de 2 (méthode **« double-and-add »**, ou **multiplication russe**) :

```
a × 0x0b = a × (8 + 2 + 1) = a×8 ⊕ a×2 ⊕ a
```

### 4.8 L'inverse multiplicatif

Pour tout a ≠ 0, il existe un unique b tel que a × b = 1. Exemple : `0x53 × 0xCA = 0x01`.

Deux méthodes pour le calculer :
- **l'algorithme d'Euclide étendu**, qui donne une **identité de Bézout** a·u + m·v = 1, d'où a⁻¹ = u ;
- **le théorème de Lagrange** : le **groupe multiplicatif** GF(2⁸)* a 255 éléments, donc a²⁵⁵ = 1 et **a⁻¹ = a²⁵⁴**.

GF(2⁸)* est un **groupe cyclique** : `0x03` en est un **générateur**.

---

## 5. Les 4 étapes d'un tour

### 5.1 SubBytes (`substituer_octets`) : la S-box

Chaque octet a est remplacé par :

```
S(a) = A · a⁻¹ ⊕ c
```

- a⁻¹ est l'**inverse dans GF(2⁸)** (0 est envoyé sur 0) ;
- A est une **matrice 8×8 à coefficients dans 𝔽₂** ;
- c = `0x63`.

Bit par bit (indices modulo 8) :

```
b'ᵢ = bᵢ ⊕ bᵢ₊₄ ⊕ bᵢ₊₅ ⊕ bᵢ₊₆ ⊕ bᵢ₊₇ ⊕ cᵢ
```

- **Notions :** inversion dans un corps fini, **transformation affine** sur l'espace vectoriel 𝔽₂⁸, **bijection** (S est une permutation des 256 octets).
- **Exemple :** `0x53` → inverse `0xCA` → transformation affine → **`0xED`**.
- **Rôle :** c'est la **seule étape non linéaire** d'AES. Sans elle, tout AES serait un système d'équations linéaires, facile à résoudre.

Dans le code, les 256 valeurs sont précalculées dans la table `Sbox`, et la réciproque est dans `Sbox_inverse`.

### 5.2 ShiftRows (`decaler_lignes`) : une permutation

La ligne i tourne de **i cases vers la gauche** :

```
a0 a1 a2 a3        a0 a1 a2 a3     (ligne 0 : ne bouge pas)
b0 b1 b2 b3   →    b1 b2 b3 b0     (ligne 1 : 1 case)
c0 c1 c2 c3        c2 c3 c0 c1     (ligne 2 : 2 cases)
d0 d1 d2 d3        d3 d0 d1 d2     (ligne 3 : 3 cases)
```

- **Notion :** **permutation** des 16 positions. Sa réciproque (`decaler_lignes_inverse`) fait tourner vers la droite.

### 5.3 MixColumns (`melanger_colonnes`) : un produit matrice × vecteur

Chaque colonne est multipliée par une matrice fixe, dans GF(2⁸) :

```
| s0' |   | 02 03 01 01 |   | s0 |
| s1' | = | 01 02 03 01 | × | s1 |
| s2' |   | 01 01 02 03 |   | s2 |
| s3' |   | 03 01 01 02 |   | s3 |
```

On peut aussi voir la colonne comme un polynôme à coefficients dans GF(2⁸), s(x) = s₃x³ + s₂x² + s₁x + s₀, qu'on multiplie par a(x) = 03x³ + 01x² + 01x + 02 **modulo x⁴ + 1**.
Comme x⁴ ≡ 1, multiplier par x fait **tourner** les coefficients : c'est pour ça que chaque ligne de la matrice est la précédente décalée d'une case. On parle de **matrice circulante**.

**L'astuce du code** (pour éviter de calculer les ×3, avec 3·a = 2·a ⊕ a) :

```
s0' = s0 ⊕ somme ⊕ 2·(s0 ⊕ s1)            où somme = s0 ⊕ s1 ⊕ s2 ⊕ s3
    = s0 ⊕ s0 ⊕ s1 ⊕ s2 ⊕ s3 ⊕ 2·s0 ⊕ 2·s1
    = 2·s0 ⊕ (2·s1 ⊕ s1) ⊕ s2 ⊕ s3          car s0 ⊕ s0 = 0
    = 2·s0 ⊕ 3·s1 ⊕ s2 ⊕ s3                 ✓ première ligne de la matrice
```

**Exemple avec la colonne `db 13 53 45`** :

```
2·db = b6 ⊕ 1b = ad
3·13 = 2·13 ⊕ 13 = 26 ⊕ 13 = 35
s0'  = ad ⊕ 35 ⊕ 53 ⊕ 45 = 8e
```

Résultat complet : `db 13 53 45` → **`8e 4d a1 bc`**.

- **Notions :** **application linéaire**, **matrice circulante**, anneau quotient GF(2⁸)[x]/(x⁴ + 1). La matrice est **MDS** (*Maximum Distance Separable*) : si on change un seul octet d'entrée, les 4 octets de sortie changent.

**L'inverse (`melanger_colonnes_inverse`)** : la matrice inverse est

```
0e 0b 0d 09
09 0e 0b 0d
0d 09 0e 0b
0b 0d 09 0e
```

Le code utilise une **factorisation** : a⁻¹(x) = a(x) · (04x² + 05). On applique d'abord la matrice `05 00 04 00`, qui ne demande que des ×4 :

```
u = 4·(s0 ⊕ s2)      v = 4·(s1 ⊕ s3)
s0 ⊕= u   s1 ⊕= v   s2 ⊕= u   s3 ⊕= v
```

puis un MixColumns normal.

### 5.4 AddRoundKey (`ajouter_cle_de_tour`) : une addition

```
état ← état ⊕ clé_de_tour
```

- **Notions :** **translation** dans l'espace vectoriel 𝔽₂¹²⁸. C'est une **involution** : (a ⊕ k) ⊕ k = a. La même fonction sert donc pour chiffrer et pour déchiffrer.
- C'est la seule étape qui utilise la clé.

---

## 6. L'expansion de clé (`expansion_cle`)

La clé de 32 octets = **8 mots** de 4 octets doit fournir **15 clés de tour** (une initiale + 14 tours), soit **4 × 15 = 60 mots**.

Les 8 premiers mots sont la clé elle-même. Ensuite, pour i de 8 à 59 :

```
temp = w[i−1]
si i mod 8 = 0 :  temp = SubWord(RotWord(temp)) ⊕ Rcon[i/8]
si i mod 8 = 4 :  temp = SubWord(temp)                      ← spécifique à AES-256
w[i] = w[i−8] ⊕ temp
```

- `RotWord` (`rotation`) : [a, b, c, d] → [b, c, d, a]
- `SubWord` (`substituer_mot`) : la S-box sur chaque octet
- **Rcon[i] = xⁱ⁻¹** dans GF(2⁸) : `01 02 04 08 10 20 40 80`, puis `0x80 × 2 = 0x1B` (même réduction qu'en 4.6)

- **Notions :** **suite définie par récurrence**, **puissances d'un élément** dans un corps fini.

---

## 7. Le mode compteur (chiffrer des fichiers)

AES ne chiffre que des blocs de 16 octets. Pour un fichier de taille quelconque, on utilise le **mode compteur (CTR)** :

```
bloc de compteur n° i = NONCE ‖ IV ‖ i         (4 + 8 + 4 octets = 16 octets)
flux de clé Kᵢ        = AES(bloc de compteur n° i)
chiffré               = clair ⊕ K₁ K₂ K₃ ...
```

- **Déchiffrer = refaire exactement le même calcul**, car (m ⊕ K) ⊕ K = m.
- Le dernier bloc peut être plus court : on coupe le flux de clé à la bonne longueur. Le fichier chiffré a donc **la même taille** que l'original (plus les 12 octets d'en-tête).
- **NONCE et IV sont tirés au hasard** à chaque chiffrement : il ne faut **jamais** réutiliser le même compteur avec la même clé. Sinon, C₁ ⊕ C₂ = M₁ ⊕ M₂, et l'attaquant obtient le XOR des deux messages.

- **Notion :** c'est le principe du **masque jetable** (**chiffre de Vernam**), où le masque est fabriqué par AES.

---

## 8. Confusion et diffusion

Les deux principes de **Claude Shannon** (1949) pour un bon chiffrement :

| Principe | Définition | Étape d'AES | Outil mathématique |
|---|---|---|---|
| **Confusion** | rendre le lien entre la clé et le chiffré le plus compliqué possible | SubBytes | inversion dans GF(2⁸) (non linéaire) |
| **Diffusion** | qu'un bit du message influence tout le bloc | ShiftRows + MixColumns | permutation + matrice MDS (linéaire) |

Après 2 tours, chaque octet de sortie dépend de **tous** les octets d'entrée.

---

## 9. Correspondance code ↔ notions mathématiques

| Fonction (`aes256.py`) | Nom officiel FIPS-197 | Notion mathématique |
|---|---|---|
| `^` | addition | addition dans 𝔽₂ / GF(2⁸), XOR |
| `multiplier_par_2` | `xtime` | multiplication par x modulo m(x) |
| `substituer_octets` | SubBytes | inverse dans GF(2⁸) + transformation affine |
| `decaler_lignes` | ShiftRows | permutation |
| `melanger_colonnes` | MixColumns | application linéaire, matrice circulante |
| `ajouter_cle_de_tour` | AddRoundKey | translation, involution |
| `expansion_cle` | KeyExpansion | suite récurrente, puissances de x |
| `rotation` | RotWord | permutation circulaire |
| `substituer_mot` | SubWord | S-box sur 4 octets |
| `chiffrer` / `dechiffrer` | Cipher / InvCipher | composition de bijections |
| `mode_compteur` | CTR (NIST SP 800-38A) | masque jetable |

---

## 10. Tests

Le programme a été vérifié avec les exemples officiels :

| Test | Entrée | Résultat attendu | Obtenu |
|---|---|---|---|
| Multiplication par 2 | `0x57 × 2` | `0xAE` | ✅ |
| MixColumns | `db 13 53 45` | `8e 4d a1 bc` | ✅ |
| MixColumns inverse | `8e 4d a1 bc` | `db 13 53 45` | ✅ |
| **AES-256 (FIPS-197, annexe C.3)** | clé `000102…1e1f`, texte `00112233445566778899aabbccddeeff` | `8ea2b7ca516745bfeafc49904b496089` | ✅ |
| Déchiffrement C.3 | `8ea2b7ca…` | `00112233…eeff` | ✅ |
| Fichiers (vide, 16, 17 octets, 100 Ko) | chiffrer puis déchiffrer | fichier identique | ✅ |

Le test C.3 peut être relancé avec l'option **4** du menu.

---

## 11. Limites

Ce projet est **pédagogique**. Il ne doit pas servir à protéger de vraies données :

- **Lenteur** : Python pur, et l'expansion de clé est recalculée pour chaque bloc. Il faut environ **10 secondes pour 100 Ko**.
- **Pas d'authentification** : si quelqu'un modifie le fichier chiffré, le déchiffrement donne un résultat faux sans le signaler. Avec une mauvaise clé, on obtient aussi des données incompréhensibles, sans message d'erreur. En pratique, on utilise **AES-GCM**, qui ajoute un code d'authentification.
- **Attaques par canaux auxiliaires** : les accès aux tables (S-box) ne se font pas en temps constant.
- **La clé est stockée en clair** dans le fichier `.cle` : il faut la garder en lieu sûr.

---

## 12. Références

- NIST, **FIPS-197** : *Advanced Encryption Standard (AES)*, 2001 (mise à jour 2023). Contient la définition complète et les exemples des annexes C.
- NIST, **SP 800-38A** : *Recommendation for Block Cipher Modes of Operation*. Définit le mode compteur (CTR).
- J. Daemen et V. Rijmen, ***The Design of Rijndael***, Springer, 2002. Écrit par les auteurs d'AES.
- C. Shannon, *Communication Theory of Secrecy Systems*, 1949. Introduit la confusion et la diffusion.
