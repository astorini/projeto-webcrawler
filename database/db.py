from pymongo import MongoClient

import config

cliente = MongoClient(config.MONGO_URI)
banco = cliente[config.NOME_BANCO]

colecao_livros = banco["livros"]
colecao_coletas = banco["coletas"]

colecao_livros.create_index("url", unique=True)
