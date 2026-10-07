@echo off
cd /d "%~dp0"
title Projeto Web Crawler

if not exist venv (
    echo Criando o ambiente virtual...
    python -m venv venv
)

echo Instalando as bibliotecas...
venv\Scripts\python -m pip install -q -r requirements.txt

echo.
echo Rodando o crawler...
venv\Scripts\python -m crawler.crawler 1

echo.
echo Iniciando a API em http://localhost:8000
echo Para parar e so fechar essa janela
start "" cmd /c "timeout /t 4 >nul & start http://localhost:8000"
venv\Scripts\python -m uvicorn api.main:app
pause
