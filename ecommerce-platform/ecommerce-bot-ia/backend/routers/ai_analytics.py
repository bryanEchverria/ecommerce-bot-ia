"""
🤖 ROUTER DE ANALYTICS DE IA
Panel de administración para analizar y mejorar el bot con IA
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from database import get_db
from auth import get_current_client
import json

router = APIRouter()

@router.get("/ai-analytics/conversation-stats")
async def get_conversation_stats(
    days_back: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    """Estadísticas generales de conversaciones del bot"""
    try:
        query = text("""
            SELECT 
                COUNT(*) as total_conversaciones,
                COUNT(DISTINCT telefono) as usuarios_unicos,
                AVG(duracion_respuesta_ms) as tiempo_promedio_respuesta,
                COUNT(CASE WHEN intencion_detectada = 'intencion_compra' THEN 1 END) as intentos_compra,
                COUNT(CASE WHEN respuesta_bot LIKE '%🎉%' THEN 1 END) as conversiones_exitosas
            FROM conversation_history
            WHERE tenant_id = :tenant_id 
            AND timestamp_mensaje >= NOW() - INTERVAL ':days_back days'
        """)
        
        result = db.execute(query, {
            "tenant_id": current_client.id,
            "days_back": days_back
        }).first()
        
        if not result:
            return {
                "total_conversaciones": 0,
                "usuarios_unicos": 0,
                "tiempo_promedio_respuesta": 0,
                "intentos_compra": 0,
                "conversiones_exitosas": 0,
                "conversion_rate": 0
            }
        
        conversion_rate = (result.conversiones_exitosas / result.intentos_compra * 100) if result.intentos_compra > 0 else 0
        
        return {
            "total_conversaciones": result.total_conversaciones,
            "usuarios_unicos": result.usuarios_unicos,
            "tiempo_promedio_respuesta": round(result.tiempo_promedio_respuesta or 0),
            "intentos_compra": result.intentos_compra,
            "conversiones_exitosas": result.conversiones_exitosas,
            "conversion_rate": round(conversion_rate, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@router.get("/ai-analytics/intent-analysis")
async def get_intent_analysis(
    days_back: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    """Análisis de intenciones detectadas por el bot"""
    try:
        query = text("""
            SELECT 
                intencion_detectada,
                COUNT(*) as frecuencia,
                AVG(duracion_respuesta_ms) as tiempo_promedio,
                COUNT(CASE WHEN respuesta_bot LIKE '%✅%' OR respuesta_bot LIKE '%🎉%' 
                           THEN 1 END) as respuestas_exitosas,
                array_agg(DISTINCT productos_mencionados[1]) FILTER (WHERE productos_mencionados[1] IS NOT NULL) as productos_frecuentes
            FROM conversation_history
            WHERE tenant_id = :tenant_id 
            AND timestamp_mensaje >= NOW() - INTERVAL ':days_back days'
            AND intencion_detectada IS NOT NULL
            GROUP BY intencion_detectada
            ORDER BY frecuencia DESC
        """)
        
        result = db.execute(query, {
            "tenant_id": current_client.id,
            "days_back": days_back
        })
        
        intenciones = []
        for row in result:
            efectividad = (row.respuestas_exitosas / row.frecuencia * 100) if row.frecuencia > 0 else 0
            intenciones.append({
                "intencion": row.intencion_detectada,
                "frecuencia": row.frecuencia,
                "tiempo_promedio_ms": round(row.tiempo_promedio or 0),
                "efectividad": round(efectividad, 2),
                "productos_frecuentes": row.productos_frecuentes or []
            })
        
        return {"intenciones": intenciones}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing intents: {str(e)}")

@router.get("/ai-analytics/product-performance")
async def get_product_performance(
    days_back: int = Query(30, ge=1, le=365),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    """Análisis de rendimiento de productos en conversaciones"""
    try:
        query = text("""
            SELECT 
                producto_id,
                producto_nombre,
                SUM(consultas_totales) as total_consultas,
                SUM(conversiones_compra) as total_conversiones,
                AVG(conversion_rate) as conversion_rate_promedio,
                MAX(fecha_analisis) as ultima_actualizacion
            FROM product_analytics
            WHERE tenant_id = :tenant_id 
            AND fecha_analisis >= CURRENT_DATE - INTERVAL ':days_back days'
            GROUP BY producto_id, producto_nombre
            ORDER BY total_consultas DESC
            LIMIT :limit
        """)
        
        result = db.execute(query, {
            "tenant_id": current_client.id,
            "days_back": days_back,
            "limit": limit
        })
        
        productos = []
        for row in result:
            productos.append({
                "producto_id": row.producto_id,
                "producto_nombre": row.producto_nombre,
                "total_consultas": row.total_consultas,
                "total_conversiones": row.total_conversiones,
                "conversion_rate": round(row.conversion_rate_promedio or 0, 2),
                "ultima_actualizacion": row.ultima_actualizacion.isoformat() if row.ultima_actualizacion else None
            })
        
        return {"productos": productos}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing products: {str(e)}")

@router.get("/ai-analytics/conversation-flow")
async def get_conversation_flow(
    telefono: Optional[str] = Query(None),
    days_back: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    """Flujo detallado de conversaciones para análisis"""
    try:
        conditions = ["tenant_id = :tenant_id", "timestamp_mensaje >= NOW() - INTERVAL ':days_back days'"]
        params = {"tenant_id": current_client.id, "days_back": days_back}
        
        if telefono:
            conditions.append("telefono = :telefono")
            params["telefono"] = telefono
        
        query = text(f"""
            SELECT 
                telefono,
                mensaje_usuario,
                respuesta_bot,
                intencion_detectada,
                productos_mencionados,
                timestamp_mensaje,
                duracion_respuesta_ms
            FROM conversation_history
            WHERE {' AND '.join(conditions)}
            ORDER BY telefono, timestamp_mensaje DESC
            LIMIT 100
        """)
        
        result = db.execute(query, params)
        
        conversaciones = []
        for row in result:
            conversaciones.append({
                "telefono": row.telefono,
                "mensaje_usuario": row.mensaje_usuario,
                "respuesta_bot": row.respuesta_bot,
                "intencion_detectada": row.intencion_detectada,
                "productos_mencionados": row.productos_mencionados,
                "timestamp": row.timestamp_mensaje.isoformat(),
                "duracion_ms": row.duracion_respuesta_ms
            })
        
        return {"conversaciones": conversaciones}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversation flow: {str(e)}")

@router.get("/ai-analytics/user-behavior")
async def get_user_behavior_analysis(
    days_back: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    """Análisis de comportamiento de usuarios"""
    try:
        # Análisis de patrones de uso
        query = text("""
            WITH user_stats AS (
                SELECT 
                    telefono,
                    COUNT(*) as total_mensajes,
                    COUNT(DISTINCT DATE(timestamp_mensaje)) as dias_activos,
                    COUNT(CASE WHEN intencion_detectada = 'intencion_compra' THEN 1 END) as intentos_compra,
                    MIN(timestamp_mensaje) as primera_interaccion,
                    MAX(timestamp_mensaje) as ultima_interaccion,
                    array_agg(DISTINCT productos_mencionados[1]) FILTER (WHERE productos_mencionados[1] IS NOT NULL) as productos_interes
                FROM conversation_history
                WHERE tenant_id = :tenant_id 
                AND timestamp_mensaje >= NOW() - INTERVAL ':days_back days'
                GROUP BY telefono
            )
            SELECT 
                CASE 
                    WHEN total_mensajes >= 10 THEN 'usuario_frecuente'
                    WHEN intentos_compra > 0 THEN 'comprador_potencial'
                    WHEN total_mensajes >= 3 THEN 'explorador'
                    ELSE 'nuevo_usuario'
                END as tipo_usuario,
                COUNT(*) as cantidad_usuarios,
                AVG(total_mensajes) as promedio_mensajes,
                AVG(dias_activos) as promedio_dias_activos
            FROM user_stats
            GROUP BY tipo_usuario
            ORDER BY cantidad_usuarios DESC
        """)
        
        result = db.execute(query, {
            "tenant_id": current_client.id,
            "days_back": days_back
        })
        
        tipos_usuario = []
        for row in result:
            tipos_usuario.append({
                "tipo_usuario": row.tipo_usuario,
                "cantidad_usuarios": row.cantidad_usuarios,
                "promedio_mensajes": round(row.promedio_mensajes, 1),
                "promedio_dias_activos": round(row.promedio_dias_activos, 1)
            })
        
        return {"tipos_usuario": tipos_usuario}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing user behavior: {str(e)}")

@router.post("/ai-analytics/feedback")
async def submit_response_feedback(
    conversation_id: int,
    fue_util: bool,
    razon_feedback: Optional[str] = None,
    sugerencia_mejora: Optional[str] = None,
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    """Recibir feedback sobre la calidad de respuestas del bot"""
    try:
        # Verificar que la conversación pertenece al tenant
        query = text("""
            SELECT telefono FROM conversation_history 
            WHERE id = :conversation_id AND tenant_id = :tenant_id
        """)
        
        result = db.execute(query, {
            "conversation_id": conversation_id,
            "tenant_id": current_client.id
        }).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        # Insertar feedback
        insert_query = text("""
            INSERT INTO response_quality 
            (conversation_history_id, telefono, tenant_id, fue_util, razon_feedback, sugerencia_mejora)
            VALUES (:conversation_id, :telefono, :tenant_id, :fue_util, :razon_feedback, :sugerencia_mejora)
        """)
        
        db.execute(insert_query, {
            "conversation_id": conversation_id,
            "telefono": result.telefono,
            "tenant_id": current_client.id,
            "fue_util": fue_util,
            "razon_feedback": razon_feedback,
            "sugerencia_mejora": sugerencia_mejora
        })
        
        db.commit()
        
        return {"message": "Feedback registrado exitosamente"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@router.get("/ai-analytics/training-data")
async def get_training_data_suggestions(
    min_frequency: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    """Sugerencias para mejorar el entrenamiento del bot"""
    try:
        # Patrones de mensajes que el bot no maneja bien
        query = text("""
            WITH problematic_patterns AS (
                SELECT 
                    mensaje_usuario,
                    intencion_detectada,
                    COUNT(*) as frecuencia,
                    AVG(CASE WHEN respuesta_bot LIKE '%Lo siento%' OR respuesta_bot LIKE '%no entiendo%' 
                             THEN 1.0 ELSE 0.0 END) as confusion_rate
                FROM conversation_history
                WHERE tenant_id = :tenant_id 
                AND timestamp_mensaje >= NOW() - INTERVAL '30 days'
                GROUP BY mensaje_usuario, intencion_detectada
                HAVING COUNT(*) >= :min_frequency
                ORDER BY confusion_rate DESC, frecuencia DESC
                LIMIT 20
            )
            SELECT * FROM problematic_patterns WHERE confusion_rate > 0.3
        """)
        
        result = db.execute(query, {
            "tenant_id": current_client.id,
            "min_frequency": min_frequency
        })
        
        patrones_problematicos = []
        for row in result:
            patrones_problematicos.append({
                "mensaje_patron": row.mensaje_usuario,
                "intencion_actual": row.intencion_detectada,
                "frecuencia": row.frecuencia,
                "confusion_rate": round(row.confusion_rate * 100, 1),
                "sugerencia": "Mejorar detección de intención para este patrón"
            })
        
        return {"patrones_para_mejorar": patrones_problematicos}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting training suggestions: {str(e)}")

@router.post("/ai-analytics/cleanup-data")
async def cleanup_old_data(
    days_to_keep: int = Query(90, ge=30, le=365),
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    """Limpiar datos antiguos de conversaciones"""
    try:
        # Limpiar conversation_history antiguo
        query = text("""
            DELETE FROM conversation_history
            WHERE tenant_id = :tenant_id 
            AND timestamp_mensaje < NOW() - INTERVAL ':days_to_keep days'
        """)
        
        result = db.execute(query, {
            "tenant_id": current_client.id,
            "days_to_keep": days_to_keep
        })
        
        rows_deleted = result.rowcount
        
        # Limpiar contextos expirados
        db.execute(text("SELECT cleanup_expired_contexts()"))
        
        db.commit()
        
        return {
            "message": f"Limpieza completada: {rows_deleted} conversaciones eliminadas",
            "days_kept": days_to_keep
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error cleaning up data: {str(e)}")