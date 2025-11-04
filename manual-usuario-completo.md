# 📊 MANUAL DE USUARIO - SISTEMA CONTABLE

## 🎯 INICIO RÁPIDO

### Acceder al Sistema

**En el PC Servidor:**
- Abrir navegador → `http://localhost:8000`

**En otros PCs de la oficina:**
- Abrir navegador → `http://192.168.1.105:8000`
- (Usar la IP del servidor)

---

## 📁 MÓDULOS DEL SISTEMA

### 1️⃣ DASHBOARD (Página Principal)

**¿Qué muestra?**
- 🚨 Gastos vencidos
- ⏰ Gastos que vencen hoy
- ⚠️ Alertas críticas (próximos 3 días)
- 📊 Estadísticas del mes
- 💡 Alertas de tendencias de presupuestos

**Acciones rápidas:**
- Ver detalles de cada gasto
- Navegar a otros módulos

---

### 2️⃣ GESTIÓN DE GASTOS

#### **Crear un Gasto Nuevo**

1. Click en "Gestión de Gastos"
2. Bajar hasta "➕ Añadir Nuevo Gasto"
3. Completar formulario:
   - Descripción: "Nómina Noviembre 2025"
   - Monto: 3600000
   - Fecha de vencimiento: 2025-11-30
   - Categoría: Seleccionar (Nómina, Arriendo, etc.)
   - Etiqueta: OFICINA o GTFF
4. **Opcional:** Activar descuento
   - ☑ Marcar "Tiene descuento por pronto pago"
   - Fecha límite: 2025-11-25
   - Porcentaje: 5%
5. **Opcional:** Marcar como recurrente
   - ☑ Marcar "Este gasto es recurrente"
   - Frecuencia: Mensual
6. Click "✅ Añadir Gasto"

#### **Pagar un Gasto**

1. Buscar el gasto en la lista
2. Click "💵 Marcar como Pagado"
3. Se actualizará automáticamente:
   - Estado cambia a "Pagado"
   - Si es recurrente, se crea el siguiente mes
   - Los presupuestos se actualizan

#### **Editar un Gasto**

1. Click "✏️ Editar"
2. Modificar los campos necesarios
3. Click "💾 Guardar Cambios"

#### **Eliminar un Gasto**

1. Click "🗑️ Eliminar"
2. Confirmar eliminación
3. Se borra permanentemente

#### **Filtros Disponibles**

- **Por Etiqueta:** TODOS, OFICINA, GTFF
- **Por Estado:** TODOS, Pendiente, Pagado
- **Por Mes:** Seleccionar mes específico

---

### 3️⃣ PRESUPUESTOS

#### **PESTAÑA 1: MES ACTUAL**

**Ver Presupuestos del Mes:**
- Muestra todos los presupuestos de este mes
- Barra de progreso visual
- Monto gastado vs presupuestado

**Crear Presupuesto Nuevo:**

1. Ir a "➕ Crear Nuevo Presupuesto"
2. Seleccionar:
   - Categoría: Nómina, Arriendo, etc.
   - Etiqueta: OFICINA o GTFF
   - Monto Presupuestado: 3600000
3. Click "✅ Crear Presupuesto"

**Editar Presupuesto (Solo mes actual):**

1. Click "✏️ Editar"
2. Modificar el monto presupuestado
3. **Nota:** No afecta el template original
4. Click "💾 Guardar Cambios"

**Eliminar Presupuesto:**

1. Click "🗑️ Eliminar"
2. **Si tiene gastos:** Ingresar PIN (0000)
3. **Si no tiene gastos:** Se elimina directamente

---

#### **PESTAÑA 2: TEMPLATES**

**¿Qué son los Templates?**
- Configuraciones maestras que crean presupuestos automáticamente cada mes

**Crear Template Nuevo:**

1. Bajar a "➕ Crear Nuevo Template"
2. Configurar:
   - Categoría: Nómina
   - Etiqueta: OFICINA
   - Monto Base: 3600000
   - **Opcional:** Meses especiales
     - Febrero (Cesantías): 4200000
     - Junio (Prima): 4100000
     - Diciembre (Liquidaciones): 4500000
   - Observaciones: "Incluye bonos"
3. Click "✅ Crear Template"

**¿Qué pasa después?**
- El día 1 de cada mes se crea automáticamente
- Usa el monto base (10 meses)
- Usa montos especiales en Feb/Jun/Dic

