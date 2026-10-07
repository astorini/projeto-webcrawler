from urllib.parse import urljoin

from bs4 import BeautifulSoup

NOTAS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def pegar_categorias(html, url_base):
    soup = BeautifulSoup(html, "html.parser")
    categorias = []
    links = soup.select("div.side_categories ul li ul li a")
    for link in links:
        nome = link.text.strip()
        url = urljoin(url_base, link["href"])
        categorias.append({"nome": nome, "url": url})
    return categorias


def pegar_livros(html, url_pagina, categoria):
    soup = BeautifulSoup(html, "html.parser")
    livros = []

    for item in soup.find_all("article", class_="product_pod"):
        titulo = item.h3.a["title"].strip()
        link = urljoin(url_pagina, item.h3.a["href"])

        preco_texto = item.find("p", class_="price_color").text
        preco = float(preco_texto.replace("£", "").replace("Â", "").strip())

        classes = item.find("p", class_="star-rating")["class"]
        nota = 0
        for c in classes:
            if c in NOTAS:
                nota = NOTAS[c]

        disponibilidade = item.find("p", class_="availability").text.strip()
        em_estoque = disponibilidade == "In stock"

        imagem = urljoin(url_pagina, item.find("img")["src"])

        livros.append({
            "titulo": titulo,
            "url": link,
            "categoria": categoria,
            "preco": preco,
            "avaliacao": nota,
            "disponibilidade": disponibilidade,
            "em_estoque": em_estoque,
            "imagem_url": imagem,
            "fonte": "books.toscrape.com",
        })

    return livros


def pegar_proxima_pagina(html, url_pagina):
    soup = BeautifulSoup(html, "html.parser")
    botao_next = soup.find("li", class_="next")
    if botao_next:
        return urljoin(url_pagina, botao_next.a["href"])
    return None
