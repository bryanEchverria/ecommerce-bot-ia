#!/usr/bin/env python3
"""
Test PostgreSQL tenant_id migration
"""
import psycopg2
import os
import sys

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

def test_postgres_migration():
    """Test PostgreSQL tenant_id migration results"""
    conn = get_postgres_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("[INFO] Testing PostgreSQL tenant_id migration...")
        
        # Check if tables exist and have tenant_id columns
        tables_to_check = ['flow_sesiones', 'flow_pedidos', 'whatsapp_settings']
        
        for table in tables_to_check:
            print(f"\n[INFO] Checking table: {table}")
            
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table,))
            
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                print(f"  ❌ Table {table} does not exist")
                continue
                
            # Get table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table,))
            
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]
            
            print(f"  Columns: {', '.join(column_names)}")
            
            # Check if tenant_id exists
            tenant_id_col = None
            for col in columns:
                if col[0] == 'tenant_id':
                    tenant_id_col = col
                    break
            
            if tenant_id_col:
                col_name, data_type, is_nullable = tenant_id_col
                print(f"  ✅ tenant_id column: {data_type} (nullable: {is_nullable})")
                
                # Check data
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total_records = cursor.fetchone()[0]
                
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE tenant_id IS NOT NULL")
                records_with_tenant = cursor.fetchone()[0]
                
                print(f"  Records: {total_records} total, {records_with_tenant} with tenant_id")
                
                # Show sample data if exists
                if total_records > 0:
                    if table == 'flow_sesiones':
                        cursor.execute(f"SELECT id, telefono, tenant_id FROM {table} LIMIT 3")
                    elif table == 'flow_pedidos':
                        cursor.execute(f"SELECT id, telefono, total, tenant_id FROM {table} LIMIT 3")
                    else:
                        cursor.execute(f"SELECT id, provider, tenant_id FROM {table} LIMIT 3")
                        
                    sample_data = cursor.fetchall()
                    for row in sample_data:
                        print(f"    Sample: {row}")
                        
            else:
                print(f"  ❌ tenant_id column missing")

        # Check indexes
        print(f"\n[INFO] Checking tenant-specific indexes...")
        
        cursor.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE indexname LIKE '%tenant%'
            ORDER BY indexname
        """)
        
        indexes = cursor.fetchall()
        for index_name, index_def in indexes:
            print(f"  ✅ Index: {index_name}")
            print(f"      SQL: {index_def}")

        # Check UUID extension
        print(f"\n[INFO] Checking UUID extension...")
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp'
            )
        """)
        
        uuid_enabled = cursor.fetchone()[0]
        if uuid_enabled:
            print("  ✅ UUID extension is enabled")
        else:
            print("  ❌ UUID extension is not enabled")

        cursor.close()
        conn.close()
        
        print(f"\n[SUCCESS] PostgreSQL migration test completed")
        return True
        
    except Exception as e:
        print(f"[ERROR] PostgreSQL migration test failed: {e}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    success = test_postgres_migration()
    sys.exit(0 if success else 1)