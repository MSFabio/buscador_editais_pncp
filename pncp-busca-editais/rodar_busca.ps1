# Script do PowerShell para executar a Busca Semântica do PNCP Monitor
Clear-Host
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host "               PNCP MONITOR - BUSCA SEMANTICA DE EDITAIS" -ForegroundColor Cyan
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host "Iniciando varredura automatica de editais..." -ForegroundColor Yellow

# Executa o motor CLI Python
python run_cli.py

Write-Host "`n"
Write-Host "Processo concluido!" -ForegroundColor Green
Write-Host "Verifique os resultados gerados em 'resultados_busca.txt'." -ForegroundColor Cyan
Write-Host "A configuracao de regras pode ser editada em 'buscas_config.json'." -ForegroundColor Gray
Write-Host "==========================================================================" -ForegroundColor Cyan
