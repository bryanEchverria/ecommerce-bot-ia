export default {
  "common": {
    "edit": "Editar",
    "delete": "Eliminar",
    "cancel": "Cancelar",
    "save": "Guardar",
    "saveProduct": "Guardar Producto",
    "saveCampaign": "Guardar Campaña",
    "saveDiscount": "Guardar Descuento",
    "saveClient": "Guardar Cliente",
    "status": "Estado",
    "actions": "Acciones",
    "all": "Todos",
    "name": "Nombre",
    "category": "Categoría",
    "price": "Precio",
    "stock": "Inventario",
    "units": "{{count}} unidades",
    "clicks": "Clics",
    "conversions": "Conversiones",
    "type": "Tipo",
    "value": "Valor",
    "target": "Objetivo",
    "search": "Buscar..."
  },
  "sidebar": {
    "title": "E-commerce",
    "dashboard": "Dashboard",
    "products": "Productos",
    "orders": "Pedidos",
    "clients": "Clientes",
    "campaigns": "Campañas",
    "discounts": "Descuentos",
    "copyright": "© 2024 E-commerce Inc.",
    "rightsReserved": "Todos los derechos reservados."
  },
  "header": {
    "titles": {
      "dashboard": "Resumen del Dashboard",
      "products": "Gestión de Productos",
      "orders": "Seguimiento de Pedidos",
      "clients": "Gestión de Clientes",
      "campaigns": "Gestión de Campañas",
      "discounts": "Gestión de Descuentos",
      "default": "Dashboard"
    }
  },
  "dashboard": {
    "timeFilters": {
      "today": "Hoy",
      "7d": "Últimos 7 días",
      "30d": "Últimos 30 días",
      "1y": "Último Año"
    },
    "cards": {
      "totalRevenue": "Ingresos Totales",
      "sales": "Ventas",
      "newOrders": "Pedidos Nuevos",
      "newCustomers": "Clientes Nuevos"
    },
    "changeLabels": {
      "today": "desde ayer",
      "7d": "de los 7 días ant.",
      "30d": "de los 30 días ant.",
      "1y": "del año pasado"
    },
    "salesTrend": {
      "title": "Tendencia de Ventas"
    },
    "recentOrders": {
      "title": "Pedidos Recientes",
      "headers": {
        "orderId": "ID de Pedido",
        "orderNumber": "Número de Pedido",
        "customer": "Cliente",
        "date": "Fecha",
        "status": "Estado",
        "total": "Total"
      },
      "noOrders": "No se encontraron pedidos para este período."
    }
  },
  "products": {
    "title": "Todos los Productos",
    "description": "Gestiona el inventario y los detalles de tus productos.",
    "addProduct": "Añadir Producto",
    "searchPlaceholder": "Buscar por nombre de producto...",
    "table": {
      "productName": "Nombre del Producto"
    },
    "noProducts": "No se encontraron productos. Intenta ajustar tus filtros.",
    "showingCount": "Mostrando {{count}} de {{total}} productos",
    "messages": {
      "created": "Producto '{{name}}' creado exitosamente",
      "updated": "Producto '{{name}}' actualizado exitosamente",
      "deleted": "Producto '{{name}}' eliminado exitosamente",
      "error": "Error al guardar el producto. Inténtalo de nuevo.",
      "deleteError": "Error al eliminar el producto. Inténtalo de nuevo."
    }
  },
  "productModal": {
    "addTitle": "Añadir Nuevo Producto",
    "editTitle": "Editar Producto",
    "labels": {
      "productName": "Nombre del Producto",
      "category": "Categoría",
      "status": "Estado",
      "price": "Precio",
      "salePrice": "Precio de Oferta (Opcional)",
      "stock": "Inventario"
    }
  },
  "orders": {
    "title": "Todos los Pedidos",
    "description": "Rastrea y gestiona los pedidos de los clientes.",
    "export": "Exportar CSV",
    "headers": {
      "orderId": "ID de Pedido",
      "orderNumber": "Número de Pedido",
      "customerName": "Nombre del Cliente",
      "date": "Fecha",
      "items": "Artículos",
      "total": "Total"
    },
    "showingCount": "Mostrando {{count}} de {{total}} pedidos",
    "searchPlaceholder": "Buscar por Número de Pedido o Cliente...",
    "filterByStatus": "Filtrar por estado",
    "allStatuses": "Todos los Estados",
    "noOrders": "No se encontraron pedidos. Intenta ajustar tus filtros.",
    "timeFilters": {
      "today": "Hoy",
      "7d": "Últimos 7 días",
      "30d": "Últimos 30 días",
      "allTime": "Todo el tiempo"
    },
    "messages": {
      "updated": "Pedido {{id}} actualizado exitosamente",
      "updateError": "Error al actualizar el pedido",
      "loadError": "Error al cargar los pedidos"
    }
  },
  "clients": {
    "title": "Todos los Clientes",
    "description": "Gestiona la información de tus clientes.",
    "addClient": "Añadir Cliente",
    "searchPlaceholder": "Buscar por nombre o email...",
    "headers": {
      "client": "Cliente",
      "phone": "Teléfono",
      "joinDate": "Fecha de Registro",
      "totalSpent": "Gasto Total"
    },
    "noClients": "No se encontraron clientes. Intenta ajustar tu búsqueda.",
    "showingCount": "Mostrando {{count}} de {{total}} clientes",
    "back": "Volver a Todos los Clientes",
    "totalSpentLabel": "Gasto Total",
    "orderHistory": "Historial de Pedidos",
    "orderHistoryDesc": "Una lista de todas las compras realizadas por {{name}}.",
    "noOrders": "Este cliente aún no ha realizado ninguna compra.",
    "foundOrders": "Se encontraron {{count}} pedido(s) para este cliente.",
    "joinedOn": "Se unió el {{date}}"
  },
  "clientModal": {
    "addTitle": "Añadir Nuevo Cliente",
    "editTitle": "Editar Cliente",
    "labels": {
      "fullName": "Nombre Completo",
      "email": "Correo Electrónico",
      "phone": "Número de Teléfono"
    }
  },
  "campaigns": {
    "title": "Todas las Campañas",
    "description": "Gestiona tus campañas de marketing.",
    "addCampaign": "Añadir Campaña",
    "headers": {
      "campaign": "Campaña",
      "period": "Período",
      "products": "Productos",
      "budget": "Presupuesto"
    },
    "showingCount": "Mostrando {{count}} de {{total}} campañas",
    "messages": {
      "created": "Campaña '{{name}}' creada exitosamente",
      "updated": "Campaña '{{name}}' actualizada exitosamente",
      "deleted": "Campaña '{{name}}' eliminada exitosamente",
      "error": "Error al guardar la campaña. Inténtalo de nuevo.",
      "deleteError": "Error al eliminar la campaña. Inténtalo de nuevo."
    }
  },
  "campaignModal": {
    "addTitle": "Añadir Nueva Campaña",
    "editTitle": "Editar Campaña",
    "labels": {
      "name": "Nombre de la Campaña",
      "startDate": "Fecha de Inicio",
      "endDate": "Fecha de Fin",
      "budget": "Presupuesto",
      "productsOnSale": "Productos en Oferta"
    }
  },
  "discounts": {
    "title": "Todos los Descuentos",
    "description": "Crea y gestiona reglas de descuento para tu tienda.",
    "addDiscount": "Añadir Descuento",
    "showingCount": "Mostrando {{count}} de {{total}} descuentos",
    "targets": {
      "all": "Todos los Productos",
      "category": "Categoría: {{name}}",
      "product": "Producto: {{name}}"
    },
    "messages": {
      "created": "Descuento '{{name}}' creado exitosamente",
      "updated": "Descuento '{{name}}' actualizado exitosamente",
      "deleted": "Descuento '{{name}}' eliminado exitosamente",
      "error": "Error al guardar el descuento. Inténtalo de nuevo.",
      "deleteError": "Error al eliminar el descuento. Inténtalo de nuevo."
    }
  },
  "discountModal": {
    "addTitle": "Añadir Nuevo Descuento",
    "editTitle": "Editar Descuento",
    "labels": {
      "name": "Nombre del Descuento",
      "type": "Tipo",
      "value": "Valor",
      "target": "Objetivo",
      "category": "Categoría",
      "product": "Producto",
      "status": "Estado"
    },
    "targets": {
      "all": "Todos los Productos",
      "category": "Categoría Específica",
      "product": "Producto Específico"
    }
  },
  "confirmationModal": {
    "delete": "Eliminar",
    "titles": {
      "product": "Eliminar Producto",
      "campaign": "Eliminar Campaña",
      "discount": "Eliminar Descuento",
      "client": "Eliminar Cliente"
    },
    "messages": {
      "product": "¿Estás seguro de que quieres eliminar este producto? Esta acción no se puede deshacer.",
      "campaign": "¿Estás seguro de que quieres eliminar esta campaña? Esta acción no se puede deshacer.",
      "discount": "¿Estás seguro de que quieres eliminar esta regla de descuento? Esta acción no se puede deshacer.",
      "client": "¿Estás seguro de que quieres eliminar este cliente? Esta acción no se puede deshacer."
    }
  },
  "productStatus": {
    "Active": "Activo",
    "Archived": "Archivado",
    "Out of Stock": "Agotado"
  },
  "orderStatus": {
    "Pending": "Pendiente",
    "Received": "Recibido",
    "Shipping": "En Envío",
    "Delivered": "Entregado",
    "Cancelled": "Cancelado"
  },
  "campaignStatus": {
    "Active": "Activa",
    "Paused": "Pausada",
    "Completed": "Completada"
  },
  "discountStatus": {
    "active": "Activo",
    "inactive": "Inactivo"
  },
  "discountType": {
    "Percentage": "Porcentaje",
    "Fixed Amount": "Monto Fijo"
  }
};