**Editar Template:**

1. Click "✏️ Editar"
2. Modificar montos
3. **Importante:** Los cambios aplican desde el próximo mes
4. Click "💾 Guardar Cambios"

**Pausar/Reactivar Template:**

1. Click "⏸️ Pausar" o "▶️ Activar"
2. **Pausado:** No crea más presupuestos
3. **Activo:** Sigue creando cada mes

**Eliminar Template:**

1. Click "🗑️ Eliminar"
2. Confirmar
3. **Nota:** No afecta presupuestos ya creados

---

#### **PESTAÑA 3: CATEGORÍAS**

**Ver Categorías Existentes:**
- Lista de todas las categorías
- Estado: Activa o Inactiva

**Crear Categoría Nueva:**

1. Bajar a "➕ Crear Nueva Categoría"
2. Nombre: "Publicidad"
3. Click "✅ Crear Categoría"

**Desactivar/Activar Categoría:**

1. Click "❌ Desactivar" o "✅ Activar"
2. Confirmar
3. **Desactivada:** No aparece en formularios
4. **Activa:** Disponible para usar

---

### 4️⃣ TAREAS

**Crear Tarea:**

1. Click en "Tareas"
2. Ir a "➕ Crear Nueva Tarea"
3. Completar:
   - Descripción: "Revisar cuentas bancarias"
   - Fecha vencimiento: 2025-11-10
   - Prioridad: Alta/Media/Baja
   - Categoría: Interno/Externo
   - Cliente: (opcional)
4. Click "✅ Crear Tarea"

**Completar Tarea:**

1. Click "✅ Completar"
2. Se marca como completada
3. Desaparece de la lista de pendientes

**Filtrar Tareas:**

- Por estado: Pendiente / Completada / Todas

---

## 🔄 AUTOMATIZACIÓN

### ¿Cómo Funciona?

**Día 1 de cada mes a las 6:00 AM:**
1. ✅ El sistema lee todos los templates activos
2. ✅ Verifica si es mes especial (Feb/Jun/Dic)
3. ✅ Crea presupuestos automáticamente
4. ✅ Calcula montos ya gastados
5. ✅ Los presupuestos aparecen en "Mes Actual"

### Ejecutar Manualmente

Si necesitas crear presupuestos fuera de la fecha programada:

**En el PC Servidor:**

1. Abrir CMD en la carpeta del proyecto
2. Ejecutar:
```bash
python crear_presupuestos_automaticos.py
```

---

## 💡 FLUJO DE TRABAJO RECOMENDADO

### **CONFIGURACIÓN INICIAL (Una vez)**

**Semana 1:**
1. ✅ Crear todas las categorías necesarias
2. ✅ Configurar templates para cada presupuesto recurrente
3. ✅ Verificar que la automatización funcione

**Ejemplo de Templates:**
- Nómina - OFICINA: $3,600,000
- Arriendo - OFICINA: $2,500,000
- Servicios - OFICINA: $400,000
- Internet - OFICINA: $180,000
- Cafetería - OFICINA: $200,000

---

### **USO DIARIO**

**Por la mañana:**
1. ✅ Revisar dashboard
2. ✅ Ver alertas de gastos vencidos
3. ✅ Verificar descuentos por vencer

**Cuando llega una factura:**
1. ✅ Ir a "Gestión de Gastos"
2. ✅ Crear el gasto nuevo
3. ✅ Si tiene descuento, configurarlo

**Cuando se paga:**
1. ✅ Marcar como pagado
2. ✅ El presupuesto se actualiza solo

---

### **REVISIÓN MENSUAL**

**Fin de mes:**
1. ✅ Ir a "Presupuestos"
2. ✅ Revisar cumplimiento por categoría
3. ✅ Ver alertas de tendencias
4. ✅ Ajustar templates si es necesario

**Ejemplo de decisión:**
- Cafetería lleva 3 meses excediendo +20%
- Sugerencia: Aumentar template de $200K a $240K

---

## 🚨 SOLUCIÓN DE PROBLEMAS

### **Problema 1: No puedo acceder desde otro PC**

**Solución:**
1. Verificar que el servidor esté corriendo
2. Usar la IP correcta (192.168.X.X:8000)
3. Verificar firewall del PC servidor
4. Asegurarse que ambos PCs estén en la misma red

