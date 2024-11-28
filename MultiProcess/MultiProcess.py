import os
import subprocess
import threading
from colorama import init, Fore

# Initialisation de colorama pour fonctionner sur tous les systèmes (Windows, Mac, Linux)
init(autoreset=True)

# Dictionnaire pour stocker les processus en cours
processes = {}

# Dossier contenant les fichiers Python à exécuter
FILES_DIR = "files"


def colored_print(message, color=Fore.WHITE):
    """Fonction d'impression colorée."""
    print(color + message)


def run_file(file_name):
    """Lance un fichier Python du dossier 'files' en arrière-plan."""
    file_path = os.path.join(FILES_DIR, file_name)
    if file_name in processes:
        colored_print(f"{file_name} est déjà en cours d'exécution.", Fore.YELLOW)
        return
    if not os.path.exists(file_path):
        colored_print(f"Le fichier {file_name} n'existe pas dans {FILES_DIR}.", Fore.RED)
        return
    try:
        # Lance le fichier dans un processus séparé et capture la sortie en UTF-8
        process = subprocess.Popen(
            ["python", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # Utilisation de texte pour la sortie (en UTF-8)
            bufsize=1  # Ligne par ligne (buffering)
        )
        processes[file_name] = process
        colored_print(f"{file_name} a été démarré.", Fore.GREEN)

        # Lancer le monitoring de la sortie dans un thread séparé
        threading.Thread(target=monitor_output, args=(file_name, process), daemon=True).start()
    except Exception as e:
        colored_print(f"Erreur lors du démarrage de {file_name}: {e}", Fore.RED)


def monitor_output(file_name, process):
    """Affiche la sortie du fichier Python dans la console avec le format [nom_fichier.py : Console]."""
    # Affichage d'introduction de la console pour le fichier
    colored_print(f"[{file_name} : Console] :", Fore.CYAN)

    # Utiliser `iter()` pour récupérer ligne par ligne, plus propre
    stdout_lines = iter(process.stdout.readline, "")
    stderr_lines = iter(process.stderr.readline, "")

    # Affiche toutes les sorties stdout et stderr en temps réel
    for line in stdout_lines:
        if line:
            colored_print(f"[{file_name} : Console] : {line.strip()}", Fore.WHITE)

    for line in stderr_lines:
        if line:
            colored_print(f"[{file_name} : Console] : {line.strip()}", Fore.RED)

    process.stdout.close()
    process.stderr.close()
    process.wait()

    # Une fois le processus terminé
    colored_print(f"[{file_name} : Console] : Terminé.", Fore.GREEN)
    del processes[file_name]  # Retirer le processus une fois terminé


def stop_file(file_name):
    """Arrête un fichier Python en cours d'exécution."""
    process = processes.pop(file_name, None)
    if process:
        process.terminate()
        process.wait()
        colored_print(f"{file_name} a été arrêté.", Fore.YELLOW)
    else:
        colored_print(f"{file_name} n'est pas en cours d'exécution.", Fore.RED)


def restart_file(file_name):
    """Redémarre un fichier Python."""
    stop_file(file_name)
    run_file(file_name)


def list_files():
    """Affiche tous les fichiers Python dans le dossier 'files'."""
    if not os.path.exists(FILES_DIR):
        colored_print(f"Le dossier {FILES_DIR} n'existe pas.", Fore.RED)
        return
    files = [f for f in os.listdir(FILES_DIR) if f.endswith('.py')]
    colored_print("Fichiers disponibles dans 'files' :", Fore.CYAN)
    for f in files:
        colored_print(f, Fore.WHITE)


def list_running():
    """Affiche les fichiers en cours d'exécution."""
    if not processes:
        colored_print("Aucun fichier en cours d'exécution.", Fore.RED)
    else:
        colored_print("Fichiers en cours d'exécution :", Fore.CYAN)
        for file_name in processes.keys():
            colored_print(file_name, Fore.WHITE)


def reload_server():
    """Relance le script serveur."""
    colored_print("Rechargement du serveur...", Fore.YELLOW)
    os.execv(__file__, [])


def handle_command():
    """Boucle principale pour gérer les commandes."""
    while True:
        command = input("> ").strip()
        # Normalisation des commandes pour accepter à la fois "/list" et "list"
        if command.startswith("/run") or command.startswith("run"):
            _, file_name = command.split(maxsplit=1) if command.startswith("/run") else (
            command.split()[0], command.split()[1])
            run_file(file_name)
        elif command.startswith("/stop") or command.startswith("stop"):
            _, file_name = command.split(maxsplit=1) if command.startswith("/stop") else (
            command.split()[0], command.split()[1])
            stop_file(file_name)
        elif command.startswith("/restart") or command.startswith("restart"):
            _, file_name = command.split(maxsplit=1) if command.startswith("/restart") else (
            command.split()[0], command.split()[1])
            restart_file(file_name)
        elif command == "/list" or command == "list":
            list_files()
        elif command == "/list_running" or command == "list_running":
            list_running()
        elif command == "/reload" or command == "reload":
            reload_server()
        elif command == "/exit" or command == "exit":
            colored_print("Arrêt du serveur...", Fore.RED)
            for file_name in list(processes.keys()):
                stop_file(file_name)
            break
        else:
            colored_print("Commande non reconnue.", Fore.RED)


# Création du dossier 'files' s'il n'existe pas
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)
    colored_print(f"Le dossier '{FILES_DIR}' a été créé. Placez vos fichiers Python dedans.", Fore.GREEN)

# Démarrage de la boucle principale dans un thread séparé
if __name__ == "__main__":
    colored_print("Serveur de gestion de fichiers démarré.", Fore.GREEN)
    command_thread = threading.Thread(target=handle_command, daemon=True)
    command_thread.start()

    # La boucle principale attend les entrées de la commande, sans être bloquée par les fichiers en cours d'exécution
    command_thread.join()  # Permet à la boucle des commandes de continuer en parallèle
