@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Protesta Live

rem Perdorimi:  start.bat            -> live i @partiamegrada
rem             start.bat @emri     -> live i nje llogarie tjeter
rem             start.bat demo      -> prove pa TikTok
set TTUSER=%~1
if "%TTUSER%"=="" set TTUSER=@partiamegrada

where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)
%PY% --version >nul 2>nul
if errorlevel 1 (
  echo Python nuk u gjet. Instalo Python 3.12 nga python.org dhe ndiz "Add Python to PATH".
  pause
  exit /b 1
)

echo [1/3] Po instaloj bibliotekat ^(vetem hera e pare ndalon pak^)...
%PY% -m pip install -q -U pip setuptools wheel
%PY% -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo Instalimi normal deshtoi, po provoj rrugen alternative...
  %PY% -m pip install -q --no-deps TikTokLive
  %PY% -m pip install -q TikTokLiveProto==0.2.2 betterproto2==0.9.1 EulerApiSdk==0.1.0 websockets_proxy==0.1.3 "python-socks[asyncio]" httpx pyee==13.0.1 ffmpy websockets
)

echo [2/3] Po hap dritaren e lojes...
start "" cmd /c "timeout /t 4 /nobreak >nul && start msedge --app=http://localhost:8000 --window-size=540,960"

echo [3/3] Po nis lidhjen me TikTok. Live-i duhet te jete i hapur te TikTok LIVE Studio.
if /i "%TTUSER%"=="demo" (
  %PY% server.py --demo
) else (
  %PY% server.py --user %TTUSER%
)
echo.
echo Serveri u ndal. Nese ppa gabim me siper, live-i ndoshta nuk ishte i hapur ^(user offline^).
pause
