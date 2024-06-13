import os
import requests
from bs4 import BeautifulSoup

# Função para criar o diretório, se não existir
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Função para baixar o vídeo
def download_video(url, path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        print("Download do vídeo iniciado...")
        with open(path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print("Download do vídeo concluído.")
    else:
        print("Erro ao baixar o vídeo.")

# URL da página
url = 'https://www.anibunker.com/anime/hajime-no-ippo-episodio-45-legendado'

# Obter o HTML da página
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extrair as informações do HTML
title_tag = soup.find('title').text
anime_name = ' '.join(title_tag.split(' ')[:-2])  # Pega todos os termos antes de "episódio x"
episode_number = title_tag.split(' ')[-1]
episode_title = soup.find('h4').text.replace(' ', '_')
video_url = soup.find('video')['src']

# Substituir espaços por underscores no nome do anime
anime_name = anime_name.replace(' ', '_')

# Verificar se a URL contém "legendado" ou "dublado"
if 'legendado' in url:
    version = 'legendado'
elif 'dublado' in url:
    version = 'dublado'
else:
    version = ''

# Criar o caminho do arquivo com a versão (legendado ou dublado)
directory = f"{anime_name}-{version}" if version else anime_name
filename = f"{episode_number}-{episode_title}.mp4"
path = os.path.join(directory, filename)

# Criar o diretório
create_directory(directory)

# Baixar o vídeo
download_video(video_url, path)

print(f"Vídeo salvo em: {path}")
