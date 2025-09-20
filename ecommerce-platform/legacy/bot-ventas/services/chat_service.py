from sqlalchemy.orm import Session
from sqlalchemy import func
from models.sesion import Sesion
from models.producto import Producto
from models.pedido import Pedido
from models.producto_pedido import ProductoPedido
from services.ia_service import interpretar_mensaje, interpretar_confirmacion
from services.pagos_service import crear_orden_flow, verificar_pago_flow


def obtener_o_crear_sesion(db: Session, telefono: str) -> Sesion:
    sesion = db.query(Sesion).filter_by(telefono=telefono).first()
    if not sesion:
        sesion = Sesion(telefono=telefono, estado="INITIAL", datos={})
        db.add(sesion)
        db.commit()
        db.refresh(sesion)
        print(f"🆕 Nueva sesión creada para {telefono}")
    return sesion


def menu_principal() -> str:
    return (
        "🤖 *Bienvenido al Bot Automatizado* 🤖\n"
        "Elige una opción:\n"
        "1️⃣ Ver catálogo\n"
        "2️⃣ Hablar con un ejecutivo\n"
        "3️⃣ Reportar un problema\n"
        "4️⃣ Consultar estado de mi pedido"
    )


def procesar_mensaje(db: Session, telefono: str, texto_usuario: str) -> str:
    sesion = obtener_o_crear_sesion(db, telefono)
    texto = texto_usuario.lower().strip()
    print(f"📩 [{telefono}] Mensaje recibido: {texto}")

    # Cancelar pedido
    if texto in ["cancelar", "cancelar pedido", "anular pedido"]:
        pedido_id = sesion.datos.get("pedido_id")
        if pedido_id:
            pedido = db.query(Pedido).filter_by(id=pedido_id).first()
            if pedido and pedido.estado == "pendiente_pago":
                pedido.estado = "cancelado"
                db.commit()
                print(f"❌ Pedido #{pedido.id} cancelado por el usuario {telefono}")

        sesion.estado = "INITIAL"
        sesion.datos = {}
        db.commit()
        return "❌ Tu pedido ha sido *cancelado* y registrado como tal.\n" + menu_principal()

    # Confirmación de pedido
    if sesion.estado == "ORDER_CONFIRMATION":
        confirmacion = interpretar_confirmacion(texto)
        print(f"🔎 [{telefono}] Confirmación detectada: {confirmacion}")

        if confirmacion == "si":
            items = sesion.datos.get("items", [])
            if not items:
                sesion.estado = "INITIAL"
                db.commit()
                return "❌ No hay productos pendientes.\n" + menu_principal()

            total = 0
            pedido = Pedido(monto_total=0, estado="pendiente_pago")
            db.add(pedido)
            db.commit()
            db.refresh(pedido)

            detalles = []
            for item in items:
                producto = db.query(Producto).filter_by(id=item["id"]).first()
                if producto:
                    total += producto.precio * item["cantidad"]
                    db.add(ProductoPedido(
                        pedido_id=pedido.id,
                        producto_id=producto.id,
                        cantidad=item["cantidad"],
                    ))
                    detalles.append(f"{item['cantidad']} x {producto.nombre}")

            pedido.monto_total = total
            db.commit()

            url_pago = crear_orden_flow(str(pedido.id), total, f"Pedido_{pedido.id}", db)

            if "token=" not in url_pago:
                return "⚠️ Error al generar el link de pago. Intenta de nuevo."

            sesion.estado = "ORDER_SCHEDULING"
            sesion.datos = {"pedido_id": pedido.id}
            db.commit()

            return (
                f"✅ Pedido confirmado #{pedido.id}: {', '.join(detalles)}\n"
                f"Total: ${total}\n"
                f"👉 Para continuar, realiza el pago aquí:\n{url_pago}\n\n"
                f"Cuando termines el pago, escribe *pagado* para confirmar."
            )

        elif confirmacion == "no":
            sesion.estado = "INITIAL"
            sesion.datos = {}
            db.commit()
            return "❌ Pedido cancelado.\n" + menu_principal()

        else:
            return "🤔 No entendí tu respuesta. ¿Confirmas el pedido? (sí o no)"

    # Pagado
    if texto in ["pagado", "ya pagué", "pague", "pago"]:
        pedido_id = sesion.datos.get("pedido_id")
        if not pedido_id:
            return "❌ No hay pedidos pendientes de pago.\n" + menu_principal()

        pedido = db.query(Pedido).filter_by(id=pedido_id).first()
        if not pedido:
            return "❌ Pedido no encontrado.\n" + menu_principal()

        # Verificar estado actual del pedido en la BD (más confiable que consultar API)
        pedido_actualizado = db.query(Pedido).filter_by(id=pedido_id).first()
        if pedido_actualizado and pedido_actualizado.estado == "pagado":
            sesion.estado = "INITIAL"
            sesion.datos = {}
            db.commit()
            return f"✅ ¡Pago confirmado! Tu pedido #{pedido.id} ha sido registrado como pagado.\nGracias por tu compra. 🙌"
        else:
            return f"⚠️ Aún no hemos recibido el pago de tu pedido #{pedido.id}."

    # Consultar estado de pedido
    if sesion.estado == "CHECK_ORDER":
        try:
            pedido_id = int(texto)
        except ValueError:
            return "🔎 Por favor, envíame el *número de tu pedido* válido."

        pedido = db.query(Pedido).filter_by(id=pedido_id).first()
        if pedido:
            productos = (
                db.query(Producto, ProductoPedido.cantidad)
                .join(ProductoPedido, Producto.id == ProductoPedido.producto_id)
                .filter(ProductoPedido.pedido_id == pedido.id)
                .all()
            )
            detalle = "\n".join([f"- {cant} x {prod.nombre}" for prod, cant in productos])
            sesion.estado = "INITIAL"
            db.commit()
            return f"📋 Estado de tu pedido #{pedido.id}: *{pedido.estado.upper()}*\n{detalle}\nTotal: ${pedido.monto_total}"
        else:
            return "❌ No encontré ese pedido. Intenta nuevamente."

    # Compra detectada
    interpretacion = interpretar_mensaje(texto)
    if interpretacion["intencion"] == "comprar" and interpretacion["productos"]:
        items = []
        detalles = []
        total = 0

        for p in interpretacion["productos"]:
            producto = (
                db.query(Producto)
                .filter(func.lower(Producto.nombre).like(f"%{p['nombre']}%"))
                .first()
            )
            if producto:
                items.append({"id": producto.id, "cantidad": p["cantidad"]})
                total += producto.precio * p["cantidad"]
                detalles.append(f"{p['cantidad']} x {producto.nombre}")
            else:
                detalles.append(f"❌ {p['nombre']} (no encontrado)")

        if items:
            sesion.estado = "ORDER_CONFIRMATION"
            sesion.datos = {"items": items}
            db.commit()
            return (
                f"🔎 Esto es lo que entendí:\n{chr(10).join(detalles)}\n"
                f"Total: ${total}\n👉 ¿Confirmas tu pedido? (sí o no)"
            )
        else:
            return "❌ No encontré los productos que mencionaste."

    # Menú principal
    if sesion.estado == "INITIAL":
        if texto in ["1", "catalogo", "catálogo"]:
            productos = db.query(Producto).filter_by(activo=True).all()
            listado = "\n".join([f"- {p.nombre} (${p.precio})" for p in productos])
            return f"📦 *Catálogo de productos:*\n{listado}\n\n👉 ¿Quieres comprar algo?"
        elif texto in ["2", "ejecutivo"]:
            return "🔀 Te conecto con un ejecutivo humano."
        elif texto in ["3", "problema"]:
            return "🛠 Por favor, cuéntame el problema que tienes."
        elif texto in ["4", "pedido", "estado", "mis pedidos"]:
            sesion.estado = "CHECK_ORDER"
            db.commit()
            return "🔎 Por favor, envíame el *número de tu pedido*."
        else:
            return menu_principal()

    if sesion.estado == "ORDER_SCHEDULING":
        return "Tu pedido está pendiente de pago. Si ya pagaste escribe *pagado*, o escribe *cancelar pedido* para anularlo."

    return menu_principal()
