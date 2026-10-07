let paginaAtual = 1;
let totalPaginas = 1;

let graficoCategorias = null;
let graficoNotas = null;
let graficoPrecos = null;


function pegarFiltros() {
    let parametros = new URLSearchParams();

    let busca = document.getElementById("busca").value;
    let categoria = document.getElementById("categoria").value;
    let nota = document.getElementById("nota").value;
    let precoMin = document.getElementById("preco-min").value;
    let precoMax = document.getElementById("preco-max").value;

    if (busca != "") parametros.append("busca", busca);
    if (categoria != "") parametros.append("categoria", categoria);
    if (nota != "") parametros.append("nota_minima", nota);
    if (precoMin != "") parametros.append("preco_min", precoMin);
    if (precoMax != "") parametros.append("preco_max", precoMax);

    return parametros.toString();
}


async function carregarCategorias() {
    let resposta = await fetch("/categorias");
    let categorias = await resposta.json();

    let select = document.getElementById("categoria");
    for (let i = 0; i < categorias.length; i++) {
        let opcao = document.createElement("option");
        opcao.value = categorias[i];
        opcao.textContent = categorias[i];
        select.appendChild(opcao);
    }
}


async function carregarEstatisticas() {
    let resposta = await fetch("/estatisticas?" + pegarFiltros());
    let dados = await resposta.json();

    document.getElementById("total-livros").textContent = dados.total_livros;
    document.getElementById("preco-medio").textContent = "£" + dados.preco_medio.toFixed(2);
    document.getElementById("nota-media").textContent = dados.nota_media + " ★";
    document.getElementById("em-estoque").textContent = dados.porcentagem_em_estoque + "%";
    document.getElementById("total-categorias").textContent = dados.total_categorias;

    if (dados.ultima_coleta) {
        let data = new Date(dados.ultima_coleta);
        document.getElementById("ultima-coleta").textContent = "Última coleta: " + data.toLocaleString("pt-BR");
    }
}


async function carregarGraficos() {
    let resposta = await fetch("/graficos?" + pegarFiltros());
    let dados = await resposta.json();

    if (graficoCategorias) graficoCategorias.destroy();
    if (graficoNotas) graficoNotas.destroy();
    if (graficoPrecos) graficoPrecos.destroy();

    Chart.defaults.font.family = "Poppins";
    Chart.defaults.color = "#9ca3af";

    graficoCategorias = new Chart(document.getElementById("grafico-categorias"), {
        type: "bar",
        data: {
            labels: dados.categorias.map(c => c.categoria),
            datasets: [{
                label: "Livros",
                data: dados.categorias.map(c => c.quantidade),
                backgroundColor: "#818cf8",
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: "y",
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { x: { grid: { color: "#23232e" } }, y: { grid: { display: false } } }
        }
    });

    graficoNotas = new Chart(document.getElementById("grafico-notas"), {
        type: "bar",
        data: {
            labels: dados.notas.map(n => n.nota + " ★"),
            datasets: [{
                label: "Livros",
                data: dados.notas.map(n => n.quantidade),
                backgroundColor: "#fbbf24",
                borderRadius: 6
            }]
        },
        options: {
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { x: { grid: { display: false } }, y: { grid: { color: "#23232e" } } }
        }
    });

    graficoPrecos = new Chart(document.getElementById("grafico-precos"), {
        type: "doughnut",
        data: {
            labels: dados.faixas_preco.map(f => f.faixa),
            datasets: [{
                data: dados.faixas_preco.map(f => f.quantidade),
                backgroundColor: ["#4ade80", "#818cf8", "#c084fc", "#fb7185"],
                borderWidth: 3,
                borderColor: "#15151c"
            }]
        },
        options: {
            maintainAspectRatio: false,
            cutout: "60%",
            plugins: { legend: { position: "bottom", labels: { usePointStyle: true, padding: 16 } } }
        }
    });
}


async function carregarTabela() {
    let resposta = await fetch("/livros?pagina=" + paginaAtual + "&limite=15&" + pegarFiltros());
    let dados = await resposta.json();

    totalPaginas = dados.total_paginas;
    let tabela = document.getElementById("tabela-livros");
    tabela.innerHTML = "";

    if (dados.livros.length == 0) {
        tabela.innerHTML = "<tr><td colspan='6'>Nenhum livro encontrado</td></tr>";
    }

    for (let livro of dados.livros) {
        let estrelas = "★".repeat(livro.avaliacao) + "☆".repeat(5 - livro.avaliacao);
        let estoque = livro.em_estoque ? "<span class='badge sim'>Sim</span>" : "<span class='badge nao'>Não</span>";

        let linha = document.createElement("tr");
        linha.innerHTML = `
            <td><img src="${livro.imagem_url}" alt="capa"></td>
            <td><a href="${livro.url}" target="_blank"></a></td>
            <td><span class="categoria-tag">${livro.categoria}</span></td>
            <td class="preco">£${livro.preco.toFixed(2)}</td>
            <td class="estrelas">${estrelas}</td>
            <td>${estoque}</td>
        `;
        linha.querySelector("a").textContent = livro.titulo;
        tabela.appendChild(linha);
    }

    document.getElementById("info-pagina").textContent =
        "Página " + dados.pagina + " de " + dados.total_paginas + " (" + dados.total + " livros)";
}


function filtrar() {
    paginaAtual = 1;
    carregarEstatisticas();
    carregarGraficos();
    carregarTabela();
}

function limparFiltros() {
    document.getElementById("busca").value = "";
    document.getElementById("categoria").value = "";
    document.getElementById("nota").value = "";
    document.getElementById("preco-min").value = "";
    document.getElementById("preco-max").value = "";
    filtrar();
}

function proximaPagina() {
    if (paginaAtual < totalPaginas) {
        paginaAtual++;
        carregarTabela();
    }
}

function paginaAnterior() {
    if (paginaAtual > 1) {
        paginaAtual--;
        carregarTabela();
    }
}

document.getElementById("busca").addEventListener("keyup", function (evento) {
    if (evento.key == "Enter") filtrar();
});


carregarCategorias();
filtrar();
