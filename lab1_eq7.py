## Numéro d'équipe : 
## Bouh Abdillahi (Matricule : 1940646)
## Vincent Yves Nodjom (Matricule : 1944011)
## Équipe : 7
## Github link : https://github.com/konoDioDA253/ELE8702-H24-Lab1
## Question 1 : À quoi sert l'attribut group de la classe ue, et quelle est la différence avec l'attribut app
## Question 2 : Est-ce correct d'utiliser group=app pour les ues?
## Question 3 : à quoi sert la fonction d'erreur?
## Question 4 : Notre  fichier de cas eat-il sensé supporter plus d'un model à la foi?
## Question 5 : Est-ce qu'on peut comparer avec la prof les valeurs du pathlosses?
import sys
import math
import yaml
import random
import os
import argparse

# Variables GLOBAL
# Numero propres a l'équipe
numero_equipe = '7'
numero_lab = '1'
# (PROF) Est-ce que c'est du Hard-wired? Comment le faire a travers le fichier de cas? 
coord_file_name = "lab"+numero_lab+"_eq"+numero_equipe+"_coords.txt"
pathloss_file_name = "lab"+numero_lab+"_eq"+numero_equipe+"_pl.txt"
assoc_ues_file_name = "lab"+numero_lab+"_eq"+numero_equipe+"_assoc_ue.txt"
assoc_antennas_file_name = "lab"+numero_lab+"_eq"+numero_equipe+"_assoc_ant.txt"


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

class Pathloss:
     def __init__(self, id_ue, id_ant):
        self.id_ue = id_ue   # ID de l'ue
        self.id_ant = id_ant # ID de l'antenne
        self.value = None   # Valeur du pathloss



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
        # (PROF) Est-ce que group=app est correct pour ue?
        ue.group = ue.app
        ue.gen = type_de_generation
        ue.coords = coords
        ue.apptype = "app1"
        liste_ues_avec_coordonnees.append(ue)

    for i in range(nombre_ues_ue2):
        ue = UE(id=len(liste_ues_avec_coordonnees), app_name='UE2-App2')
        if (type_de_generation == 'a') :
            coords = gen_random_coords(fichier_de_cas)
        # (PROF) Est-ce que group=app est correct pour ue?
        ue.group = ue.app
        ue.gen = type_de_generation
        ue.coords = coords
        ue.apptype = "app2"
        liste_ues_avec_coordonnees.append(ue)

    return liste_ues_avec_coordonnees

# fonction initialisant une liste de antennes et assignant des coordonnées selon la grille à chaque antenne
def assigner_coordonnees_antennes(fichier_de_cas):
    liste_antennes_avec_coordonnees = []
    terrain_shape =  fichier_de_cas['ETUDE_PATHLOSS']['GEOMETRY']['Surface']
    id_counter = 0  # Tenir à jour un compteur pour chaque type d'antenne

    # nombre_antennes = fichier_de_cas['ETUDE_PATHLOSS']['DEVICES']['Antenna1']['number']
    # type_de_generation = fichier_de_cas['ETUDE_PATHLOSS']['ANT_COORD_GEN']
    
    # coords = gen_lattice_coords(terrain_shape, nombre_antennes)

    devices = fichier_de_cas['ETUDE_PATHLOSS']['DEVICES']
    for antenna_group, antenna_info in devices.items():
        if antenna_group.startswith('Antenna'):
            nombre_antennes = antenna_info['number']
            type_de_generation = fichier_de_cas['ETUDE_PATHLOSS']['ANT_COORD_GEN']
            
            coords = gen_lattice_coords(terrain_shape, nombre_antennes)
            for id, coord in enumerate(coords, start=id_counter):
                antenna = Antenna(id)
                antenna.coords = coord
                antenna.gen = type_de_generation
                antenna.group = antenna_group
                liste_antennes_avec_coordonnees.append(antenna)

            # Mettre a jour le compteur pour ce type d'antenne
            id_counter += nombre_antennes

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
# Fonction qui écrire les un fichier la valeurs des pathlosses calculer l'id de l'ue et des antennes associés le senario utilisé et le model
def write_pathloss_to_file(pathlosses, fichier_de_cas):
    with open(pathloss_file_name, 'w') as file:
        for pathloss in pathlosses:
            line = f"{pathloss.id_ue}\t{pathloss.id_ant}\t{pathloss.value}\t{fichier_de_cas['ETUDE_PATHLOSS']['PATHLOSS']['model']}\t{fichier_de_cas['ETUDE_PATHLOSS']['PATHLOSS']['scenario']}\n"
            file.write(line)

