@echo off
chcp 65001 >nul
color 0A
title 🚀 Instalación Automática - Sistema Contable

echo.
echo ═══════════════════════════════════════════════════════════════
echo     🚀 INSTALACIÓN AUTOMÁTICA - SISTEMA CONTABLE
echo ═══════════════════════════════════════════════════════════════
echo.
echo Este script instalará todo lo necesario para el sistema.
echo.
pause

:: =========================================
:: PASO 1: Verificar Python
:: =========================================
echo.
echo ═══════════════════════════════════════════════════════════════
echo     📦 PASO 1: Verificando Python...
echo ═══════════════════════════════════════════════════════════════
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python NO está instalado
    echo.
    echo Por favor instala Python desde: https://www.python.org/downloads/
    echo Marca la opción "Add Python to PATH" durante la instalación
    echo.
    pause
    exit /b 1
)

echo ✅ Python instalado correctamente
python --version
echo.

:: =========================================
:: PASO 2: Verificar Git (solo si necesita clonar)
:: =========================================
echo.
echo ═══════════════════════════════════════════════════════════════
echo     📦 PASO 2: Verificando Git...
echo ═══════════════════════════════════════════════════════════════
echo.

git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Git NO está instalado
    echo Si ya tienes el repositorio, presiona cualquier tecla para continuar
    echo Si NO lo tienes, instala Git desde: https://git-scm.com/downloads
    pause
) else (
    echo ✅ Git instalado correctamente
    git --version
)
echo.

:: =========================================
:: PASO 3: Verificar si ya está en la carpeta del proyecto
:: =========================================
echo.
echo ═══════════════════════════════════════════════════════════════
echo     📂 PASO 3: Verificando carpeta del proyecto...
echo ═══════════════════════════════════════════════════════════════
echo.

if exist "SISTEMA_CONTABLE" (
    echo ✅ Ya estás en la carpeta del proyecto
    echo.
) else (
    echo ⚠️ No estás en la carpeta del proyecto
    echo.
    echo ¿Quieres clonar el repositorio ahora? (S/N)
    set /p CLONAR="Respuesta: "
    
    if /i "%CLONAR%"=="S" (
        echo.
        echo Clonando repositorio...
        git clone https://github.com/FelipeBossioZ/Automatizacion_Oficina.git
        if %errorlevel% neq 0 (
            echo ❌ Error al clonar el repositorio
            pause
            exit /b 1
        )
        cd Automatizacion_Oficina
        echo ✅ Repositorio clonado exitosamente
    ) else (
        echo.
        echo Por favor, ejecuta este script desde la carpeta del proyecto
        pause
        exit /b 1
    )
)
echo.

:: =========================================
:: PASO 4: Instalar dependencias
:: =========================================
echo.
echo ═══════════════════════════════════════════════════════════════
echo     📦 PASO 4: Instalando dependencias de Python...
echo ═══════════════════════════════════════════════════════════════
echo.
echo Instalando Flask, OpenPyXL y Python-DateUtil...
echo.

python -m pip install --upgrade pip
python -m pip install flask openpyxl python-dateutil

if %errorlevel% neq 0 (
    echo ❌ Error al instalar dependencias
    pause
    exit /b 1
)

echo.
echo ✅ Dependencias instaladas correctamente
echo.

:: Verificar instalación
echo Verificando instalación...
python -m pip list | findstr flask
python -m pip list | findstr openpyxl
python -m pip list | findstr python-dateutil
echo.

:: =========================================
:: PASO 5: Crear carpeta de datos si no existe
:: =========================================
echo.
echo ═══════════════════════════════════════════════════════════════
echo     📁 PASO 5: Verificando carpeta de datos...
echo ═══════════════════════════════════════════════════════════════
echo.

if not exist "SISTEMA_CONTABLE\DATOS" (
    mkdir "SISTEMA_CONTABLE\DATOS"
    echo ✅ Carpeta de datos creada
) else (
    echo ✅ Carpeta de datos ya existe
)
echo.

