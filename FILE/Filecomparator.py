import os
import json


def sanitize_name(name):
    """Nettoie un chemin pour l'utiliser dans un nom de fichier."""
    return name.replace(os.sep, "_").replace(":", "").replace(" ", "_")


def compare_directories(path1, path2, output_dir="."):
    """
    Compare les fichiers dans deux dossiers et génère des fichiers JSON :
    - equal.json : Fichiers présents dans les deux dossiers.
    - missing_<dossier1>.json : Fichiers manquants dans path2.
    - missing_<dossier2>.json : Fichiers manquants dans path1.
    """
    # Obtenir les noms de fichiers dans chaque dossier
    files1 = set(os.listdir(path1))
    files2 = set(os.listdir(path2))

    # Calculer les fichiers communs et manquants
    equal_files = list(files1 & files2)
    missing_in_path2 = list(files1 - files2)
    missing_in_path1 = list(files2 - files1)

    # Préparer les noms pour les fichiers JSON
    name1 = os.path.basename(path1)
    name2 = os.path.basename(path2)

    # Si les noms sont identiques, ajouter un suffixe "(2)" et inclure les chemins
    if name1 == name2:
        name2 += f"(2)_{sanitize_name(path2)}"
        name1 += f"_{sanitize_name(path1)}"

    equal_file_path = os.path.join(output_dir, "equal.json")
    missing1_file_path = os.path.join(output_dir, f"missing_{name1}.json")
    missing2_file_path = os.path.join(output_dir, f"missing_{name2}.json")

    # Écrire les résultats dans des fichiers JSON
    with open(equal_file_path, "w", encoding="utf-8") as equal_file:
        json.dump(equal_files, equal_file, indent=4, ensure_ascii=False)

    with open(missing1_file_path, "w", encoding="utf-8") as missing1_file:
        json.dump(missing_in_path2, missing1_file, indent=4, ensure_ascii=False)

    with open(missing2_file_path, "w", encoding="utf-8") as missing2_file:
        json.dump(missing_in_path1, missing2_file, indent=4, ensure_ascii=False)

    print(f"Fichiers générés :\n- {equal_file_path}\n- {missing1_file_path}\n- {missing2_file_path}")


if __name__ == "__main__":
    # Demander les chemins des dossiers
    path1 = input("Entrez le chemin du premier dossier : ").strip()
    path2 = input("Entrez le chemin du deuxième dossier : ").strip()
    output_directory = input("Entrez le dossier de sortie des fichiers JSON (par défaut : courant) : ").strip() or "."

    # Vérifier si les dossiers existent
    if not os.path.isdir(path1):
        print(f"Erreur : Le dossier '{path1}' n'existe pas.")
    elif not os.path.isdir(path2):
        print(f"Erreur : Le dossier '{path2}' n'existe pas.")
    else:
        # Comparer les dossiers
        compare_directories(path1, path2, output_directory)
