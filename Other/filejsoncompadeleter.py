import os
import json


def delete_files_from_json(json_path, folder_path):
    """
    Supprime les fichiers listés dans un fichier JSON d'un dossier donné.

    Arguments :
    - json_path : Chemin vers le fichier JSON contenant les noms de fichiers.
    - folder_path : Chemin vers le dossier où les fichiers doivent être supprimés.
    """
    # Vérifier si le fichier JSON et le dossier existent
    if not os.path.isfile(json_path):
        print(f"Erreur : Le fichier JSON '{json_path}' n'existe pas.")
        return
    if not os.path.isdir(folder_path):
        print(f"Erreur : Le dossier '{folder_path}' n'existe pas.")
        return

    # Lire les noms de fichiers depuis le JSON
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            files_to_delete = json.load(file)
    except json.JSONDecodeError:
        print(f"Erreur : Impossible de lire le fichier JSON '{json_path}'.")
        return

    # Supprimer les fichiers
    deleted_files = []
    not_found_files = []
    for filename in files_to_delete:
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                deleted_files.append(filename)
            except Exception as e:
                print(f"Erreur lors de la suppression de '{file_path}': {e}")
        else:
            not_found_files.append(filename)

    # Résumé des opérations
    print(f"\nFichiers supprimés ({len(deleted_files)}):")
    for f in deleted_files:
        print(f" - {f}")

    if not_found_files:
        print(f"\nFichiers non trouvés ({len(not_found_files)}):")
        for f in not_found_files:
            print(f" - {f}")


if __name__ == "__main__":
    # Demander les chemins des fichiers et dossiers
    json_path = input("Entrez le chemin du fichier JSON (missing_*.json ou equal.json) : ").strip()
    folder_path = input("Entrez le chemin du dossier cible : ").strip()

    # Appeler la fonction pour supprimer les fichiers
    delete_files_from_json(json_path, folder_path)
