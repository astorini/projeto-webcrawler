import re
from datetime import datetime

from bson import ObjectId

from database.db import colecao_livros, colecao_coletas


def salvar_livro(livro):
    agora = datetime.now()
    livro_existente = colecao_livros.find_one({"url": livro["url"]})

    if livro_existente:
        livro["data_ultima_coleta"] = agora
        colecao_livros.update_one({"url": livro["url"]}, {"$set": livro})
        return False
    else:
        livro["data_primeira_coleta"] = agora
        livro["data_ultima_coleta"] = agora
        colecao_livros.insert_one(livro)
        return True


def salvar_coleta(inicio, fim, novos, atualizados, paginas):
    colecao_coletas.insert_one({
        "origem": "https://books.toscrape.com/",
        "inicio": inicio,
        "fim": fim,
        "livros_novos": novos,
        "livros_atualizados": atualizados,
        "paginas_visitadas": paginas,
    })


def arrumar_id(documento):
    documento["id"] = str(documento["_id"])
    del documento["_id"]
    return documento


def montar_filtro(busca=None, categoria=None, nota_minima=None, preco_min=None, preco_max=None):
    filtro = {}
    if busca:
        filtro["titulo"] = {"$regex": re.escape(busca), "$options": "i"}
    if categoria:
        filtro["categoria"] = categoria
    if nota_minima:
        filtro["avaliacao"] = {"$gte": nota_minima}
    if preco_min is not None or preco_max is not None:
        filtro["preco"] = {}
        if preco_min is not None:
            filtro["preco"]["$gte"] = preco_min
        if preco_max is not None:
            filtro["preco"]["$lte"] = preco_max
    return filtro


def listar_livros(filtro, pagina=1, limite=20, ordenar="titulo", ordem="asc"):
    if ordem == "desc":
        direcao = -1
    else:
        direcao = 1

    total = colecao_livros.count_documents(filtro)
    pular = (pagina - 1) * limite
    resultado = colecao_livros.find(filtro).sort(ordenar, direcao).skip(pular).limit(limite)

    livros = []
    for livro in resultado:
        livros.append(arrumar_id(livro))

    total_paginas = total // limite
    if total % limite != 0:
        total_paginas += 1

    return {
        "total": total,
        "pagina": pagina,
        "total_paginas": max(total_paginas, 1),
        "livros": livros,
    }


def buscar_livro(id_livro):
    try:
        livro = colecao_livros.find_one({"_id": ObjectId(id_livro)})
    except Exception:
        return None
    if livro is None:
        return None
    return arrumar_id(livro)


def listar_categorias():
    categorias = colecao_livros.distinct("categoria")
    categorias.sort()
    return categorias


def calcular_estatisticas(filtro):
    livros = list(colecao_livros.find(filtro))
    total = len(livros)

    ultima_coleta = colecao_coletas.find_one(sort=[("fim", -1)])
    data_ultima_coleta = ultima_coleta["fim"] if ultima_coleta else None

    if total == 0:
        return {"total_livros": 0, "preco_medio": 0, "nota_media": 0,
                "porcentagem_em_estoque": 0, "total_categorias": 0,
                "livro_mais_caro": None, "ultima_coleta": data_ultima_coleta}

    soma_precos = 0
    soma_notas = 0
    qtd_em_estoque = 0
    categorias = []
    mais_caro = livros[0]

    for livro in livros:
        soma_precos += livro["preco"]
        soma_notas += livro["avaliacao"]
        if livro["em_estoque"]:
            qtd_em_estoque += 1
        if livro["categoria"] not in categorias:
            categorias.append(livro["categoria"])
        if livro["preco"] > mais_caro["preco"]:
            mais_caro = livro

    return {
        "total_livros": total,
        "preco_medio": round(soma_precos / total, 2),
        "nota_media": round(soma_notas / total, 2),
        "porcentagem_em_estoque": round(qtd_em_estoque / total * 100, 1),
        "total_categorias": len(categorias),
        "livro_mais_caro": {"titulo": mais_caro["titulo"], "preco": mais_caro["preco"]},
        "ultima_coleta": data_ultima_coleta,
    }


def dados_graficos(filtro):
    livros = list(colecao_livros.find(filtro))

    por_categoria = {}
    for livro in livros:
        cat = livro["categoria"]
        if cat in por_categoria:
            por_categoria[cat] += 1
        else:
            por_categoria[cat] = 1
    top_categorias = sorted(por_categoria.items(), key=lambda item: item[1], reverse=True)[:10]

    por_nota = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for livro in livros:
        if livro["avaliacao"] in por_nota:
            por_nota[livro["avaliacao"]] += 1

    faixas = {"Até £20": 0, "£20 a £35": 0, "£35 a £50": 0, "Mais de £50": 0}
    for livro in livros:
        preco = livro["preco"]
        if preco < 20:
            faixas["Até £20"] += 1
        elif preco < 35:
            faixas["£20 a £35"] += 1
        elif preco < 50:
            faixas["£35 a £50"] += 1
        else:
            faixas["Mais de £50"] += 1

    return {
        "categorias": [{"categoria": c, "quantidade": q} for c, q in top_categorias],
        "notas": [{"nota": n, "quantidade": q} for n, q in por_nota.items()],
        "faixas_preco": [{"faixa": f, "quantidade": q} for f, q in faixas.items()],
    }


def listar_coletas():
    coletas = []
    for coleta in colecao_coletas.find().sort("inicio", -1).limit(20):
        coletas.append(arrumar_id(coleta))
    return coletas