---

### **Problema 2: Los presupuestos no se actualizan**

**Solución:**
1. Verificar que el gasto esté marcado como "Pagado"
2. Verificar que la categoría coincida exactamente
3. Verificar que la etiqueta coincida
4. Refrescar la página (F5)

---

### **Problema 3: No se crearon presupuestos automáticamente**

**Solución:**
1. Verificar que existan templates activos
2. Verificar que la tarea programada esté activa
3. Ejecutar manualmente: `python crear_presupuestos_automaticos.py`
4. Revisar si ya existían presupuestos del mes

---

### **Problema 4: Error al eliminar presupuesto**

**Solución:**
1. Si tiene gastos, usar PIN: 0000
2. Verificar que estás en el mes actual (solo se puede editar/eliminar el actual)

---

### **Problema 5: El servidor se detiene solo**

**Solución:**
1. Crear el archivo `.bat` de inicio automático
2. Configurarlo en el inicio de Windows
3. O mantener la ventana CMD abierta (minimizada)

---

## 📊 CONCEPTOS CLAVE

### **Categoría vs Etiqueta**

**Categoría:** Tipo de gasto
- Ejemplos: Nómina, Arriendo, Servicios

**Etiqueta:** Área o proyecto
- OFICINA: Gastos de la oficina principal
- GTFF: Gastos del grupo de trabajo

### **Template vs Presupuesto**

**Template:** Configuración maestra
- Se crea UNA vez
- Genera presupuestos automáticamente
- Cambios afectan meses futuros

**Presupuesto:** Instancia mensual
- Se crea cada mes (automático o manual)
- Cambios solo afectan ese mes
- Rastrea gastos vs presupuestado

### **Presupuesto Gastado**

- Se calcula automáticamente
- Suma de todos los gastos PAGADOS del mes
- Se actualiza en tiempo real al pagar

---

## 🎯 MEJORES PRÁCTICAS

### **✅ HACER:**

1. ✅ Crear templates para gastos recurrentes
2. ✅ Marcar gastos como pagados inmediatamente
3. ✅ Configurar descuentos cuando apliquen
4. ✅ Revisar dashboard diariamente
5. ✅ Ajustar templates basándose en tendencias
6. ✅ Mantener categorías organizadas

### **❌ NO HACER:**

1. ❌ Crear presupuestos manualmente si existe template
2. ❌ Olvidar marcar gastos como pagados
3. ❌ Ignorar alertas de tendencias
4. ❌ Crear múltiples categorías similares
5. ❌ Editar presupuestos de meses pasados
6. ❌ Desactivar templates sin razón

---

## 📞 CONTACTO Y SOPORTE

Para dudas o problemas:
- Revisar este manual primero
- Consultar sección "Solución de Problemas"
- Ejecutar scripts de prueba

---

## 📋 CHECKLIST DE CONFIGURACIÓN

### **Configuración Inicial del Sistema**

- [ ] Sistema instalado en PC servidor
- [ ] Firewall configurado (puerto 8000)
- [ ] IP del servidor anotada
- [ ] Accesos directos creados en todos los PCs
- [ ] Probado acceso desde los 3 PCs

### **Configuración de Datos**

- [ ] Todas las categorías creadas
- [ ] Templates configurados
- [ ] Montos especiales configurados (Feb/Jun/Dic)
- [ ] Primer mes de presupuestos creado

### **Configuración de Automatización**

- [ ] Script probado manualmente
- [ ] Tarea programada configurada
- [ ] Tarea probada con "Ejecutar"
- [ ] Script de inicio automático configurado (opcional)

### **Pruebas Finales**

- [ ] Crear un gasto de prueba
- [ ] Marcarlo como pagado
- [ ] Verificar que presupuesto se actualizó
- [ ] Crear un template de prueba
- [ ] Ejecutar script de creación
- [ ] Eliminar datos de prueba

---

## 🎉 ¡LISTO PARA USAR!

Tu sistema está completamente configurado y listo para gestionar la contabilidad de tu oficina.

**Recuerda:**
- El día 1 de cada mes se crean presupuestos automáticamente
- Los presupuestos se actualizan al marcar gastos como pagados
- Las alertas te avisan de tendencias y gastos críticos
- Todo está centralizado y accesible desde cualquier PC

---

**Última actualización:** Noviembre 2025
**Versión:** 1.0
