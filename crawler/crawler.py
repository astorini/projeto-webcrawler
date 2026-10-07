import sys
import time
from datetime import datetime

import requests

import config
from crawler.parser import pegar_categorias, pegar_livros, pegar_proxima_pagina
from database import repository


def baixar_pagina(url):
    cabecalho = {"User-Agent": "Mozilla/5.0 (projeto da faculdade)"}
    resposta = requests.get(url, headers=cabecalho, timeout=15)
    resposta.encoding = "utf-8"
    time.sleep(0.3)
    return resposta.text


def rodar_crawler(max_paginas=None):
    inicio = datetime.now()
    novos = 0
    atualizados = 0
    paginas_visitadas = 0
    urls_vistas = []

    print("Iniciando a coleta em", config.URL_SITE)
    html_inicial = baixar_pagina(config.URL_SITE)
    categorias = pegar_categorias(html_inicial, config.URL_SITE)
    print("Foram encontradas", len(categorias), "categorias\n")

    for categoria in categorias:
        url = categoria["url"]
        pagina = 1

        while url is not None:
            if max_paginas is not None and pagina > max_paginas:
                break

            try:
                html = baixar_pagina(url)
            except Exception as erro:
                print("Erro ao acessar", url, "->", erro)
                break

            paginas_visitadas += 1
            livros = pegar_livros(html, url, categoria["nome"])
            print(f"{categoria['nome']} - pagina {pagina}: {len(livros)} livros")

            for livro in livros:
                if livro["url"] in urls_vistas:
                    continue
                urls_vistas.append(livro["url"])

                if repository.salvar_livro(livro):
                    novos += 1
                else:
                    atualizados += 1

            url = pegar_proxima_pagina(html, url)
            pagina += 1

    fim = datetime.now()
    repository.salvar_coleta(inicio, fim, novos, atualizados, paginas_visitadas)

    print("\nColeta finalizada!")
    print("Livros novos:", novos)
    print("Livros atualizados:", atualizados)
    print("Paginas visitadas:", paginas_visitadas)
    print("Tempo:", round((fim - inicio).total_seconds()), "segundos")


if __name__ == "__main__":
    max_paginas = None
    if len(sys.argv) > 1:
        max_paginas = int(sys.argv[1])
    rodar_crawler(max_paginas)
