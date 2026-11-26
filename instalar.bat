@echo off
cd /d "%~dp0"
cls
echo ===================================================
echo    CONFIGURANDO AUTOMATICAMENTE: PUBLICAR POWER GYM
echo ===================================================

:: 1. Crear entorno virtual si no existe
if not exist venv (
    echo [+] Creando entorno virtual de Python...
    python -m venv venv
)

:: 2. Activar entorno e instalar dependencias
echo [+] Instalando librerias necesarias...
call venv\Scripts\activate
python -m pip install --upgrade pip
if exist requirements.txt (
    pip install -r requirements.txt
)

:: 3. Crear carpetas necesarias automaticamente
echo [+] Creando carpetas de trabajo (data y media)...
if not exist data mkdir data
if not exist media mkdir media

:: 4. Crear plantillas iniciales si no existen
if not exist data\lista_grupos.txt (
    echo # Pega tus grupos aqui un enlace por linea: > data\lista_grupos.txt
    echo # https://www.facebook.com/groups/123456789/ >> data\lista_grupos.txt
    echo [+] Se creo la plantilla vacia: data\lista_grupos.txt
)

if not exist data\spintax.txt (
    echo === > data\spintax.txt
    echo ¡Hola! {Aprovecha|No te pierdas} nuestra promo de hoy. ^| @imagen: promo.jpg >> data\spintax.txt
    echo === >> data\spintax.txt
    echo [+] Se creo la plantilla de anuncios: data\spintax.txt
)

:: 5. Ejecutar script para generar grupos.csv inicial si existe el archivo de procesamiento
if exist obtener_grupos.py (
    echo [+] Generando archivo grupos.csv inicial...
    python obtener_grupos.py
)

echo.
echo ===================================================
echo [OK] ¡INSTALACION Y CONFIGURACION COMPLETADAS!
echo ===================================================
echo - Tus grupos van en: data\lista_grupos.txt
echo - Tus anuncios van en: data\spintax.txt
echo - Tus imagenes van en la carpeta: media\
echo.
pause
