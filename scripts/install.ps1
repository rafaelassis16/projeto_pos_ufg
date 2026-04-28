# scripts/install.ps1
Write-Host "Iniciando instalação das dependências..." -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv .venv
}

Write-Host "Instalando dependências do projeto (modo editável + dev)..." -ForegroundColor Yellow
& .venv\Scripts\pip install -e .[dev]

Write-Host "Instalação concluída!" -ForegroundColor Green
