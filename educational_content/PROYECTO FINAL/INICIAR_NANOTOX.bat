@echo off
title NanoTox AI — Servidor
echo ==========================================
echo   NanoTox AI Predictor
echo   Prediccion de Toxicidad de Nanoparticulas
echo ==========================================
echo.
echo Iniciando servidor...
echo.
cd /d "%~dp0nanotox_api"
call conda activate ia_nano 2>nul || call activate ia_nano 2>nul
echo.
echo Dashboard disponible en: http://localhost:8000
echo Presiona Ctrl+C para detener el servidor.
echo.
start "" "http://localhost:8000"
python app.py
pause
