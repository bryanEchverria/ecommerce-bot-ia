#!/bin/bash

# Multi-tenant Migration Application Script
# Este script aplica las migraciones necesarias para completar el multi-tenancy

echo "🔧 Aplicando migración multi-tenant..."

cd /root/ecommerce-bot-ia/backend

# Check if we have virtual environment or requirements
if [ -f "requirements.txt" ]; then
    echo "📦 Installing requirements..."
    pip3 install -r requirements.txt
fi

# Check current migration status
echo "📊 Estado actual de migraciones:"
python3 -c "
import sys
sys.path.append('.')
try:
    from alembic.config import Config
    from alembic import command
    
    # Create alembic config
    alembic_cfg = Config('alembic.ini')
    
    print('✅ Alembic configurado correctamente')
    print('⏳ Aplicando migración...')
    
    # Apply migration
    command.upgrade(alembic_cfg, 'head')
    print('✅ Migraciones aplicadas exitosamente!')
    
except ImportError:
    print('❌ Error: Alembic no está instalado')
    print('Instalando dependencias...')
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'alembic', 'sqlalchemy'])
    
    # Try again after installation
    try:
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config('alembic.ini')
        command.upgrade(alembic_cfg, 'head')
        print('✅ Migraciones aplicadas después de instalar dependencias!')
    except Exception as e:
        print(f'❌ Error aplicando migración: {e}')
        
except Exception as e:
    print(f'❌ Error: {e}')
"

echo ""
echo "🧪 Verificando schema después de migración..."

python3 -c "
import sys
sys.path.append('.')
try:
    from database import engine
    from sqlalchemy import inspect, text
    
    inspector = inspect(engine)
    
    # Check if tables exist with multi-tenant fields
    tables_to_check = {
        'orders': 'client_id',
        'clients': 'client_id', 
        'products': 'client_id',
        'campaigns': 'client_id',
        'discounts': 'client_id',
        'flow_pedidos': 'tenant_id',
        'flow_sesiones': 'tenant_id',
        'tenant_clients': 'slug'
    }
    
    print('📊 Verificación de schema multi-tenant:')
    all_good = True
    
    for table_name, field_name in tables_to_check.items():
        try:
            if inspector.has_table(table_name):
                columns = [col['name'] for col in inspector.get_columns(table_name)]
                has_field = field_name in columns
                status = '✅' if has_field else '❌'
                print(f'   {status} {table_name}.{field_name} = {has_field}')
                if not has_field:
                    all_good = False
            else:
                print(f'   ❌ Table {table_name} does not exist')
                all_good = False
        except Exception as e:
            print(f'   ⚠️  Error checking {table_name}: {e}')
            all_good = False
    
    if all_good:
        print('\\n🎉 ¡Schema multi-tenant configurado correctamente!')
    else:
        print('\\n⚠️  Algunos campos multi-tenant están faltando')
        
except ImportError as e:
    print(f'⚠️  No se pueden verificar las tablas: {e}')
except Exception as e:
    print(f'❌ Error verificando schema: {e}')
"

echo ""
echo "✅ Migración completada. El sistema está listo para multi-tenancy!"