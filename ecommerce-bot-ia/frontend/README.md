# Frontend - E-commerce Backoffice

Aplicación React para la gestión del backoffice de e-commerce.

## Inicio Rápido

```bash
# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev
```

La aplicación estará disponible en: http://localhost:5173

## Scripts Disponibles

```bash
npm run dev      # Modo desarrollo
npm run build    # Build para producción
npm run preview  # Preview del build
npm run lint     # Linter ESLint
```

## Estructura

```
frontend/
├── components/         # Componentes React
│   ├── Dashboard.tsx   # Panel principal
│   ├── Products.tsx    # Gestión de productos
│   ├── Campaigns.tsx   # Gestión de campañas
│   ├── Discounts.tsx   # Gestión de descuentos
│   ├── Orders.tsx      # Gestión de pedidos
│   ├── Clients.tsx     # Gestión de clientes
│   └── Toast.tsx       # Sistema de notificaciones
├── services/          # APIs y servicios
│   └── api.ts         # Cliente API
├── locales/          # Traducciones
│   ├── en/           # Inglés
│   └── es/           # Español
├── types.ts          # Tipos TypeScript
└── App.tsx           # Componente principal
```

## Características

### 🎨 Interfaz Moderna
- Diseño responsive con Tailwind CSS
- Tema oscuro moderno
- Animaciones suaves
- Componentes reutilizables

### 📊 Dashboard Interactivo
- Estadísticas en tiempo real
- Gráficos de tendencias con Recharts
- Filtros por período de tiempo
- Métricas de rendimiento

### 🛍️ Gestión Completa
- **Productos**: CRUD completo con sistema de descuentos
- **Campañas**: Marketing campaigns con métricas
- **Descuentos**: Sistema flexible de promociones
- **Pedidos**: Seguimiento y gestión de órdenes
- **Clientes**: Base de datos de clientes

### 🔔 Sistema de Notificaciones
- Notificaciones toast elegantes
- Confirmación de operaciones
- Alertas de errores
- Auto-dismiss y cierre manual

### 🌍 Internacionalización
- Soporte para español e inglés
- Cambio dinámico de idioma
- Formateo de fechas y monedas por región

### 💰 Multi-moneda
- Soporte para diferentes divisas
- Conversión automática
- Formateo localizado

## Configuración API

El frontend se conecta al backend en `http://127.0.0.1:8000/api`. 

Para cambiar la URL de la API, edita el archivo `services/api.ts`:

```typescript
const API_BASE_URL = 'http://127.0.0.1:8000/api';
```

## Variables de Entorno

Crea un archivo `.env.local` para configuraciones opcionales:

```env
VITE_GEMINI_API_KEY=tu_api_key_de_gemini
```

## Tecnologías

- **React 19** - Biblioteca de UI
- **TypeScript** - JavaScript tipado
- **Vite** - Herramienta de desarrollo
- **Tailwind CSS** - Framework CSS
- **Recharts** - Gráficos y visualizaciones
- **React Router** - Navegación
- **i18next** - Internacionalización
- **date-fns** - Manipulación de fechas