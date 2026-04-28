# scripts/setup_env.ps1
Write-Host "Configurando variáveis de ambiente..." -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    Write-Host "Criando arquivo .env a partir de .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Arquivo .env criado. Ajuste os valores se necessário." -ForegroundColor Green
} else {
    Write-Host "Arquivo .env já existe." -ForegroundColor Blue
}
