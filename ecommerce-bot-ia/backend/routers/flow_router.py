"""
Router para endpoints de Flow (callbacks y confirmaciones de pago)
Compatible con el sistema multi-tenant
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from services.flow_service import validar_firma
from models import FlowPedido
import logging
import httpx
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

async def enviar_confirmacion_whatsapp(telefono: str, pedido_id: str, total: float):
    """Envía confirmación de pago exitoso por WhatsApp"""
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        
        if not account_sid or not auth_token:
            logger.error("Twilio credentials not configured for payment confirmation")
            return
        
        # Normalizar número de teléfono
        if not telefono.startswith('whatsapp:'):
            if not telefono.startswith('+'):
                telefono = '+' + telefono
            telefono = f'whatsapp:{telefono}'
        
        mensaje = f"""🎉 *¡PAGO CONFIRMADO!* 🎉

✅ Tu pedido #{pedido_id} ha sido pagado exitosamente.

💰 Total pagado: ${total:.0f}

📦 Procesaremos tu pedido y te contactaremos para coordinar la entrega.

🙌 ¡Gracias por confiar en Sintestesia!

💬 Si tienes alguna pregunta, no dudes en escribirnos."""
        
        async with httpx.AsyncClient() as client:
            auth = (account_sid, auth_token)
            
            data = {
                'To': telefono,
                'From': whatsapp_number,
                'Body': mensaje
            }
            
            response = await client.post(
                f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json',
                auth=auth,
                data=data
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Payment confirmation sent successfully to {telefono}")
            else:
                logger.error(f"❌ Failed to send payment confirmation: {response.status_code} - {response.text}")
                
    except Exception as e:
        logger.error(f"❌ Error sending payment confirmation: {str(e)}")

@router.post("/flow/confirm")
async def confirmar_pago_flow(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para recibir confirmaciones de pago desde Flow
    URL: https://webhook.sintestesia.cl/flow/confirm
    """
    try:
        data = dict(await request.form())
        logger.info(f"📩 [Flow Confirm] Datos recibidos: {data}")

        # Validar firma de Flow
        if not validar_firma(data.copy()):
            logger.warning("❌ [Flow Confirm] Firma inválida, callback rechazado.")
            return {"status": "error", "message": "Firma inválida"}

        order_id = data.get("commerceOrder")
        if not order_id:
            logger.warning("⚠️ [Flow Confirm] order_id faltante en el callback.")
            return {"status": "error", "message": "Falta order_id"}

        # Obtener el status directamente del callback (más confiable que consultar API)
        status_flow = data.get("status")
        logger.info(f"🆔 [Flow Confirm] Status recibido: {status_flow} para orden #{order_id}")

        # Status "2" significa pago exitoso según documentación de Flow
        pagado = (status_flow == "2")
        logger.info(f"💰 [Flow Confirm] Interpretando pago como: {'EXITOSO' if pagado else 'PENDIENTE/FALLIDO'}")

        if pagado:
            # Get tenant_id from context for multi-tenant support
            from tenant_middleware import get_tenant_id
            try:
                tenant_id = get_tenant_id()
                pedido = db.query(FlowPedido).filter_by(id=order_id, tenant_id=tenant_id).first()
            except:
                # Fallback for webhooks without tenant context - find by order_id only
                pedido = db.query(FlowPedido).filter_by(id=order_id).first()
                
            if pedido:
                pedido.estado = "pagado"
                db.commit()
                logger.info(f"✅ [Flow Confirm] Pedido #{order_id} marcado como PAGADO en la BD.")
                
                # Enviar confirmación por WhatsApp
                await enviar_confirmacion_whatsapp(pedido.telefono, order_id, pedido.total)
                
                return {"status": "ok", "message": f"Pedido {order_id} pagado"}
            else:
                logger.warning(f"⚠️ [Flow Confirm] Pedido #{order_id} no encontrado en la BD.")
                return {"status": "error", "message": "Pedido no encontrado"}
        
        logger.info(f"⏳ [Flow Confirm] Pedido #{order_id} aún PENDIENTE de pago (status: {status_flow}).")
        return {"status": "pending"}

    except Exception as e:
        logger.error(f"⚠️ [Flow Confirm] ERROR interno al verificar pedido: {e}")
        return {"status": "error", "message": str(e)}

