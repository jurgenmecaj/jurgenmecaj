@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Protesta Live - ZERAT SHQIP

rem Gjeneron klipet e zerit shqip (Anila dhe Ilir) ne assets\voice. Nevojitet internet. Nise nje here.
rem Pa kete, loja perdor zerin shqip te Edge (nese e ka) - klipet e bejne zerin me te qendrueshem dhe me cilesi.
where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)
%PY% --version >nul 2>nul
if errorlevel 1 (
  echo Python nuk u gjet. Instalo Python 3.12 nga python.org dhe ndiz "Add Python to PATH".
  pause
  exit /b 1
)
echo Po instaloj edge-tts...
%PY% -m pip install -q -U edge-tts
echo Po gjeneroj klipet ^(rreth 1 minute^)...
%PY% make_voices.py %*
echo.
echo Gati. Rihap 1-LOJA.bat.
pause
