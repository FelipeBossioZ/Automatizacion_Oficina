@echo off
chcp 65001 >nul
color 0E
title 🔍 Verificación de Instalación

echo.
echo ═══════════════════════════════════════════════════════════════
echo     🔍 VERIFICACIÓN DE INSTALACIÓN
echo ═══════════════════════════════════════════════════════════════
echo.

set ERRORES=0

:: Verificar Python
echo [1/7] Verificando Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✅ Python instalado
    python --version
) else (
    echo     ❌ Python NO instalado
    set /a ERRORES+=1
)
echo.

:: Verificar dependencias
echo [2/7] Verificando Flask...
python -c "import flask" >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✅ Flask instalado
) else (
    echo     ❌ Flask NO instalado
    set /a ERRORES+=1
)
echo.

echo [3/7] Verificando OpenPyXL...
python -c "import openpyxl" >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✅ OpenPyXL instalado
) else (
    echo     ❌ OpenPyXL NO instalado
    set /a ERRORES+=1
)
echo.

echo [4/7] Verificando Python-DateUtil...
python -c "import dateutil" >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✅ Python-DateUtil instalado
) else (
    echo     ❌ Python-DateUtil NO instalado
    set /a ERRORES+=1
)
echo.

:: Verificar estructura de carpetas
echo [5/7] Verificando estructura de carpetas...
if exist "SISTEMA_CONTABLE" (
    echo     ✅ Carpeta SISTEMA_CONTABLE existe
) else (
    echo     ❌ Carpeta SISTEMA_CONTABLE NO existe
    set /a ERRORES+=1
)
echo.

:: Verificar base de datos
echo [6/7] Verificando base de datos...
if exist "SISTEMA_CONTABLE\DATOS\contabilidad.db" (
    echo     ✅ Base de datos existe
) else (
    echo     ⚠️ Base de datos NO existe (debes crearla)
)
echo.

:: Verificar scripts
echo [7/7] Verificando scripts importantes...
set SCRIPTS_OK=0
if exist "migrar_base_datos.py" set /a SCRIPTS_OK+=1
if exist "migrar_templates_presupuestos.py" set /a SCRIPTS_OK+=1
if exist "crear_presupuestos_automaticos.py" set /a SCRIPTS_OK+=1
if exist "backup_automatico.py" set /a SCRIPTS_OK+=1
if exist "exportar_excel.py" set /a SCRIPTS_OK+=1

echo     ✅ %SCRIPTS_OK%/5 scripts encontrados
echo.

:: Resumen
echo ═══════════════════════════════════════════════════════════════
echo     📊 RESUMEN
echo ═══════════════════════════════════════════════════════════════
echo.

if %ERRORES% equ 0 (
    echo ✅ TODO CORRECTO - El sistema está listo para usar
    echo.
    echo Puedes iniciar el servidor ejecutando: iniciar_servidor.bat
) else (
    echo ❌ Se encontraron %ERRORES% errores
    echo.
    echo Por favor, ejecuta: instalacion_automatica.bat
)
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

pause