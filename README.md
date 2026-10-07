# Projeto Web Crawler + API + Dashboard

Projeto da disciplina de Python.

**Integrantes:**

| Nome | RM |
|---|---|
| Eric Kang | 572575 |
| Guilherme Tome Nogueira | 570144 |
| Lucas de Andrade Astorini | 569119 |
| Sabrina Lopes da Silva | 571870 |
| Sofia Satomi Hagio | 569120 |

## Sobre o projeto

A ideia do projeto é coletar dados de um site automaticamente, salvar no MongoDB, disponibilizar por uma API feita com FastAPI e mostrar tudo num dashboard.

O fluxo fica assim:

```
Site -> Web Crawler -> MongoDB -> FastAPI -> Dashboard
```

## Site escolhido

Escolhemos o **Books to Scrape** (https://books.toscrape.com). É uma livraria de mentira que foi feita justamente para quem está aprendendo web scraping, então não tem problema coletar os dados. Também não tem nenhum dado pessoal.

O site tem 1000 livros divididos em 50 categorias. De cada livro a gente pega:

- título
- categoria
- preço (em libras)
- nota (de 1 a 5 estrelas)
- se tem em estoque ou não
- link do livro e link da imagem da capa

Tratamentos que fizemos nos dados:
- o preço vem como texto ("£51.77"), então tiramos o símbolo e convertemos para número
- a nota vem escrita em inglês na classe do HTML ("Three"), então convertemos para número (3)
- os links vêm relativos ("../../livro/index.html"), então transformamos em link completo
- o título que aparece na página vem cortado, então pegamos o título completo do atributo `title`

## Estrutura das pastas

```
projeto-webcrawler/
├── config.py             -> endereço do mongo e do site
├── crawler/
│   ├── crawler.py        -> parte que navega pelas páginas do site
│   └── parser.py         -> funções que tiram as informações do HTML
├── database/
│   ├── db.py             -> conexão com o MongoDB
│   └── repository.py     -> funções que salvam e buscam no banco
├── api/
│   └── main.py           -> endpoints da API (FastAPI)
├── dashboard/
│   ├── index.html
│   ├── style.css
│   └── app.js            -> busca os dados na API e monta os gráficos
├── requirements.txt
└── RODAR_PROJETO.bat     -> roda tudo de uma vez no Windows
```

## Como instalar e rodar

Precisa ter instalado:
- Python 3
- MongoDB Community Server rodando na porta padrão (27017)

**Jeito mais fácil (Windows):** dar dois cliques no `RODAR_PROJETO.bat`. Ele instala as bibliotecas, roda o crawler e abre o dashboard.

**Pelo terminal**, dentro da pasta do projeto:

```bash
# criar o ambiente virtual e instalar as bibliotecas
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# rodar o crawler (o "1" é para pegar só 1 página de cada categoria, sem ele pega tudo)
python -m crawler.crawler 1

# rodar a API
uvicorn api.main:app --reload
```

Depois é só abrir:
- Dashboard: http://localhost:8000
- Documentação da API: http://localhost:8000/docs

## Banco de dados

Usamos o MongoDB com o banco `webcrawler_livros`, que tem 2 coleções.

### Coleção `livros`

Exemplo de um documento:

```json
{
  "_id": "ObjectId(...)",
  "titulo": "A Light in the Attic",
  "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "categoria": "Poetry",
  "preco": 51.77,
  "avaliacao": 3,
  "disponibilidade": "In stock",
  "em_estoque": true,
  "imagem_url": "https://books.toscrape.com/media/cache/.../capa.jpg",
  "fonte": "books.toscrape.com",
  "data_primeira_coleta": "2026-10-06T16:00:00",
  "data_ultima_coleta": "2026-10-06T16:00:00"
}
```

- Os campos `fonte` e `url` mostram **de onde** o dado veio, e `data_primeira_coleta` / `data_ultima_coleta` mostram **quando**.
- Para **não ter livro duplicado**, criamos um índice único no campo `url`. Quando o crawler encontra um livro que já está no banco, ele só atualiza os dados e a `data_ultima_coleta`.
- Rodar o crawler de novo **não apaga** nada que já foi coletado.

### Coleção `coletas`

Guarda um registro de cada vez que o crawler rodou:

```json
{
  "origem": "https://books.toscrape.com/",
  "inicio": "2026-10-06T16:00:00",
  "fim": "2026-10-06T16:00:30",
  "livros_novos": 0,
  "livros_atualizados": 300,
  "paginas_visitadas": 50
}
```

## Endpoints da API

| Método | Endpoint | O que faz |
|---|---|---|
| GET | `/livros` | Lista os livros (com paginação, busca e filtros) |
| GET | `/livros/{id}` | Mostra um livro específico pelo id |
| GET | `/categorias` | Lista todas as categorias |
| GET | `/estatisticas` | Total de livros, preço médio, nota média, % em estoque, nº de categorias e livro mais caro |
| GET | `/graficos` | Dados para os gráficos do dashboard |
| GET | `/coletas` | Histórico das vezes que o crawler rodou |

Filtros que dá para usar em `/livros`, `/estatisticas` e `/graficos`:
- `busca` -> pesquisa no título
- `categoria`
- `nota_minima` -> de 1 a 5
- `preco_min` e `preco_max`

Só no `/livros`: `pagina`, `limite`, `ordenar` (titulo, preco, avaliacao, categoria) e `ordem` (asc ou desc).

Exemplos:
```
/livros?busca=love&nota_minima=4
/livros?categoria=Travel&ordenar=preco&ordem=desc
/estatisticas?categoria=Poetry
```

## Dashboard

O dashboard foi feito com HTML, CSS e JavaScript, e os gráficos usam a biblioteca Chart.js. Ele pega os dados **só pela API**.

Tem:
- cards com o total de livros, preço médio, nota média, % em estoque e quantidade de categorias
- 3 gráficos: top 10 categorias, livros por nota e livros por faixa de preço
- filtros por título, categoria, nota e preço (atualizam os cards, os gráficos e a tabela)
- tabela com os livros e paginação

## Demonstração

1. Rodar o crawler e mostrar ele coletando as páginas no terminal
2. Abrir o MongoDB Compass e mostrar as coleções `livros` e `coletas`
3. Rodar o crawler de novo e mostrar que não duplicou os livros
4. Abrir o `/docs` da API e testar os endpoints
5. Abrir o dashboard e usar os filtros
