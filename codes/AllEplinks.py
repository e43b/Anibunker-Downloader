import requests
from bs4 import BeautifulSoup

# Função para obter o número total de episódios
def get_total_episodes(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extrair o nome do anime
    anime_name = soup.find('h1').text.strip().replace(' ', '_')

    # Extrair o total de episódios
    perfil_desc = soup.find('div', class_='perfil--desc')
    total_episodes_text = perfil_desc.find_all('li')[4].text if perfil_desc else ""

    # Extrair os números de episódios legendados e dublados
    total_episodes_legendado = int(total_episodes_text.split(' ')[1])
    total_episodes_dublado = int(total_episodes_text.split(' ')[-2])

    return anime_name, total_episodes_legendado, total_episodes_dublado

# Função para gerar links de episódios
def generate_episode_links(anime_name, total_episodes, version):
    base_url = f"https://www.anibunker.com/anime/{anime_name.lower().replace('_', '-')}-episodio-"
    return [f"{base_url}{i}-{version}" for i in range(1, total_episodes + 1)]

# URL da página do anime
anime_url = 'https://www.anibunker.com/anime/death-note'

# Obter o nome do anime e o número total de episódios
anime_name, total_episodes_legendado, total_episodes_dublado = get_total_episodes(anime_url)

# Gerar links para episódios legendados e dublados
legendado_links = generate_episode_links(anime_name, total_episodes_legendado, 'legendado')
dublado_links = generate_episode_links(anime_name, total_episodes_dublado, 'dublado')

print("Links dos episódios legendados:")
for link in legendado_links:
    print(link)

print("\nLinks dos episódios dublados:")
for link in dublado_links:
    print(link)
