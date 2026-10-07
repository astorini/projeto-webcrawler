@echo off
cd /d "%~dp0"
echo Coletando todos os livros do site (demora alguns minutos)...
venv\Scripts\python -m crawler.crawler
pause