:: =========================================
:: PASO 6: Crear base de datos
:: =========================================
echo.
echo ═══════════════════════════════════════════════════════════════
echo     🗄️ PASO 6: Creando base de datos...
echo ═══════════════════════════════════════════════════════════════
echo.

if exist "SISTEMA_CONTABLE\DATOS\contabilidad.db" (
    echo ⚠️ La base de datos ya existe
    echo ¿Quieres recrearla? Esto BORRARÁ todos los datos. (S/N)
    set /p RECREAR="Respuesta: "
    
    if /i "%RECREAR%"=="S" (
        del "SISTEMA_CONTABLE\DATOS\contabilidad.db"
        echo Base de datos eliminada
    ) else (
        echo Manteniendo base de datos existente
        goto :SKIP_MIGRACION
    )
)

echo.
echo Ejecutando migración de base de datos...
python migrar_base_datos.py

if %errorlevel% neq 0 (
    echo ❌ Error al crear base de datos
    pause
    exit /b 1
)

echo.
echo ✅ Base de datos creada exitosamente
echo.

:SKIP_MIGRACION

:: =========================================
:: PASO 7: Crear tablas de presupuestos
:: =========================================
echo.
echo ═══════════════════════════════════════════════════════════════
echo     💰 PASO 7: Creando tablas de presupuestos...
echo ═══════════════════════════════════════════════════════════════
echo.

python migrar_templates_presupuestos.py

if %errorlevel% neq 0 (
    echo ❌ Error al crear tablas de presupuestos
    pause
    exit /b 1
)

echo.
echo ✅ Tablas de presupuestos creadas exitosamente
echo.

:: =========================================
:: PASO 8: Crear carpeta de backups
:: =========================================
echo.
echo ═══════════════════════════════════════════════════════════════
echo     💾 PASO 8: Creando carpeta de backups...
echo ═══════════════════════════════════════════════════════════════
echo.

if not exist "SISTEMA_CONTABLE\DATOS\BACKUPS" (
    mkdir "SISTEMA_CONTABLE\DATOS\BACKUPS"
    echo ✅ Carpeta de backups creada
) else (
    echo ✅ Carpeta de backups ya existe
)
echo.

:: =========================================
:: FINALIZACIÓN
:: =========================================
echo.
echo ═══════════════════════════════════════════════════════════════
echo     ✅ ¡INSTALACIÓN COMPLETADA!
echo ═══════════════════════════════════════════════════════════════
echo.
echo El sistema está listo para usar.
echo.
echo Para iniciar el servidor, ejecuta: iniciar_servidor.bat
echo O manualmente: python SISTEMA_CONTABLE\MODULOS\panel_control\app.py
echo.
echo Luego abre tu navegador en: http://localhost:8000
echo.
echo ═══════════════════════════════════════════════════════════════
echo     📋 INFORMACIÓN IMPORTANTE
echo ═══════════════════════════════════════════════════════════════
echo.
echo PIN del sistema: 0000
echo Puerto del servidor: 8000
echo.
echo Para crear datos de prueba:
echo   - Crear categorías en Presupuestos ^> Categorías
echo   - Crear templates en Presupuestos ^> Templates
echo   - Crear gastos en Gestión de Gastos
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

echo ¿Quieres iniciar el servidor ahora? (S/N)
set /p INICIAR="Respuesta: "

if /i "%INICIAR%"=="S" (
    echo.
    echo Iniciando servidor...
    echo.
    echo ⚠️ NO CIERRES esta ventana mientras uses el sistema
    echo Para detener el servidor, presiona CTRL+C
    echo.
    pause
    python SISTEMA_CONTABLE\MODULOS\panel_control\app.py
) else (
    echo.
    echo Puedes iniciar el servidor cuando quieras ejecutando: iniciar_servidor.bat
    echo.
)

pause