## Fonction qui ecrire dans un fichier l'id de l'antenne et tous les id des eus associer
def write_assoc_ues_to_file(antennas, fichier_de_cas):
    with open(assoc_antennas_file_name, 'w') as file:
        for antenna in antennas:
            line = f"{antenna.id}"
            for ue in antenna.assoc_ues :
                line += f"\t{ue}"
            line += "\n"
            file.write(line)

# Fonction qui ecrit dans un fichier l'id de l'ue avec l'antenne associee
def write_assoc_ant_to_file(ues, fichier_de_cas):
    with open(assoc_ues_file_name, 'w') as file:
        for ue in ues:
            line = f"{ue.id}\t{ue.assoc_ant}\n"
            file.write(line)

# Fonction calculant la distance entre deux point sur le terrain
def calculate_distance(coord1, coord2):
    x1, y1 = coord1
    x2, y2 = coord2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Fonction donnant le group a partir du ID d'un objet dans une liste du meme objet
def get_group_and_coords_by_id(object_list, target_id):
    for object in object_list:
        if object.id == target_id:
            return object.group, object.coords
    return None  

def okumura(fichier_de_cas, fichier_de_device, antenna_id, ue_id, antennas, ues):
    #TODO ....
    # C'est à vous décider le nombre et type d'arguments utilisés pour
    #faire le calcul de pathloss avec le modèle d'Okumura-Hata
    # CETTE FONCTION EST OBLIGATOIRE
    model = fichier_de_cas['ETUDE_PATHLOSS']['PATHLOSS']['model']
    scenario = fichier_de_cas['ETUDE_PATHLOSS']['PATHLOSS']['scenario']
    if model == "okumura" and scenario == "urban_small":
        # Model okumura scenario urbain petites villes
        antenna_group, antenna_coords = get_group_and_coords_by_id(antennas, antenna_id)
        ue_group, ue_coords = get_group_and_coords_by_id(ues, ue_id)
        fc = fichier_de_device['ANTENNAS'][antenna_group]['frequency']
        ht = fichier_de_device['ANTENNAS'][antenna_group]['height']
        hr = fichier_de_device['UES'][ue_group]['height']
        distance = calculate_distance(antenna_coords, ue_coords)
        # (PROF) est-ce que les chiffres dans les formules en dB doivent etre converti (exemple avec le 0.8 ici)?
        A = (1.1*math.log10(fc) - 0.7)*hr - 1.56*math.log10(fc) - 0.8
        pathloss = 69.55 + 26.16*math.log10(fc) - 13.82*math.log10(ht) - A + (44.9 - 6.55*math.log10(ht))*math.log10(distance)
        return pathloss
    if model == "okumura" and scenario == "urban_large":
        # Model okumura scenario urbain grande villes
        antenna_group, antenna_coords = get_group_and_coords_by_id(antennas, antenna_id)
        ue_group, ue_coords = get_group_and_coords_by_id(ues, ue_id)
        fc = fichier_de_device['ANTENNAS'][antenna_group]['frequency']
        ht = fichier_de_device['ANTENNAS'][antenna_group]['height']
        hr = fichier_de_device['UES'][ue_group]['height']
        distance = calculate_distance(antenna_coords, ue_coords)
        # A = 
        if fc < 0.3 :
            # (PROF) Est-ce que le log est base 10 pour okumura?
            # (PROF) est-ce que les chiffres dans les formules en dB doivent etre converti (exemple avec le 1.1 ici)?
            A = 8.29*(math.log10(1.54*hr))**2 - 1.1
        elif fc >= 0.3 :
            A = 3.2*(math.log10(11.75*hr))**2 - 4.97
        pathloss = 69.55 + 26.16*math.log10(fc) - 13.82*math.log10(ht) - A + (44.9 - 6.55*math.log10(ht))*math.log10(distance)
        return pathloss
    if model == "okumura" and scenario == "suburban":
        # Model okumura scenario suburbain
        antenna_group, antenna_coords = get_group_and_coords_by_id(antennas, antenna_id)
        ue_group, ue_coords = get_group_and_coords_by_id(ues, ue_id)
        fc = fichier_de_device['ANTENNAS'][antenna_group]['frequency']
        ht = fichier_de_device['ANTENNAS'][antenna_group]['height']
        hr = fichier_de_device['UES'][ue_group]['height']
        distance = calculate_distance(antenna_coords, ue_coords)
        # (PROF) est-ce que les chiffres dans les formules en dB doivent etre converti (exemple avec le 0.8 ici)?
        A = (1.1*math.log10(fc) - 0.7)*hr - 1.56*math.log10(fc) - 0.8
        pathloss_urban_small = 69.55 + 26.16*math.log10(fc) - 13.82*math.log10(ht) - A + (44.9 - 6.55*math.log10(ht))*math.log10(distance)
        pathloss = pathloss_urban_small - 2*(math.log10(fc/28))**2 - 5.4
        return pathloss
    if model == "okumura" and scenario == "open":
        # Model okumura scenario ouvert
        antenna_group, antenna_coords = get_group_and_coords_by_id(antennas, antenna_id)
        ue_group, ue_coords = get_group_and_coords_by_id(ues, ue_id)
        fc = fichier_de_device['ANTENNAS'][antenna_group]['frequency']
        ht = fichier_de_device['ANTENNAS'][antenna_group]['height']
        hr = fichier_de_device['UES'][ue_group]['height']
        distance = calculate_distance(antenna_coords, ue_coords)
        # (PROF) est-ce que les chiffres dans les formules en dB doivent etre converti (exemple avec le 0.8 ici)?
        A = (1.1*math.log10(fc) - 0.7)*hr - 1.56*math.log10(fc) - 0.8
        pathloss_urban_small = 69.55 + 26.16*math.log10(fc) - 13.82*math.log10(ht) - A + (44.9 - 6.55*math.log10(ht))*math.log10(distance)
        pathloss = pathloss_urban_small - 4.78*(math.log10(fc))**2 -18.733*math.log10(fc) -40.98
        return pathloss    
    # Si aucun cas n'est selectionnee :
    # (PROF) Que doit-on retourner si aucun cas de pathloss n'est trouve?
    return 0

