@echo off
chcp 65001 > nul
cd /d "%~dp0"
cls
echo ===================================================
echo    INSTALADOR Y CONFIGURADOR: PUBLICAR POWER GYM
echo ===================================================

:: 1. Crear entorno virtual si no existe
if not exist venv (
    echo [+] Creando entorno virtual de Python...
    python -m venv venv
)

:: 2. Activar entorno e instalar dependencias
echo [+] Verificando e instalando librerias...
call venv\Scripts\activate
python -m pip install --upgrade pip > nul
if exist requirements.txt (
    pip install -r requirements.txt
)

:: 3. Abrir el configurador visual (Grupos + Promociones 1, 2, 3...)
echo.
echo [+] Abriendo asistente visual de configuracion...
python configurar_todo.py

:: 4. Procesar los grupos al archivo grupos.csv
if exist obtener_grupos.py (
    echo [+] Actualizando base de datos grupos.csv...
    python obtener_grupos.py
)

echo.
echo ===================================================
echo [OK] ¡TODO LISTO PARA PUBLICAR!
echo ===================================================
pause
