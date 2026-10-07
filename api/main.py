from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import repository

app = FastAPI(title="API de Livros - Projeto Web Crawler")


@app.get("/livros")
def listar_livros(busca: str = None, categoria: str = None, nota_minima: int = None,
                  preco_min: float = None, preco_max: float = None,
                  pagina: int = 1, limite: int = 20, ordenar: str = "titulo", ordem: str = "asc"):
    if ordenar not in ["titulo", "preco", "avaliacao", "categoria"]:
        ordenar = "titulo"
    if limite > 100:
        limite = 100
    filtro = repository.montar_filtro(busca, categoria, nota_minima, preco_min, preco_max)
    return repository.listar_livros(filtro, pagina, limite, ordenar, ordem)


@app.get("/livros/{id_livro}")
def buscar_livro(id_livro: str):
    livro = repository.buscar_livro(id_livro)
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return livro


@app.get("/categorias")
def listar_categorias():
    return repository.listar_categorias()


@app.get("/estatisticas")
def estatisticas(busca: str = None, categoria: str = None, nota_minima: int = None,
                 preco_min: float = None, preco_max: float = None):
    filtro = repository.montar_filtro(busca, categoria, nota_minima, preco_min, preco_max)
    return repository.calcular_estatisticas(filtro)


@app.get("/graficos")
def graficos(busca: str = None, categoria: str = None, nota_minima: int = None,
             preco_min: float = None, preco_max: float = None):
    filtro = repository.montar_filtro(busca, categoria, nota_minima, preco_min, preco_max)
    return repository.dados_graficos(filtro)


@app.get("/coletas")
def listar_coletas():
    return repository.listar_coletas()


app.mount("/static", StaticFiles(directory="dashboard"), name="static")


@app.get("/")
def pagina_inicial():
    return FileResponse("dashboard/index.html")