def pathloss_attribution(fichier_de_cas, fichier_de_device, antennas, ues):
    pathloss_list =[]
    for ue in ues:
        for antenna in antennas:
            pathloss = Pathloss(ue.id, antenna.id)
            pathloss.value = okumura(fichier_de_cas, fichier_de_device, antenna.id, ue.id, antennas, ues)
            pathloss_list.append(pathloss)
    return pathloss_list

def association_ue_antenne(pathlosses, antennas, ues):
    # Initialize a dictionary to store the antenna with the smallest pathloss for each UE
    ue_to_antenna = {}

    for pathloss_object in pathlosses:
        ue_id = pathloss_object.id_ue
        ant_id = pathloss_object.id_ant
        pathloss_value = pathloss_object.value

        # If the UE ID is not in the dictionary or the pathloss value is smaller than the current minimum,
        # update the dictionary entry
        if ue_id not in ue_to_antenna or pathloss_value < ue_to_antenna[ue_id][1]:
            ue_to_antenna[ue_id] = (ant_id, pathloss_value)

    # Update the assoc_ant attribute for corresponding UEs
    for ue_id, (ant_id, _) in ue_to_antenna.items():
        ue = next((ue for ue in ues if ue.id == ue_id), None)
        if ue:
            ue.assoc_ant = ant_id

    # Update the assoc_ues attribute for corresponding antennas
    for ant in antennas:
        associated_ues = [ue.id for ue in ues if ue.assoc_ant == ant.id]
        ant.assoc_ues = associated_ues

    return antennas, ues


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


