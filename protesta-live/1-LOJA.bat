@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Protesta Live - LOJA

rem 1-LOJA.bat            -> hap lojen (pa TikTok)
rem 1-LOJA.bat demo       -> loja me ngjarje te simuluara (prove)
rem 1-LOJA.bat 9123 9124  -> porta tjeter e faqes dhe e lidhjes
set DEMO=
set PORT=8123
set WSPORT=8124
if /i "%~1"=="demo" (set DEMO=--demo) else (
  if not "%~1"=="" set PORT=%~1
  if not "%~2"=="" set WSPORT=%~2
)

where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)
%PY% --version >nul 2>nul
if errorlevel 1 (
  echo Python nuk u gjet. Instalo Python 3.12 nga python.org dhe ndiz "Add Python to PATH".
  pause
  exit /b 1
)

echo [1/2] Po kontrolloj bibliotekat...
%PY% -m pip install -q websockets

echo [2/2] Po hap lojen ^(faqja %PORT%, lidhja %WSPORT%^)...
start "" cmd /c "timeout /t 3 /nobreak >nul && start msedge --app=http://localhost:%PORT%/?ws=ws://localhost:%WSPORT% --window-size=540,960"
%PY% server.py %DEMO% --http-port %PORT% --ws-port %WSPORT%
echo.
echo Serveri i lojes u ndal. Shih gabimin me siper.
pause
