import requests
from bs4 import BeautifulSoup
import re

# Função para obter informações dos animes na página de lançamentos
def get_anime_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    animes = []
    section_body = soup.find('div', class_='section--body')
    articles = section_body.find_all('article', limit=30)

    for article in articles:
        title = article['title']
        link = 'https://www.anibunker.com/' + article.find('a')['href']
        cover = article.find('img')['src']
        animes.append((title, link, cover))

    return animes

# Função para obter os últimos episódios legendados e dublados
def get_last_episodes(anime_url):
    response = requests.get(anime_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    legendado_links = []
    dublado_links = []

    episodes = soup.find_all('a', href=re.compile(r'/anime/.+-episodio-\d+-(legendado|dublado)'))

    # Extrair os números dos episódios usando expressão regular
    episode_numbers = [int(re.search(r'\d+', ep['href']).group()) for ep in episodes]

    # Ordenar os episódios pelo número
    episodes_sorted = sorted(zip(episodes, episode_numbers), key=lambda x: x[1], reverse=True)

    for episode, _ in episodes_sorted[:4]:
        if 'legendado' in episode['href']:
            legendado_links.append('https://www.anibunker.com' + episode['href'])
        elif 'dublado' in episode['href']:
            dublado_links.append('https://www.anibunker.com' + episode['href'])

    return legendado_links, dublado_links

# URL da página de lançamentos
releases_url = 'https://www.anibunker.com/releases'

# Obter informações dos animes
animes = get_anime_info(releases_url)

# Para cada anime, obter os últimos episódios legendados e dublados
for anime in animes:
    title, link, cover = anime
    legendado_links, dublado_links = get_last_episodes(link)

    print(f"Anime: {title}")
    print(f"Capa: {cover}")
    print(f"Link do Anime: {link}")
    print("\nÚltimos episódios legendados:")
    if legendado_links:
        for ep in legendado_links:
            print(ep)
    else:
        print("Ops, esse anime não tem episódios legendados disponíveis.")

    print("\nÚltimos episódios dublados:")
    if dublado_links:
        for ep in dublado_links:
            print(ep)
    else:
        print("Ops, esse anime não tem episódios dublados disponíveis.")

    print("\n" + "="*50 + "\n")
