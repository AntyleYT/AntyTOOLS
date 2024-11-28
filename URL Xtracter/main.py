import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import zipfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configuration du dossier de téléchargement
DOWNLOAD_FOLDER = "download"


def setup_browser():
    options = Options()
    options.add_argument('--headless')  # Mode headless (pas d'interface graphique)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def create_download_directory():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)


def download_file(url):
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            print(f"URL invalide : {url}")
            return None

        response = requests.get(url, stream=True)
        response.raise_for_status()

        filename = os.path.basename(parsed_url.path)
        download_path = os.path.join(DOWNLOAD_FOLDER, filename)

        with open(download_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return download_path
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement du fichier {url}: {e}")
        return None


def extract_and_download_files(url, browser, visited_urls=set()):
    if url in visited_urls:
        return []

    visited_urls.add(url)
    browser.get(url)
    browser.implicitly_wait(10)

    soup = BeautifulSoup(browser.page_source, "html.parser")
    file_urls = []

    tags_attributes = {
        "a": "href",
        "link": "href",
        "script": "src",
        "img": "src",
        "iframe": "src",
        "source": "src"
    }

    for tag, attribute in tags_attributes.items():
        for element in soup.find_all(tag):
            file_url = element.get(attribute)
            if file_url:
                full_url = urljoin(url, file_url)
                if any(full_url.endswith(ext) for ext in
                       [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".html", ".htm", ".php", ".pdf",
                        ".woff", ".woff2", ".ttf", ".eot"]):
                    file_urls.append(full_url)
                elif full_url.startswith(url):
                    file_urls.extend(extract_and_download_files(full_url, browser, visited_urls))

    create_download_directory()
    return file_urls


def download_files_in_parallel(file_urls):
    downloaded_files = []
    with ThreadPoolExecutor(max_workers=10) as executor:  # 10 threads pour le téléchargement
        future_to_url = {executor.submit(download_file, url): url for url in file_urls}
        for future in as_completed(future_to_url):
            result = future.result()
            if result:
                downloaded_files.append(result)
    return downloaded_files


def zip_downloaded_files(files, zip_filename="download.zip"):
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))
    print(f"Fichiers compressés dans {zip_filename}")


def cleanup_download_directory():
    shutil.rmtree(DOWNLOAD_FOLDER)
    print("Dossier 'download' nettoyé.")


def validate_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


# Demande de l'URL et exécution du script
url = input("Entrez l'URL du site à extraire : ")
url = validate_url(url)

# Initialisation du navigateur Selenium
browser = setup_browser()

try:
    file_urls = extract_and_download_files(url, browser)
    if file_urls:
        downloaded_files = download_files_in_parallel(file_urls)
        if downloaded_files:
            zip_downloaded_files(downloaded_files)
            cleanup_download_directory()
        else:
            print("Aucun fichier n'a été téléchargé.")
    else:
        print("Aucun fichier n'a été trouvé pour téléchargement.")
finally:
    browser.quit()
