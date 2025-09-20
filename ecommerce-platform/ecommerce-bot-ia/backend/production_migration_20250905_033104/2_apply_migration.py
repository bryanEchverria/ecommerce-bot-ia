#!/usr/bin/env python3
"""
Apply tenant_id migration to PostgreSQL database
"""
import psycopg2
import os
import sys

DEFAULT_TENANT_ID = '00000000-0000-0000-0000-000000000001'

def get_postgres_connection():
    """Get PostgreSQL connection from environment or defaults"""
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5433")  # Docker compose port
    db_name = os.getenv("POSTGRES_DB", "ecommerce")
    db_user = os.getenv("POSTGRES_USER", "postgres") 
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        return conn
    except Exception as e:
        print(f"[ERROR] Cannot connect to PostgreSQL: {e}")
        print(f"[INFO] Connection details: host={db_host}:{db_port}, db={db_name}, user={db_user}")
        return None

def apply_postgres_migration():
    """Apply tenant_id migration to PostgreSQL"""
    conn = get_postgres_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("[INFO] Applying tenant_id migration to PostgreSQL...")
        
        # === ENABLE UUID EXTENSION ===
        print("[1/7] Enabling UUID extension...")
        try:
            cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
            print("  ✅ UUID extension enabled")
        except Exception as e:
            print(f"  ⚠️  UUID extension: {e}")

        # === CREATE WHATSAPP_SETTINGS TABLE ===
        print("[2/7] Creating whatsapp_settings table...")
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS whatsapp_settings (
                    id SERIAL PRIMARY KEY,
                    provider VARCHAR NOT NULL,
                    twilio_account_sid VARCHAR,
                    twilio_auth_token VARCHAR,
                    twilio_from VARCHAR,
                    meta_token VARCHAR,
                    meta_phone_number_id VARCHAR,
                    meta_graph_api_version VARCHAR DEFAULT 'v21.0',
                    is_active BOOLEAN DEFAULT TRUE,
                    tenant_id UUID,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            ''')
            print("  ✅ whatsapp_settings table created")
        except Exception as e:
            print(f"  ⚠️  whatsapp_settings: {e}")

        # === ADD TENANT_ID COLUMNS ===
        print("[3/7] Adding tenant_id columns...")
        
        # Check if tables exist first
        tables_to_modify = ['flow_sesiones', 'flow_pedidos']
        
        for table in tables_to_modify:
            try:
                # Check if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    )
                """, (table,))
                
                table_exists = cursor.fetchone()[0]
                
                if table_exists:
                    # Check if column already exists
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = %s AND column_name = 'tenant_id'
                    """, (table,))
                    
                    column_exists = cursor.fetchone()
                    
                    if not column_exists:
                        cursor.execute(f'ALTER TABLE {table} ADD COLUMN tenant_id UUID')
                        print(f"  ✅ Added tenant_id to {table}")
                    else:
                        print(f"  ℹ️  tenant_id already exists in {table}")
                else:
                    print(f"  ⚠️  Table {table} does not exist")
                    
            except Exception as e:
                print(f"  ⚠️  {table}: {e}")

        # === FILL EXISTING RECORDS ===
        print("[4/7] Filling existing records with default tenant_id...")
        
        for table in tables_to_modify:
            try:
                cursor.execute(f"""
                    UPDATE {table} 
                    SET tenant_id = %s::uuid 
                    WHERE tenant_id IS NULL
                """, (DEFAULT_TENANT_ID,))
                
                updated = cursor.rowcount
                print(f"  ✅ Updated {updated} records in {table}")
                
            except Exception as e:
                print(f"  ⚠️  {table} update: {e}")

        # === MAKE TENANT_ID NOT NULL ===
        print("[5/7] Making tenant_id columns NOT NULL...")
        
        for table in tables_to_modify:
            try:
                cursor.execute(f'ALTER TABLE {table} ALTER COLUMN tenant_id SET NOT NULL')
                print(f"  ✅ Made tenant_id NOT NULL in {table}")
            except Exception as e:
                print(f"  ⚠️  {table} NOT NULL: {e}")

        # Make whatsapp_settings.tenant_id NOT NULL too
        try:
            cursor.execute('ALTER TABLE whatsapp_settings ALTER COLUMN tenant_id SET NOT NULL')
            print(f"  ✅ Made tenant_id NOT NULL in whatsapp_settings")
        except Exception as e:
            print(f"  ⚠️  whatsapp_settings NOT NULL: {e}")

        # === REMOVE GLOBAL UNIQUE CONSTRAINTS ===
        print("[6/7] Handling unique constraints...")
        
        try:
            # Check if unique constraint exists on telefono
            cursor.execute("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'flow_sesiones' 
                AND constraint_type = 'UNIQUE'
                AND constraint_name LIKE '%telefono%'
            """)
            
            constraints = cursor.fetchall()
            for constraint in constraints:
                constraint_name = constraint[0]
                cursor.execute(f'ALTER TABLE flow_sesiones DROP CONSTRAINT IF EXISTS {constraint_name}')
                print(f"  ✅ Dropped constraint {constraint_name}")
                
        except Exception as e:
            print(f"  ⚠️  Drop constraints: {e}")

        # === CREATE COMPOSITE INDEXES ===
        print("[7/7] Creating composite indexes...")
        
        try:
            # flow_sesiones: (tenant_id, telefono) UNIQUE
            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS ix_flow_sesiones_tenant_telefono 
                ON flow_sesiones (tenant_id, telefono)
            ''')
            print("  ✅ Created ix_flow_sesiones_tenant_telefono")
        except Exception as e:
            print(f"  ⚠️  flow_sesiones index: {e}")
            
        try:
            # flow_pedidos: (tenant_id, created_at) index normal  
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS ix_flow_pedidos_tenant_created 
                ON flow_pedidos (tenant_id, created_at)
            ''')
            print("  ✅ Created ix_flow_pedidos_tenant_created")
        except Exception as e:
            print(f"  ⚠️  flow_pedidos index: {e}")
            
        try:
            # whatsapp_settings: (tenant_id, provider) UNIQUE
            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS ix_whatsapp_settings_tenant_provider 
                ON whatsapp_settings (tenant_id, provider)
            ''')
            print("  ✅ Created ix_whatsapp_settings_tenant_provider")
        except Exception as e:
            print(f"  ⚠️  whatsapp_settings index: {e}")

        # === UPDATE MIGRATION VERSION ===
        try:
            # Check if alembic_version table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'alembic_version'
                )
            """)
            
            if cursor.fetchone()[0]:
                cursor.execute("""
                    INSERT INTO alembic_version (version_num) 
                    VALUES (%s) 
                    ON CONFLICT (version_num) DO NOTHING
                """, ('add_tenant_id_multi_tenant_support',))
                print("  ✅ Updated alembic version")
            else:
                print("  ℹ️  No alembic_version table found")
                
        except Exception as e:
            print(f"  ⚠️  Version update: {e}")

        # Commit all changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n[SUCCESS] PostgreSQL tenant migration applied successfully!")
        print(f"[INFO] Default tenant_id: {DEFAULT_TENANT_ID}")
        return True
        
    except Exception as e:
        print(f"[ERROR] PostgreSQL migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = apply_postgres_migration()
    sys.exit(0 if success else 1)