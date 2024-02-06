## Numéro d'équipe : 
## Bouh Abdillahi (Matricule : 1940646)
## Vincent Yves Nodjom (Matricule : 1944011)
## Équipe : 7
## Github link : https://github.com/konoDioDA253/ELE8702-H24-Lab0

import sys
import math
import yaml
import random
import os
import argparse

# Variables GLOBAL
# Numero propres a l'équipe
numero_equipe = '7'
numero_lab = '0'


# Germe de toutes les fonctions aléatoires
random.seed(123)

class Antenna:

     def __init__(self, id):
        self.id = id          #id de l'antenne (int)
        self.frequency = None # Antenna frequency in GHz
        self.height = None    # Antenna height
        self.group = None     # group défini dans la base de données (str)
        self.coords = None    # tuple contenant les coordonnées (x,y) 
        self.assoc_ues = []   # liste avec les id des UEs associés à l'antenne
        self.scenario = None  # pathloss scénario tel que lu du fichier de cas (str)
        self.gen = None       # type de géneration de coordonnées: 'g', 'a', etc. (str)

    
    
class UE:

     def __init__(self, id, app_name):
        self.id= id           # id de l'UE (int)
        self.height = None    # UE height
        self.group = None     # group défini dans la base de données (str)
        self.coords=None      # tuple contenant les coordonnées (x,y) 
        self.app=app_name     # nom de l'application qui tourne dans le UE (str)
        self.assoc_ant=None   # id de l'antenne associée à l'UE (int)
        self.los = True       # LoS ou non (bool)
        self.gen = None       # type de géneration de coordonnées: 'g', 'a', etc. (str)
        # Attribut rajoutee par notre equipe
        self.apptype = None # Pas besoin car tirer de la chaine de caractere de group

def ERROR(msg , code = 1):
    print("\n\n\nERROR\nPROGRAM STOPPED!!!\n")
    if msg:
        print(msg)
    print(f"\n\texit code = {code}\n\n\t\n")
    sys.exit(code)


def fill_up_the_lattice(N, lh, lv, nh, nv):
    """Function appelée par get_rectangle_lattice_coords()"""
    
    def get_delta1d(L, n):
        return L/(n + 1)
    
    coords = []
    deltav = get_delta1d(lv, nv)
    deltah = get_delta1d(lh, nh)
    line = 1
    y = deltav
    count = 0
    while count < N:
        if count + nh < N:
            x = deltah
            for  i in range(nh):
                # Fill up the horizontal line
                coords.append((x,y))
                x = x + deltah
                count += 1
            line += 1
        else:
            deltah = get_delta1d(lh, N - count)
            x = deltah
            for i in range(N - count):
                # Fill up the last horizontal line
                coords.append((x,y))
                x = x + deltah
                count += 1
            line += 1
        y = y +deltav
    return coords

def get_rectangle_lattice_coords(lh, lv, N, Np, nh, nv):
    """Function appelee par gen_lattice_coords()"""
    
    if Np > N:
        coords = fill_up_the_lattice(N, lh, lv, nh, nv)
    elif Np < N:
        coords = fill_up_the_lattice(N, lh, lv, nh, nv + 1)
    else:
        coords = fill_up_the_lattice(N, lh, lv, nh, nv)
    return coords

def gen_lattice_coords(terrain_shape: dict, N: int):
    """Génère un ensemble de N coordonnées placées en grille 
       sur un terrain rectangulaire
    
       Args: terrain_shape: dictionary {'rectangle': {'length' : lh,
                                                   'height' : lv}
           lh and lv are given in the case file"""
    #CETTE FONCION EST OBLIGATOIRE POUR L'OPTION GRILLE (g) DU FICHIER DE CAS

    shape = list(terrain_shape.keys())[0]
    lh = terrain_shape[shape]['length']
    lv = terrain_shape[shape]['height']
    R = lv / lh    
    nv = round(math.sqrt(N / R))
    nh = round(R * nv)
    Np = nh * nv
    if shape.lower() == 'rectangle':
        coords = get_rectangle_lattice_coords(lh, lv, N, Np, nh, nv)
    else:
        msg = [f"\tImproper shape ({shape}) used in the\n",
                "\tgeneration of lattice coordinates.\n"
                "\tValid values: ['rectangle']"]
        ERROR(''.join(msg), 2)
    return coords        

