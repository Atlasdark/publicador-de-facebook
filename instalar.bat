@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Instalacion Power Gym
echo ============================================
echo   INSTALACION - Power Gym (ayudantes)
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [X] No encuentro Python en esta computadora.
  echo     1. Descargalo de https://www.python.org/downloads/
  echo     2. Al instalar, MARCA la casilla "Add python.exe to PATH"
  echo     3. Vuelve a abrir este instalador.
  echo.
  pause
  exit /b 1
)

if not exist venv (
  echo [*] Creando entorno...
  python -m venv venv
  if errorlevel 1 (
    echo [X] No pude crear el entorno. Avisa a tu encargado.
    pause
    exit /b 1
  )
)

echo [*] Instalando programas necesarios (puede tardar un par de minutos)...
call venv\Scripts\activate.bat
python -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
  echo [X] Fallo la instalacion. Revisa tu internet y vuelve a intentar.
  pause
  exit /b 1
)

echo.
echo Cual es tu numero de persona? (el encargado te lo dira: 1, 2, 3 o 4)
choice /c 1234 /n /m "Numero: "
set NUM=%errorlevel%
if not exist data mkdir data
>data\ayudante.txt echo %NUM%/4
echo [OK] Quedaste como persona %NUM% de 4.

echo [*] Creando acceso directo en el escritorio...
powershell -NoProfile -Command "$ws=New-Object -ComObject WScript.Shell; $d=[Environment]::GetFolderPath('Desktop'); $l=$ws.CreateShortcut($d+'\Publicar Power Gym.lnk'); $l.TargetPath='%~dp0Publicar Power Gym.bat'; $l.WorkingDirectory='%~dp0'; if(Test-Path '%~dp0power_gym.ico'){$l.IconLocation='%~dp0power_gym.ico'}; $l.Save()"

echo.
echo ============================================
echo   LISTO. En el escritorio tienes el acceso
echo   "Publicar Power Gym". Lee LEEME.txt.
echo ============================================
pause
