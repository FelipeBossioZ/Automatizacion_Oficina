
# SUPERGUÍA: Sistema Integral de Automatización Contable

¡Bienvenido a tu nuevo centro de mando! Esta guía es el manual de operaciones definitivo para el sistema que estamos construyendo juntos. Aquí encontrarás desde la visión estratégica hasta el paso a paso detallado para usar cada herramienta.

---

## 1. El "PLAN MAESTRO" - Nuestra Visión Estratégica

**Objetivo:** Crear un sistema local 100% gratuito que automatice el 90% de los procesos manuales de gestión contable, con máxima flexibilidad y capacidad de personalización.

**Filosofía:** Construcción modular e incremental. Cada nuevo módulo se apoya en el anterior, creando un sistema cada vez más potente y cohesionado.

**Arquitectura General:**
*   **Aplicación Central:** Un "Panel de Control Unificado" (aplicación web local) que sirve como punto de acceso para todos los módulos y usuarios.
*   **Base de Datos Única:** Un archivo `contabilidad.db` (SQLite) que actúa como el "único punto de verdad" para toda la información de la oficina (clientes, facturas, gastos, etc.).
*   **Módulos Interconectados:**
    *   Módulo de Declaraciones (Completado)
    *   Módulo de Cuentas por Cobro (CxC) (Completado)
    *   Panel de Control Unificado (Fase 2 Completada)
        *   Gestión de Egresos
        *   Dashboard de Alertas Proactivas
    *   Módulo de Tareas Rápidas (Próximo)
    *   Módulo de Tesorería (Futuro)
    *   Módulo de Reportes (Futuro)

---

## 2. Puesta en Marcha Inicial (Solo se hace una vez)

Estos son los pasos para preparar cualquier computador de la oficina para que pueda ejecutar o acceder al sistema.

### 2.1. Instalar Python
Asegúrate de que Python 3 está instalado. Puedes descargarlo desde [python.org](https://www.python.org/downloads/).

### 2.2. Instalar las Librerías Necesarias
Abre una terminal (CMD, PowerShell, etc.) y ejecuta el siguiente comando. Esto instalará todas las "herramientas" que nuestro sistema necesita para funcionar.

```bash
pip install pandas openpyxl reportlab Flask
```

---

## 3. Módulo 1: Automatización de Declaraciones

**Objetivo:** Generar el archivo "Relación" a partir del "Excel Pesado" de declaraciones.

### Cómo se Usa:

1.  **Prepara el Archivo:** Coloca tu archivo "Excel Pesado" en la carpeta `SISTEMA_CONTABLE/DATOS/` y asegúrate de que se llame `declaracion_completa.xlsx`.
2.  **Ejecuta el Script:** Abre una terminal, navega a la raíz del proyecto y ejecuta:
    ```bash
    python3 SISTEMA_CONTABLE/main.py
    ```
3.  **Recoge el Resultado:** El archivo `Relacion_Generada_[...].xlsx` aparecerá en la carpeta `SISTEMA_CONTABLE/DATOS/Salidas/Reportes/`.

---

## 4. Módulo 2: Automatización de Cuentas por Cobro (CxC)

**Objetivo:** Generar masivamente los PDFs de las cuentas de cobro y los borradores de correo listos para enviar.

### Cómo se Usa:

1.  **Prepara los Archivos:**
    *   Asegúrate de que tu archivo de control de cobros se llame `SISTEMA_DE_COBROS.xlsx` y esté en `SISTEMA_CONTABLE/DATOS/`.
    *   Asegúrate de que tu plantilla de cuenta de cobro se llame `FORMATO_PARA_CXC.xlsx` y esté en la misma carpeta.
2.  **Ejecuta el Módulo:** Abre una terminal, navega a la raíz del proyecto y ejecuta:
    ```bash
    python3 -m SISTEMA_CONTABLE.MODULOS.cxc.main_cxc
    ```
3.  **Recoge los Resultados:**
    *   Los PDFs de las cuentas de cobro aparecerán en `SISTEMA_CONTABLE/DATOS/Salidas/CuentasCobro_PDFs/`.
    *   Los borradores de correo (`.eml`) aparecerán en `SISTEMA_CONTABLE/DATOS/Salidas/Correos_Borradores/`. Haz doble clic en ellos para abrirlos en Outlook y enviarlos.

---

## 5. Módulo 3: El Panel de Control Unificado (¡El Nuevo Corazón!)

**Objetivo:** Gestionar los gastos de la oficina de forma colaborativa y recibir alertas proactivas sobre los pagos pendientes.

### Cómo se Pone en Marcha (cada vez que quieras usarlo):

1.  **Elige el PC "Servidor":** Decidan cuál de los 3 computadores actuará como el servidor principal (generalmente, el que está encendido más tiempo).
2.  **Inicia la Aplicación:** En ese PC "servidor", abre una terminal, navega a la raíz del proyecto y ejecuta:
    ```bash
    python3 SISTEMA_CONTABLE/MODULOS/panel_control/app.py
    ```
3.  **¡No cierres la terminal!** Mientras esa ventana esté abierta y ejecutando el comando, tu aplicación estará viva. Verás un mensaje como `* Running on http://0.0.0.0:8000/`.

### Cómo Acceder desde los 3 Computadores:

1.  **Encuentra la Dirección IP del Servidor:**
    *   En el PC "servidor", abre una **nueva** terminal (CMD) y escribe el comando `ipconfig`.
    *   Busca la línea que dice **"Dirección IPv4"**. Será un número como `192.168.1.10`. Esa es la dirección de tu servidor en la red de la oficina.

2.  **Accede desde el Navegador:**
    *   **En el PC servidor:** Abre tu navegador y ve a `http://localhost:8000`.
    *   **En los otros 2 PCs:** Abre el navegador y ve a `http://[LA_DIRECCIÓN_IP_DEL_SERVIDOR]:8000` (por ejemplo: `http://192.168.1.10:8000`).

### Funcionalidades Actuales:

*   **Dashboard de Alertas:** La página de inicio. Te muestra automáticamente los gastos que están por vencer o que ya se vencieron. Es tu centro de mando diario.
*   **Gestión de Gastos:** Accesible desde el menú de navegación. Aquí puedes:
    *   **Registrar nuevos gastos** usando el formulario.
    *   **Ver el historial completo** de gastos (incluyendo los que migramos del Excel).
    *   **Marcar un gasto como "Pagado"** usando el botón en la tabla. Esto lo eliminará automáticamente del Dashboard de Alertas para todos.

---

Este documento vivirá en el proyecto y lo actualizaremos a medida que vayamos añadiendo nuevas y potentes funcionalidades. ¡Felicidades por tu nuevo sistema!