@router.api_route("/flow/return", methods=["GET", "POST"], response_class=HTMLResponse)
async def flow_return(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para cuando el usuario regresa desde Flow después de pagar
    URL: https://webhook.sintestesia.cl/flow/return
    """
    try:
        if request.method == "POST":
            data = dict(await request.form())
        else:
            data = dict(request.query_params)
            
        logger.info(f"🔄 [Flow Return] Datos recibidos: {data}")

        status = data.get("status")
        commerce_order = data.get("commerceOrder")
        token = data.get("token")

        # Si tenemos token pero no commerceOrder, consultar a Flow
        if not commerce_order and token:
            from services.flow_service import FLOW_API_KEY, FLOW_BASE_URL, _firmar
            import requests
            
            params = {"apiKey": FLOW_API_KEY, "token": token}
            params["s"] = _firmar(params)

            response = requests.get(f"{FLOW_BASE_URL}/payment/getStatus", params=params)
            if response.status_code == 200:
                datos = response.json()
                commerce_order = datos.get("commerceOrder")
                status = "SUCCESS" if datos.get("status") == 2 else "FAILED"
            else:
                return f"<h1>⚠️ No se pudo obtener información del pago (token={token}).</h1>"

        # Procesar resultado del pago
        if status == "SUCCESS" and commerce_order:
            # Get tenant_id from context for multi-tenant support
            from tenant_middleware import get_tenant_id
            try:
                tenant_id = get_tenant_id()
                pedido = db.query(FlowPedido).filter_by(id=commerce_order, tenant_id=tenant_id).first()
            except:
                # Fallback for webhooks without tenant context - find by order_id only
                pedido = db.query(FlowPedido).filter_by(id=commerce_order).first()
                
            if pedido:
                pedido.estado = "pagado"
                db.commit()
                logger.info(f"✅ [Flow Return] Pedido #{commerce_order} marcado como PAGADO en la BD.")
                
                # Enviar confirmación por WhatsApp
                await enviar_confirmacion_whatsapp(pedido.telefono, commerce_order, pedido.total)
            
            return f"""
            <html>
            <head><title>Pago Exitoso</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: #28a745;">✅ ¡Pago Exitoso!</h1>
                <p>Tu pedido #{commerce_order} ha sido pagado correctamente.</p>
                <p>Recibirás confirmación por WhatsApp en breve.</p>
                <p style="color: #6c757d;">Gracias por tu compra 🙌</p>
            </body>
            </html>
            """

        return f"""
        <html>
        <head><title>Pago Cancelado</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: #dc3545;">⚠️ Pago No Completado</h1>
            <p>El pago del pedido #{commerce_order} no se pudo procesar.</p>
            <p>Puedes intentar de nuevo contactando por WhatsApp.</p>
        </body>
        </html>
        """

    except Exception as e:
        logger.error(f"⚠️ [Flow Return] ERROR: {e}")
        return f"""
        <html>
        <head><title>Error</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: #dc3545;">❌ Error</h1>
            <p>Ocurrió un error procesando la información del pago.</p>
            <p>Por favor contacta a soporte.</p>
        </body>
        </html>
        """

@router.get("/flow/status")
async def flow_status():
    """
    Endpoint de estado del servicio Flow
    """
    import os
    return {
        "service": "Flow Payment Integration",
        "status": "active",
        "endpoints": {
            "confirm": "/flow/confirm",
            "return": "/flow/return"
        },
        "environment": "sandbox" if "sandbox" in os.getenv("FLOW_BASE_URL", "") else "production",
        "configured": bool(os.getenv("FLOW_API_KEY") and os.getenv("FLOW_SECRET_KEY"))
    }

@router.get("/flow/orders")
async def get_flow_orders_backoffice(limit: int = 50, db: Session = Depends(get_db)):
    """
    Endpoint simple para consultar pedidos Flow desde el backoffice (tenant-aware)
    """
    try:
        from tenant_middleware import get_tenant_id
        tenant_id = get_tenant_id()
        
        pedidos = db.query(FlowPedido).filter(
            FlowPedido.tenant_id == tenant_id
        ).order_by(FlowPedido.created_at.desc()).limit(limit).all()
        
        return {
            "pedidos": [
                {
                    "id": pedido.id,
                    "telefono": pedido.telefono,
                    "tenant_id": pedido.tenant_id,
                    "total": pedido.total,
                    "estado": pedido.estado,
                    "created_at": pedido.created_at.isoformat() if pedido.created_at else None,
                    "flow_url": f"https://sandbox.flow.cl/app/web/pay.php?token={pedido.token}" if pedido.token else None
                }
                for pedido in pedidos
            ],
            "total": len(pedidos)
        }
    except Exception as e:
        logger.error(f"Error getting Flow orders: {e}")
        return {"error": str(e), "pedidos": []}

@router.get("/flow/stats") 
async def get_flow_stats_backoffice(db: Session = Depends(get_db)):
    """
    Estadísticas básicas de Flow para el backoffice (tenant-aware)
    """
    try:
        from tenant_middleware import get_tenant_id
        tenant_id = get_tenant_id()
        
        total_pedidos = db.query(FlowPedido).filter(FlowPedido.tenant_id == tenant_id).count()
        pedidos_pagados = db.query(FlowPedido).filter(
            FlowPedido.tenant_id == tenant_id,
            FlowPedido.estado == "pagado"
        ).count()
        pedidos_pendientes = db.query(FlowPedido).filter(
            FlowPedido.tenant_id == tenant_id,
            FlowPedido.estado == "pendiente_pago"
        ).count()
        
        # Calculate total sold
        from sqlalchemy import func
        result = db.query(func.sum(FlowPedido.total)).filter(
            FlowPedido.tenant_id == tenant_id,
            FlowPedido.estado == "pagado"
        ).first()
        total_vendido = result[0] if result and result[0] else 0
        
        return {
            "total_pedidos": total_pedidos,
            "pedidos_pagados": pedidos_pagados, 
            "pedidos_pendientes": pedidos_pendientes,
            "total_vendido": int(total_vendido),
            "tasa_conversion": round((pedidos_pagados / total_pedidos * 100) if total_pedidos > 0 else 0, 2)
        }
    except Exception as e:
        logger.error(f"Error getting Flow stats: {e}")
        return {"error": str(e)}