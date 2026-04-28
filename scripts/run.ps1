# scripts/run.ps1
Write-Host "Iniciando a API FastAPI..." -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    Write-Host "Ambiente virtual não encontrado. Execute 'make install' primeiro." -ForegroundColor Red
    exit 1
}

& .venv\Scripts\uvicorn app.main:app --reload