# Fonction vérifiant si le fichier YAML fournit en input a la bonne structure 
def validate_yaml_structure(file_path):
    try:
        with open(file_path, 'r') as file:
            yaml_content = yaml.load(file, Loader=yaml.FullLoader)
    except yaml.YAMLError as e:
        print(f"Error loading YAML file '{file_path}': {e}")
        return False

    # Define the expected structure
    expected_structure = {
        'ETUDE_PATHLOSS': {
            'PATHLOSS': {
                'model': None,
                'scenario': None,
            },
            'ANT_COORD_GEN': None,
            'UE_COORD_GEN': None,
            'COORD_FILES': None,
            'DEVICES': {
                'Antenna1': {'number': None},
                'UE1-App1': {'number': None},
                'UE2-App2': {'number': None},
            },
            'GEOMETRY': {
                'Surface': {
                    'rectangle': {
                        'length': None,
                        'height': None
                    }
                }
            }
        }
    }

    # Validate the structure
    if not validate_structure(yaml_content, expected_structure):
        # Invalid structure in YAML file
        return False

    # Valid structure in YAML file
    return True

# Fonction comparant deux structures YAML et retournant False si différence existe
def validate_structure(content, expected_structure):
    if not isinstance(content, dict) or not isinstance(expected_structure, dict):
        return False

    for key, value in expected_structure.items():
        if key not in content:
            return False

        if value is not None and not validate_structure(content[key], value):
            return False

    return True


def treat_cli_args(arg):
    # arg est une liste qui contient les arguments utilisés lors de l'appel du programme par CLI. 
    # Cette fonction doit retourner le nom du fichier de cas à partir de l'interface de commande (CLI)
    #... 
    # TODO
    #....
    # CETTE FONCTION EST OBLIGATOIRE
    # À noter que dans cette fonction il faut ajouter les vérifications qui s'imposent
    # par exemple, nombre d'arguments appropriés, existance du fichier de cas, etc.
    
    case_file_name = arg[0]
    print("Le nom du fichier de cas est : ",case_file_name)
    # Check if the file exists
    YAML_file_exists = True
    YAML_file_correct_extension = True
    correct_yaml_structure = True
    if os.path.isfile(case_file_name):
        # Check if the file has a YAML extension
        _, file_extension = os.path.splitext(case_file_name)
        if file_extension.lower() not in ['.yaml', '.yml']:
            YAML_file_correct_extension = False
        else:
            # YAML has the correct extension
            # Check if the YAML structure is good
            file_path = case_file_name
            if validate_yaml_structure(file_path):
                correct_yaml_structure = True
            else:
                correct_yaml_structure = False
    else:
        YAML_file_exists = False
    return YAML_file_exists, YAML_file_correct_extension, correct_yaml_structure, case_file_name


def main(arg):
    # Verification de la validitee du fichier yaml fourni par la commande CLI
    yaml_exist, yaml_correct_extenstion, correct_yaml_structure, case_file_name = treat_cli_args(arg)
    print("YAML file name = ", case_file_name)
    if (yaml_exist == False):
        print("YAML file doesn't exist!")   
        return 
    else:
        print("YAML file exists")
    if yaml_correct_extenstion == False :
        print(f"The YAML file does not have the correct extension.")
        return
    else:
        print(f"The YAML file has the correct extension.")
    if correct_yaml_structure == True:
        print(f"The YAML file has the correct structure.")
    else:
        print(f"The YAML file does not have the correct structure.")
        return

    # Debut du programme :
    # case_file_name = "lab1_eq7_cas.yaml"
    device_file_name = "device_db.yaml"
    data_case = read_yaml_file(case_file_name)
    data_device = read_yaml_file(device_file_name)
    fichier_de_cas = data_case
    fichier_de_device = data_device
    antennas, ues = lab1(fichier_de_cas)

    pathlosses = pathloss_attribution(fichier_de_cas,fichier_de_device,antennas,ues)
    antennas, ues = association_ue_antenne(pathlosses, antennas, ues)

    write_to_file(antennas,ues,fichier_de_cas)
    write_pathloss_to_file(pathlosses, fichier_de_cas)
    write_assoc_ues_to_file(antennas, fichier_de_cas)
    write_assoc_ant_to_file(ues, fichier_de_cas)

    #
    #TODO les instructions de main qui vont faire appel aux autres fonctions du programme
    #.....

if __name__ == '__main__':
    # sys.argv est une liste qui contient les arguments utilisés lors de l'appel 
    # du programme à partir du CLI. Cette liste est créée automatiquement par Python. Vous devez 
    # juste inscrire l'argument tel que montré ci-dessous.
    main(sys.argv[1:])