def get_from_dict(key, data, res=None, curr_level = 1, min_level = 1):
    """Fonction qui retourne la valeur de n'importe quel clé du dictionnaire
       key: clé associé à la valeur recherchée
       data: dictionnaire dans lequel il faut chercher
       les autres sont des paramètres par défaut qu'il ne faut pas toucher"""
    if res:
        return res
    if type(data) is not dict:
        msg = f"get_from_dict() works with dicts and is receiving a {type(data)}"
        ERROR(msg, 1)
    else:
        # data IS a dictionary
        for k, v in data.items():
            if k == key and curr_level >= min_level:
                #print(f"return data[k] = {data[k]} k = {k}")
                return data[k]
            if type(v) is dict:
                level = curr_level + 1
                res = get_from_dict(key, v, res, level, min_level)
    return res 

def read_yaml_file(fname):
    # Fonction utilisée pour lire les fichiers de type .yaml
    # fname: nom du fichier .yaml à lire
    # le retour de la fonction est un dictionnaire avec toute l'information qui se trouve
    # dans le fichier .yaml
    # Si vous préférez vous pouvez utiliser une autre fonction pour lires les fichiers
    # de type .yaml.
    # À noter que dans cette fonction il faut ajouter les vérifications qui s'imposent
    # par exemple, l'existance du fichier
    
    # Vérifier l'existence du fichier
    if not os.path.exists(fname):
        raise FileNotFoundError(f"Le fichier {fname} n'existe pas.")

    # Ouvrir et lire le fichier YAML
    with open(fname, 'r') as file:
        return yaml.safe_load(file)

# Fonction attribuant des coordonnées aléatoires
# Prends en paramètre le fichier de cas pour avoir la longueur et la largeur du terrain    
def gen_random_coords(fichier_de_cas):
    # Cette fonction doit générer les coordonées pour le cas de positionnement aléatoire
    # TODO PRESENTABLE
    longueur_geometry = fichier_de_cas['ETUDE_PATHLOSS']['GEOMETRY']['Surface']['rectangle']['length']
    hauteur_geometry = fichier_de_cas['ETUDE_PATHLOSS']['GEOMETRY']['Surface']['rectangle']['height']
    

    x_aleatoire = random.uniform(1, longueur_geometry)
    y_aleatoire = random.uniform(1, hauteur_geometry)
    coordonnees_aleatoires = [x_aleatoire, y_aleatoire]
    return coordonnees_aleatoires

# fonction initialisant une liste de ues et assignant des coordonnées aléatoirement à chaque ue dans la liste
def assigner_coordonnees_ues(fichier_de_cas):
    liste_ues_avec_coordonnees = []

    nombre_ues_ue1 = fichier_de_cas['ETUDE_PATHLOSS']['DEVICES']['UE1-App1']['number']
    nombre_ues_ue2 = fichier_de_cas['ETUDE_PATHLOSS']['DEVICES']['UE2-App2']['number']
    type_de_generation = fichier_de_cas['ETUDE_PATHLOSS']['UE_COORD_GEN']

    for i in range(nombre_ues_ue1):
        ue = UE(id=len(liste_ues_avec_coordonnees), app_name='UE1-App1')
        if (type_de_generation == 'a') :
            coords = gen_random_coords(fichier_de_cas)
        ue.gen = type_de_generation
        ue.coords = coords
        ue.apptype = "app1"
        liste_ues_avec_coordonnees.append(ue)

    for i in range(nombre_ues_ue2):
        ue = UE(id=len(liste_ues_avec_coordonnees), app_name='UE2-App2')
        if (type_de_generation == 'a') :
            coords = gen_random_coords(fichier_de_cas)
        ue.gen = type_de_generation
        ue.coords = coords
        ue.apptype = "app2"
        liste_ues_avec_coordonnees.append(ue)

    return liste_ues_avec_coordonnees

