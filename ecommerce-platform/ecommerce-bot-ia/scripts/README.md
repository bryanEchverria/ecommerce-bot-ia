# Scripts Directory

Este directorio contiene scripts de utilidad, configuración y testing del proyecto.

## 📋 Tipos de Scripts

### Scripts de Creación
- `create_orders_*.py` - Creación de órdenes de prueba
- `create_tenant_orders_*.py` - Órdenes específicas por tenant
- `crear_*.py` - Scripts de creación de datos

### Scripts de Debug
- `debug_*.py` - Scripts para debugging
- `fix_*.py` - Scripts de corrección
- `verificacion_*.py` - Scripts de verificación

### Scripts de Configuración
- `agregar_*.py` - Scripts para agregar datos
- `update_*.py` - Scripts de actualización
- `cleanup_*.py` - Scripts de limpieza

### Scripts de Testing
- `probar_*.py` - Scripts de pruebas específicas
- `flujo_*.py` - Scripts de flujo completo
- `verify_*.py` - Scripts de verificación

## 🎯 Scripts Importantes

### Configuración de Productos
```bash
python agregar_productos_originales.py
```

### Crear Órdenes de Prueba
```bash
python create_orders_simple.py
python create_tenant_orders_mundo_canino.py
```

### Verificación del Sistema
```bash
python verificacion_final.py
python verificacion_dos_clientes.py
```

## ⚠️ Nota

Estos scripts fueron utilizados durante el desarrollo y testing del sistema multi-tenant. La mayoría son para propósitos de debugging y configuración inicial.