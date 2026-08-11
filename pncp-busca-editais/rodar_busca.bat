@echo off
chcp 65001 > nul
cls
echo ========================================================
echo        SISTEMA DE BUSCA DE EDITAIS PNCP
echo ========================================================
echo.
echo Iniciando o servidor web Streamlit...
echo Uma aba deve abrir automaticamente no seu navegador padrao.
echo.

streamlit run app_streamlit.py

echo.
echo ========================================================
echo Servidor encerrado.
pause
