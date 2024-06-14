import os
import requests
from bs4 import BeautifulSoup
import re

# Função para criar o diretório, se não existir
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Função para baixar o vídeo
def download_video(url, path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        print(f"Download do vídeo de {url} iniciado...")
        with open(path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Download do vídeo de {url} concluído.")
    else:
        print(f"Erro ao baixar o vídeo de {url}.")

# Função para procurar links alternativos em caso de falha
def find_alternative_video(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    scripts = soup.find_all('script')

    rumble_links = []
    for script in scripts:
        if script.string:
            links = re.findall(r'https://[^ ]*cdn\.rumble\.cloud[^ ]*\.mp4', script.string)
            rumble_links.extend(links)

    return rumble_links[0] if rumble_links else None

# Função para processar os links e baixar os vídeos
def process_links(links):
    for link in links:
        link = link.strip()  # Remove espaços extras
        if link:
            response = requests.get(link)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extrair as informações do HTML
            title_tag = soup.find('title').text
            anime_name = ' '.join(title_tag.split(' ')[:-2])  # Pega todos os termos antes de "episódio x"
            episode_number = title_tag.split(' ')[-1]
            episode_title = soup.find('h4').text.replace(' ', '_')
            video_url = soup.find('video')

            # Se o vídeo não for encontrado, buscar links alternativos
            if not video_url:
                print("Vídeo principal não encontrado. Procurando links alternativos...")
                video_url = find_alternative_video(link)
                if not video_url:
                    print(f"Não foi possível encontrar um vídeo para {link}")
                    continue

            video_url = video_url if isinstance(video_url, str) else video_url['src']

            anime_name = anime_name.replace(' ', '_')
            if 'legendado' in link:
                version = 'legendado'
            elif 'dublado' in link:
                version = 'dublado'
            else:
                version = ''

            directory = f"{anime_name}-{version}" if version else anime_name
            filename = f"{episode_number}-{episode_title}.mp4"
            path = os.path.join(directory, filename)

            create_directory(directory)
            download_video(video_url, path)

            print(f"Vídeo salvo em: {path}")
            print()

# Solicitar links ao usuário
def get_user_input():
    links = input("Digite o(s) link(s) do episódio (separe múltiplos links por vírgula): ").strip()
    links = links.split(',')
    return [link.strip() for link in links]

# Programa principal
def main():
    while True:
        links = get_user_input()
        process_links(links)
        choice = input("Deseja baixar mais episódios? (s/n): ").strip().lower()
        if choice != 's':
            break

if __name__ == "__main__":
    main()
