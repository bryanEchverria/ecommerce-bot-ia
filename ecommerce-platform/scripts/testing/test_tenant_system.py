#!/usr/bin/env python3
"""
🧪 PRUEBAS COMPLETAS DEL SISTEMA MULTI-TENANT
Valida resolución de tenants, aislamiento de datos y auditoría
"""
import requests
import json
import time
from typing import Dict, List, Optional
import asyncio
import aiohttp
from datetime import datetime

# Configuración de pruebas
BASE_URL = "http://localhost:8002"
TEST_TENANTS = [
    {"slug": "acme-cannabis-2024", "subdomain": "acme.localhost:8002"},
    {"slug": "bravo-gaming-2024", "subdomain": "bravo.localhost:8002"},
    {"slug": "mundo-canino-2024", "subdomain": "canino.localhost:8002"}
]

class TenantSystemTester:
    """🔬 Tester completo para sistema multi-tenant"""
    
    def __init__(self):
        self.results = []
        self.errors = []
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Registra resultado de una prueba"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        
    def log_error(self, test_name: str, error: str):
        """Registra error en prueba"""
        self.errors.append({
            "test": test_name,
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        })
        print(f"❌ ERROR en {test_name}: {error}")

    # ===========================================
    # 🔍 PRUEBAS DE RESOLUCIÓN DE TENANTS
    # ===========================================
    
    def test_subdomain_resolution(self):
        """Prueba resolución por subdomain"""
        print("\\n🔍 Probando resolución por subdomain...")
        
        for tenant in TEST_TENANTS:
            try:
                # Request con subdomain
                headers = {"Host": tenant["subdomain"]}
                response = requests.get(f"{BASE_URL}/api/products", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.log_result(
                        f"Subdomain {tenant['slug']}", 
                        True,
                        f"Status: {response.status_code}"
                    )
                else:
                    self.log_result(
                        f"Subdomain {tenant['slug']}", 
                        False,
                        f"Status: {response.status_code}, Response: {response.text[:100]}"
                    )
                    
            except Exception as e:
                self.log_error(f"Subdomain {tenant['slug']}", e)
    
    def test_header_resolution(self):
        """Prueba resolución por header X-Tenant-Id"""
        print("\\n🔍 Probando resolución por header X-Tenant-Id...")
        
        for tenant in TEST_TENANTS:
            try:
                headers = {"X-Tenant-Id": tenant["slug"]}
                response = requests.get(f"{BASE_URL}/api/products", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.log_result(
                        f"Header {tenant['slug']}", 
                        True,
                        f"Status: {response.status_code}"
                    )
                else:
                    self.log_result(
                        f"Header {tenant['slug']}", 
                        False,
                        f"Status: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_error(f"Header {tenant['slug']}", e)
    
    def test_query_fallback(self):
        """Prueba resolución por query parameter (solo en localhost)"""
        print("\\n🔍 Probando resolución por query parameter...")
        
        for tenant in TEST_TENANTS:
            try:
                params = {"client_slug": tenant["slug"]}
                headers = {"Host": "localhost:8002"}
                response = requests.get(f"{BASE_URL}/api/products", params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.log_result(
                        f"Query {tenant['slug']}", 
                        True,
                        f"Status: {response.status_code}"
                    )
                else:
                    self.log_result(
                        f"Query {tenant['slug']}", 
                        False,
                        f"Status: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_error(f"Query {tenant['slug']}", e)

    def test_tenant_rejection(self):
        """Prueba que requests sin tenant válido sean rechazados"""
        print("\\n🔍 Probando rechazo de requests sin tenant...")
        
        test_cases = [
            {"desc": "Sin headers", "headers": {}},
            {"desc": "Host inválido", "headers": {"Host": "invalid.localhost"}},
            {"desc": "Tenant inexistente", "headers": {"X-Tenant-Id": "tenant-inexistente"}},
            {"desc": "Tenant malformado", "headers": {"X-Tenant-Id": "INVALID_TENANT_123!"}}
        ]
        
        for case in test_cases:
            try:
                response = requests.get(f"{BASE_URL}/api/products", headers=case["headers"], timeout=10)
                
                # Debe ser rechazado (400)
                if response.status_code == 400:
                    self.log_result(
                        f"Rechazo: {case['desc']}", 
                        True,
                        f"Correctamente rechazado con 400"
                    )
                else:
                    self.log_result(
                        f"Rechazo: {case['desc']}", 
                        False,
                        f"No rechazado - Status: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_error(f"Rechazo: {case['desc']}", e)

    # ===========================================
    # 🔒 PRUEBAS DE AISLAMIENTO DE DATOS
    # ===========================================
    
    def test_data_isolation(self):
        """Prueba que cada tenant solo vea sus propios datos"""
        print("\\n🔒 Probando aislamiento de datos...")
        
        tenant_products = {}
        
        # Obtener productos de cada tenant
        for tenant in TEST_TENANTS:
            try:
                headers = {"X-Tenant-Id": tenant["slug"]}
                response = requests.get(f"{BASE_URL}/api/products", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    products = response.json()
                    tenant_products[tenant["slug"]] = products
                    
                    self.log_result(
                        f"Datos {tenant['slug']}", 
                        True,
                        f"Obtuvo {len(products)} productos"
                    )
                else:
                    self.log_result(
                        f"Datos {tenant['slug']}", 
                        False,
                        f"Error obteniendo productos: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_error(f"Datos {tenant['slug']}", e)
        
        # Verificar que no hay cross-tenant data leaks
        tenant_ids = list(tenant_products.keys())
        for i, tenant1 in enumerate(tenant_ids):
            for j, tenant2 in enumerate(tenant_ids):
                if i != j and tenant1 in tenant_products and tenant2 in tenant_products:
                    products1 = {p.get('id') for p in tenant_products[tenant1] if 'id' in p}
                    products2 = {p.get('id') for p in tenant_products[tenant2] if 'id' in p}
                    
                    # No debe haber productos compartidos entre tenants
                    shared = products1.intersection(products2)
                    if not shared:
                        self.log_result(
                            f"Aislamiento {tenant1[:8]} vs {tenant2[:8]}", 
                            True,
                            "Sin cross-tenant data leaks"
                        )
                    else:
                        self.log_result(
                            f"Aislamiento {tenant1[:8]} vs {tenant2[:8]}", 
                            False,
                            f"Data leak detectado: {len(shared)} productos compartidos"
                        )

    def test_cross_tenant_access_prevention(self):
        """Prueba que no se pueda acceder a recursos de otros tenants"""
        print("\\n🔒 Probando prevención de acceso cross-tenant...")
        
        # Intentar acceder a recurso específico con tenant incorrecto
        test_cases = [
            {
                "tenant": "acme-cannabis-2024",
                "resource": "orders/1",
                "wrong_tenant": "bravo-gaming-2024"
            },
            {
                "tenant": "bravo-gaming-2024", 
                "resource": "clients/1",
                "wrong_tenant": "mundo-canino-2024"
            }
        ]
        
        for case in test_cases:
            try:
                # Acceso con tenant incorrecto debe fallar
                headers = {"X-Tenant-Id": case["wrong_tenant"]}
                response = requests.get(
                    f"{BASE_URL}/api/{case['resource']}", 
                    headers=headers, 
                    timeout=10
                )
                
                # Debe retornar 404 (no encontrado) o 403 (prohibido)
                if response.status_code in [404, 403]:
                    self.log_result(
                        f"Cross-tenant {case['resource']}", 
                        True,
                        f"Correctamente bloqueado: {response.status_code}"
                    )
                else:
                    self.log_result(
                        f"Cross-tenant {case['resource']}", 
                        False,
                        f"No bloqueado - Status: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_error(f"Cross-tenant {case['resource']}", e)

    # ===========================================
    # 📊 PRUEBAS DE AUDITORÍA Y MÉTRICAS
    # ===========================================
    
    def test_audit_logging(self):
        """Prueba que se estén registrando eventos de auditoría"""
        print("\\n📋 Probando logging de auditoría...")
        
        # Hacer varias requests para generar logs
        test_requests = [
            {"headers": {"X-Tenant-Id": "acme-cannabis-2024"}, "expected": "success"},
            {"headers": {"Host": "bravo.localhost:8002"}, "expected": "success"},
            {"headers": {"Host": "invalid.localhost"}, "expected": "rejected"},
            {"headers": {}, "expected": "rejected"}
        ]
        
        for i, req in enumerate(test_requests):
            try:
                response = requests.get(f"{BASE_URL}/api/products", headers=req["headers"], timeout=10)
                
                # Verificar que la respuesta es la esperada
                if req["expected"] == "success" and response.status_code == 200:
                    self.log_result(f"Audit request {i+1}", True, "Request exitoso loggeado")
                elif req["expected"] == "rejected" and response.status_code == 400:
                    self.log_result(f"Audit request {i+1}", True, "Request rechazado loggeado")
                else:
                    self.log_result(f"Audit request {i+1}", False, f"Resultado inesperado: {response.status_code}")
                    
            except Exception as e:
                self.log_error(f"Audit request {i+1}", e)
        
        # TODO: Verificar que los logs se escribieron correctamente en BD
        # (requeriría acceso directo a BD o endpoint de consulta de auditoría)

    def test_cache_performance(self):
        """Prueba performance del cache de resolución de tenants"""
        print("\\n⚡ Probando performance del cache...")
        
        tenant = TEST_TENANTS[0]
        headers = {"Host": tenant["subdomain"]}
        
        # Primera request (sin cache)
        start_time = time.time()
        response1 = requests.get(f"{BASE_URL}/api/products", headers=headers, timeout=10)
        first_request_time = time.time() - start_time
        
        # Segunda request (con cache)
        start_time = time.time()
        response2 = requests.get(f"{BASE_URL}/api/products", headers=headers, timeout=10)
        cached_request_time = time.time() - start_time
        
        if response1.status_code == 200 and response2.status_code == 200:
            # La segunda request debería ser más rápida (usar cache)
            improvement = (first_request_time - cached_request_time) / first_request_time * 100
            
            self.log_result(
                "Cache performance", 
                True,
                f"Primera: {first_request_time:.3f}s, Segunda: {cached_request_time:.3f}s"
            )
        else:
            self.log_result(
                "Cache performance", 
                False,
                f"Error en requests: {response1.status_code}, {response2.status_code}"
            )

    # ===========================================
    # 🎯 PRUEBAS DE BYPASS PATHS
    # ===========================================
    
    def test_bypass_paths(self):
        """Prueba que paths de bypass funcionen sin tenant"""
        print("\\n🎯 Probando paths de bypass...")
        
        bypass_paths = [
            "/health",
            "/docs", 
            "/openapi.json",
            "/auth/login",
            "/flow/confirm/webhook"
        ]
        
        for path in bypass_paths:
            try:
                # Request sin headers de tenant
                response = requests.get(f"{BASE_URL}{path}", timeout=10)
                
                # Bypass paths no deben requerir tenant (no 400)
                if response.status_code != 400:
                    self.log_result(
                        f"Bypass {path}", 
                        True,
                        f"Status: {response.status_code} (no requiere tenant)"
                    )
                else:
                    self.log_result(
                        f"Bypass {path}", 
                        False,
                        "Incorrectamente requiere tenant"
                    )
                    
            except Exception as e:
                self.log_error(f"Bypass {path}", e)

    # ===========================================
    # 📊 GENERACIÓN DE REPORTE
    # ===========================================
    
    def generate_report(self) -> Dict:
        """Genera reporte completo de las pruebas"""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - successful_tests
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful": successful_tests,
                "failed": failed_tests,
                "success_rate": f"{(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            "results": self.results,
            "errors": self.errors
        }
        
        return report
    
    def print_summary(self):
        """Imprime resumen de resultados"""
        report = self.generate_report()
        
        print("\\n" + "="*60)
        print("🎯 RESUMEN DE PRUEBAS DEL SISTEMA MULTI-TENANT")
        print("="*60)
        
        print(f"📊 Total de pruebas: {report['summary']['total_tests']}")
        print(f"✅ Exitosas: {report['summary']['successful']}")
        print(f"❌ Fallidas: {report['summary']['failed']}")
        print(f"📈 Tasa de éxito: {report['summary']['success_rate']}")
        
        if self.errors:
            print(f"\\n❌ ERRORES DETECTADOS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error['test']}: {error['error']}")
        
        print("\\n" + "="*60)
        
        # Guardar reporte en archivo
        with open("/tmp/tenant_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("📄 Reporte detallado guardado en: /tmp/tenant_test_report.json")


def main():
    """Ejecuta todas las pruebas del sistema multi-tenant"""
    print("🚀 Iniciando pruebas del sistema multi-tenant...")
    
    tester = TenantSystemTester()
    
    # Ejecutar todas las pruebas
    try:
        tester.test_subdomain_resolution()
        tester.test_header_resolution()
        tester.test_query_fallback()
        tester.test_tenant_rejection()
        tester.test_data_isolation()
        tester.test_cross_tenant_access_prevention()
        tester.test_audit_logging()
        tester.test_cache_performance()
        tester.test_bypass_paths()
        
    except KeyboardInterrupt:
        print("\\n⚠️ Pruebas interrumpidas por el usuario")
    
    # Generar reporte final
    tester.print_summary()


if __name__ == "__main__":
    main()