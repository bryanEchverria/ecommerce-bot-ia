# 🔗 Sistema de Drag & Drop para Integración de Queries con Prompts

## 📋 Resumen
Sistema completo que permite arrastrar y soltar configuraciones de queries SQL directamente en el prompt del bot para generar automáticamente instrucciones inteligentes.

## 🎯 Funcionalidades Principales

### 1. **Menú Vertical de Queries** (Pestaña Configuración)
- **Ubicación**: Panel izquierdo en la pestaña "⚙️ Configuración"
- **Elementos arrastrables**:
  - 📦 **Productos** (verde): Consultas de inventario y catálogo
  - 📢 **Campañas** (morado): Promociones activas
  - 💰 **Descuentos** (naranja): Ofertas vigentes

### 2. **Zona de Drop Inteligente**
- **Ubicación**: Textarea del "Prompt del Sistema"
- **Funcionalidad**: 
  - Detecta cuando se arrastra una query
  - Muestra feedback visual con overlay
  - Inserta automáticamente texto personalizado

### 3. **Configuración de Queries** (Pestaña Base de Datos)
- Activación/desactivación de queries
- Configuración de SQL templates
- Pruebas en tiempo real con datos reales
- Validación de parámetros

## 🛠️ Arquitectura Técnica

### Frontend (`BotConfigurationWithChat.tsx`)
```typescript
// Estados del drag & drop
const [draggedQuery, setDraggedQuery] = useState<string>('');

// Funciones principales
handleDragStart(e, queryType) // Inicia el arrastre
handleDragOver(e)            // Permite el drop
handleDrop(e)                // Procesa el drop e inserta texto
```

### Backend
- **`prompt_schemas.py`**: Validación de configuraciones
- **`dynamic_database_service.py`**: Ejecución segura de queries
- **`bot_prompt_integration.py`**: Generación de instrucciones automáticas
- **`tenant_prompt_cache.py`**: Cache con prompts enriquecidos

## 📝 Templates de Texto Generados

Cuando arrastras una query, se genera texto como:

### Ejemplo - Query de Productos:
```
Eres un asistente especializado de [Cliente]. Con la query de productos configurada vas a recorrer todos los productos disponibles y dar una respuesta según lo que el cliente quiera consultar.

Cuando el cliente pregunte sobre productos, utiliza la información actualizada de la base de datos para:
- Mostrar productos disponibles con precios y stock real
- Buscar por categorías específicas que el cliente solicite
- Recomendar productos relacionados o alternativos
- Informar sobre disponibilidad y características

Siempre proporciona información precisa basada en los datos actuales del inventario.
```

## 🎨 Flujo de Uso

1. **Configurar Queries**: 
   - Ve a "🗃️ Base de Datos"
   - Activa las queries que necesites
   - Configura SQL templates y parámetros

2. **Probar Queries**:
   - Usa la interfaz de pruebas
   - Valida que retornen datos correctos

3. **Integrar con Prompts**:
   - Ve a "⚙️ Configuración"  
   - Arrastra queries del menú izquierdo
   - Suelta en el textarea del prompt
   - Se inserta automáticamente el texto

4. **Guardar y Probar**:
   - Guarda la configuración
   - Prueba en "💬 Prueba Interactiva"

## 🔧 Configuraciones Disponibles

### Opciones de Tono:
- `amigable` - Tono cordial y cercano
- `super_amigable` - Muy amistoso con emojis
- `profesional` - Formal y experto
- `casual` - Relajado e informal
- `formal` - Estricto y protocolario
- `experto` - Técnico y especializado

### Tipos de Query:
- **Productos**: Inventario, precios, stock, categorías
- **Campañas**: Promociones, fechas, beneficios
- **Descuentos**: Ofertas, porcentajes, condiciones

## 🚀 Beneficios

1. **Simplicidad**: Drag & drop visual e intuitivo
2. **Automatización**: Genera instrucciones complejas automáticamente
3. **Consistencia**: Templates estandarizados para cada tipo de query
4. **Flexibilidad**: Combinar múltiples queries en un solo prompt
5. **Tiempo Real**: Datos siempre actualizados de la base de datos

## 🔍 Endpoints Clave

- `POST /api/tenants/{tenant_id}/prompt` - Guardar configuración
- `POST /debug/test-db-queries` - Probar queries
- `GET /api/tenants/{tenant_id}/prompt` - Cargar configuración

## 📱 Acceso al Sistema

**URL**: http://localhost:8081 (o https://acme.sintestesia.cl en producción)

1. Iniciar sesión con credenciales del tenant
2. Navegar a "Configuración del Bot"
3. ¡El menú vertical estará visible en la pestaña "Configuración"!

---
*Sistema implementado y funcional - Septiembre 2024*