# fonction initialisant une liste de antennes et assignant des coordonnées selon la grille à chaque antenne
def assigner_coordonnees_antennes(fichier_de_cas):
    liste_antennes_avec_coordonnees = []

    nombre_antennes = fichier_de_cas['ETUDE_PATHLOSS']['DEVICES']['Antenna1']['number']
    type_de_generation = fichier_de_cas['ETUDE_PATHLOSS']['ANT_COORD_GEN']
    
    terrain_shape =  fichier_de_cas['ETUDE_PATHLOSS']['GEOMETRY']['Surface']
    coords = gen_lattice_coords(terrain_shape, nombre_antennes)

    for id, coord in enumerate(coords):
        antenna = Antenna(id)
        antenna.coords = coord
        antenna.gen = type_de_generation
        antenna.group = "Antenna1"
        liste_antennes_avec_coordonnees.append(antenna)

    return liste_antennes_avec_coordonnees

# fonction qui ecrit les information par rapport aux antennes et au UEs
def write_to_file(antennas, ues, fichier_de_cas):

    with open(fichier_de_cas['ETUDE_PATHLOSS']['COORD_FILES']['write'], 'w') as file:
        for antenna in antennas:
            line = f"antenna\t{antenna.id}\t{antenna.group}\t{antenna.coords[0]}\t{antenna.coords[1]}\n"
            file.write(line)

        for ue in ues:
            line = f"ue\t{ue.id}\t{ue.app}\t{ue.coords[0]}\t{ue.coords[1]}\t{ue.apptype}\n"
            file.write(line)










    
# def okumura (argument1, argument2, ...):
#     #TODO ....
#     # C'est à vous décider le nombre et type d'arguments utilisés pour
#     #faire le calcul de pathloss avec le modèle d'Okumura-Hata
#     # CETTE FONCTION EST OBLIGATOIRE
#     return pathloss

def lab1 (data_case):
    #TODO ....
    # antennas est une liste qui contient les objets de type Antenna
    # ues est une liste qui contient les objets de type UE
    #
    # antennas = [ant0,ant1,...] 
    #            ant1, ant2 etc sont des instances (objets) de la classe Antenna
    # ues = [ue0, ue1,...] 
    #             ue0, ue1, etc sont des instances (objets) de la classe UE
    # avant de faire le retour, les objets appartenant aux listes antennas et ues 
    # doivent avoir leur coordonées initialisées
    # CETTE FONCTION EST OBLIGATOIRE
    fichier_de_cas = data_case
    ues = assigner_coordonnees_ues(fichier_de_cas)
    antennas = assigner_coordonnees_antennes(fichier_de_cas)
    return (antennas,ues)

# def treat_cli_args(arg):
#     # arg est une liste qui contient les arguments utilisés lors de l'appel du programme par CLI. 
#     # Cette fonction doit retourner le nom du fichier de cas à partir de l'interface de commande (CLI)
#     #... 
#     # TODO
#     #....
#     # CETTE FONCTION EST OBLIGATOIRE
#     # À noter que dans cette fonction il faut ajouter les vérifications qui s'imposent
#     # par exemple, nombre d'arguments appropriés, existance du fichier de cas, etc.
#     return case_file_name

def main(arg):
    # case_file_name = treat_cli_args(arg)
    case_file_name = "lab1_eq7_cas.yaml"
    data_case = read_yaml_file(case_file_name)
    fichier_de_cas = data_case
    antennas, ues = lab1(fichier_de_cas)
    write_to_file(antennas,ues,fichier_de_cas)
    #
    #TODO les instructions de main qui vont faire appel aux autres fonctions du programme
    #.....

if __name__ == '__main__':
    # sys.argv est une liste qui contient les arguments utilisés lors de l'appel 
    # du programme à partir du CLI. Cette liste est créée automatiquement par Python. Vous devez 
    # juste inscrire l'argument tel que montré ci-dessous.
    main(sys.argv[1:])