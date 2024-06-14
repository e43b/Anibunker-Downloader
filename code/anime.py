import os
import requests
from bs4 import BeautifulSoup
import re

# Função para obter o número total de episódios e verificar as versões disponíveis
def get_total_episodes_and_versions(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extrair o nome do anime
    anime_name = soup.find('h1').text.strip().replace(' ', '_')

    # Extrair o total de episódios
    perfil_desc = soup.find('div', class_='perfil--desc')
    total_episodes_text = perfil_desc.find_all('li')[4].text if perfil_desc else ""

    # Inicializar as variáveis de contagem de episódios
    total_episodes_legendado = 0
    total_episodes_dublado = 0

    # Verificar se há episódios legendados e dublados
    if 'legendado' in total_episodes_text.lower():
        total_episodes_legendado = int(total_episodes_text.split(' ')[1])
    if 'dublado' in total_episodes_text.lower():
        total_episodes_dublado = int(total_episodes_text.split(' ')[-2])

    return anime_name, total_episodes_legendado, total_episodes_dublado

# Função para gerar links de episódios
def generate_episode_links(base_url, total_episodes, version):
    return [f"{base_url}-episodio-{i}-{version}" for i in range(1, total_episodes + 1)]

# Função para criar o diretório, se não existir
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Função para baixar o vídeo
def download_video(url, path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        print(f"Download do vídeo {path} iniciado...")
        with open(path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Download do vídeo {path} concluído.")
    else:
        print(f"Erro ao baixar o vídeo {path}.")

# Função para encontrar links alternativos de vídeo
def find_alternative_video_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar todas as tags <script> na página
    scripts = soup.find_all('script')

    # Procurar por links do Rumble nos scripts
    rumble_links = []
    for script in scripts:
        if script.string:
            # Usar regex para encontrar links do Rumble
            links = re.findall(r'https://[^ ]*cdn\.rumble\.cloud[^ ]*\.mp4', script.string)
            rumble_links.extend(links)

    return rumble_links

# Função para baixar os episódios
def download_episodes(links, version):
    for link in links:
        # Obter o HTML da página do episódio
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extrair as informações do HTML
        title_tag = soup.find('title').text
        anime_name = ' '.join(title_tag.split(' ')[:-2])  # Pega todos os termos antes de "episódio x"
        episode_number = title_tag.split(' ')[-1]
        episode_title_tag = soup.find('h4')
        episode_title = episode_title_tag.text.replace(' ', '_') if episode_title_tag else f'Episódio_{episode_number}'
        video_tag = soup.find('video')
        video_url = video_tag['src'] if video_tag else None

        if not video_url:
            # Tentar encontrar links alternativos
            alternative_links = find_alternative_video_links(link)
            if alternative_links:
                video_url = alternative_links[0]  # Usar o primeiro link alternativo encontrado
                print(f"Link alternativo encontrado para {link}")
            else:
                print(f"Vídeo não encontrado para o link: {link}")
                continue

        # Substituir espaços por underscores no nome do anime
        anime_name = anime_name.replace(' ', '_')

        # Criar o caminho do arquivo com a versão (legendado ou dublado)
        directory = f"{anime_name}-{version}"
        filename = f"{episode_number}-{episode_title}.mp4"
        path = os.path.join(directory, filename)

        # Criar o diretório
        create_directory(directory)

        # Baixar o vídeo
        download_video(video_url, path)

# Solicitar o URL da página do anime ao usuário
anime_url = input("Insira o URL da página do anime: ").strip()

# Obter o nome do anime e o número total de episódios e versões disponíveis
anime_name, total_episodes_legendado, total_episodes_dublado = get_total_episodes_and_versions(anime_url)

# Verificar as versões disponíveis e solicitar ao usuário a escolha
if total_episodes_legendado > 0 and total_episodes_dublado > 0:
    choice = input("Deseja baixar a versão legendada, dublada ou ambas? (legendada/dublada/ambas): ").strip().lower()
elif total_episodes_legendado > 0:
    choice = "legendada"
    print("Apenas a versão legendada está disponível.")
elif total_episodes_dublado > 0:
    choice = "dublada"
    print("Apenas a versão dublada está disponível.")
else:
    print("Nenhuma versão está disponível para download.")
    choice = ""

# Gerar e baixar os links conforme a escolha do usuário
if choice in ["legendada", "ambas"]:
    legendado_links = generate_episode_links(anime_url, total_episodes_legendado, 'legendado')
    download_episodes(legendado_links, 'legendado')

if choice in ["dublada", "ambas"]:
    dublado_links = generate_episode_links(anime_url, total_episodes_dublado, 'dublado')
    download_episodes(dublado_links, 'dublado')
