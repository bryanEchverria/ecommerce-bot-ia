# Gestión de Tenants Multi-Tenant

## Crear un nuevo cliente/tenant

### Uso del script automático:

```bash
cd /root/ecommerce-bot-ia/scripts
python3 create_new_tenant.py "Nombre Empresa" slug [email_admin]
```

### Ejemplos:

```bash
# Crear tenant básico
python3 create_new_tenant.py "Delta Corporation" delta

# Crear tenant con email específico
python3 create_new_tenant.py "Echo Industries" echo admin@echo-industries.com
```

### Lo que se crea automáticamente:

1. **Registro en tenant_clients** con slug único
2. **3 usuarios por defecto:**
   - Admin: admin@slug.com / admin123 (rol: admin)
   - Sales: sales@slug.com / sales123 (rol: user) 
   - Support: support@slug.com / support123 (rol: user)
3. **3 productos de ejemplo** con precios y stock
4. **3 descuentos de ejemplo** (porcentaje y fijo)
5. **Hashes bcrypt válidos** (evita errores de login)

### URLs automáticas generadas:

- **Backoffice:** `https://slug.sintestesia.cl/`
- **API:** `https://slug.sintestesia.cl/api/`
- **Webhook Twilio:** `https://slug.sintestesia.cl/bot/twilio/webhook`
- **Webhook Meta:** `https://slug.sintestesia.cl/bot/meta/webhook`

## Validaciones automáticas:

- ✅ Slug válido (2-20 chars, a-z, 0-9, -)
- ✅ Hashes bcrypt seguros
- ✅ Datos completos (sin NULLs problemáticos)
- ✅ Estructura consistente

## Mantenimiento:

### Listar todos los tenants:
```sql
SELECT slug, name, created_at FROM tenant_clients ORDER BY created_at;
```

### Verificar datos de un tenant:
```bash
# Reemplazar 'slug' por el slug del tenant
docker exec ecommerce-postgres psql -U ecommerce_user -d ecommerce_multi_tenant -c "
SELECT 'Products' as type, COUNT(*) as count FROM products WHERE client_id = (SELECT id FROM tenant_clients WHERE slug = 'slug')
UNION ALL
SELECT 'Discounts', COUNT(*) FROM discounts WHERE client_id = (SELECT id FROM tenant_clients WHERE slug = 'slug')  
UNION ALL
SELECT 'Users', COUNT(*) FROM tenant_users WHERE client_id = (SELECT id FROM tenant_clients WHERE slug = 'slug');
"
```

### Resetear contraseñas de un tenant:
```bash
# Si hay problemas de login, regenerar hashes:
python3 -c "
import bcrypt
passwords = ['admin123', 'sales123', 'support123']  
for pwd in passwords:
    hash_val = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f'{pwd}: {hash_val}')
"
```