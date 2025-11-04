@echo off
chcp 65001 >nul
color 0B
title 🚀 Sistema Contable - Servidor

echo.
echo ═══════════════════════════════════════════════════════════════
echo     🚀 SISTEMA CONTABLE - INICIANDO SERVIDOR
echo ═══════════════════════════════════════════════════════════════
echo.

:: Verificar que estamos en la carpeta correcta
if not exist "SISTEMA_CONTABLE" (
    echo ❌ Error: No se encuentra la carpeta SISTEMA_CONTABLE
    echo.
    echo Por favor, ejecuta este script desde la raíz del proyecto
    echo.
    pause
    exit /b 1
)

:: Verificar que existe la base de datos
if not exist "SISTEMA_CONTABLE\DATOS\contabilidad.db" (
    echo ⚠️ Advertencia: No se encuentra la base de datos
    echo.
    echo ¿Quieres crearla ahora? (S/N)
    set /p CREAR="Respuesta: "
    
    if /i "%CREAR%"=="S" (
        echo.
        echo Creando base de datos...
        python migrar_base_datos.py
        python migrar_templates_presupuestos.py
        echo.
        echo ✅ Base de datos creada
        echo.
    ) else (
        echo.
        echo No se puede iniciar sin base de datos
        pause
        exit /b 1
    )
)

echo ✅ Base de datos encontrada
echo.
echo ═══════════════════════════════════════════════════════════════
echo     📡 Iniciando servidor Flask...
echo ═══════════════════════════════════════════════════════════════
echo.
echo El servidor se iniciará en: http://localhost:8000
echo.
echo ⚠️ IMPORTANTE:
echo   - NO CIERRES esta ventana mientras uses el sistema
echo   - Para detener el servidor, presiona CTRL+C
echo   - Los otros PCs pueden acceder usando la IP del servidor
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

pause

cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo     🟢 SERVIDOR EN EJECUCIÓN
echo ═══════════════════════════════════════════════════════════════
echo.
echo Acceder desde este PC: http://localhost:8000
echo.
echo Para acceder desde otros PCs en la red:
echo   1. Abre CMD en este PC y ejecuta: ipconfig
echo   2. Busca tu IP (Ej: 192.168.1.105)
echo   3. En otros PCs abre: http://[TU_IP]:8000
echo.
echo PIN del sistema: 0000
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

python SISTEMA_CONTABLE\MODULOS\panel_control\app.py

echo.
echo.
echo ═══════════════════════════════════════════════════════════════
echo     ⚠️ SERVIDOR DETENIDO
echo ═══════════════════════════════════════════════════════════════
echo.
echo El servidor se ha detenido.
echo.
pause