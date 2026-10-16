@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Protesta Live - TIKTOK

rem 2-TIKTOK.bat                  -> lidhet me @partiamegrada
rem 2-TIKTOK.bat @emri            -> llogari tjeter
rem 2-TIKTOK.bat @emri 9124       -> nese loja perdor port lidhjeje tjeter
rem Mund ta hapesh para ose pas live-it: provon vete cdo 5 sekonda derisa live-i te hapet.
set TTUSER=%~1
if "%TTUSER%"=="" set TTUSER=@partiamegrada
set WSPORT=%~2
if "%WSPORT%"=="" set WSPORT=8124

where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)
%PY% --version >nul 2>nul
if errorlevel 1 (
  echo Python nuk u gjet. Instalo Python 3.12 nga python.org dhe ndiz "Add Python to PATH".
  pause
  exit /b 1
)

echo [1/2] Po instaloj bibliotekat ^(vetem hera e pare ndalon pak^)...
%PY% -m pip install -q -U pip setuptools wheel
%PY% -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo Instalimi normal deshtoi, po provoj rrugen alternative...
  %PY% -m pip install -q --no-deps TikTokLive
  %PY% -m pip install -q TikTokLiveProto==0.2.2 betterproto2==0.9.1 EulerApiSdk==0.1.0 websockets_proxy==0.1.3 "python-socks[asyncio]" httpx pyee==13.0.1 ffmpy websockets
)

echo [2/2] Po lidhem me TikTok ^(%TTUSER%^). Po pres live-in...
%PY% tiktok_bridge.py --user %TTUSER% --ws-port %WSPORT%
echo.
echo Ura e TikTok u ndal. Shih gabimin me siper.
pause
