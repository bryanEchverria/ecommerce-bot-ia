import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';

// Global flag to ensure initialization happens only once
let isInitialized = false;

// Define translations directly inline to avoid import issues
const esTranslations = {
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
  "productStatus": {
    "Active": "Activo",
    "Archived": "Archivado",
    "Out of Stock": "Agotado"
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
  "clientModal": {
    "addTitle": "Añadir Nuevo Cliente",
    "editTitle": "Editar Cliente",
    "labels": {
      "fullName": "Nombre Completo",
      "email": "Correo Electrónico",
      "phone": "Número de Teléfono"
    }
  }
};

const enTranslations = {
  "common": {
    "edit": "Edit",
    "delete": "Delete",
    "cancel": "Cancel",
    "save": "Save",
    "saveProduct": "Save Product",
    "saveCampaign": "Save Campaign",
    "saveDiscount": "Save Discount",
    "saveClient": "Save Client",
    "status": "Status",
    "actions": "Actions",
    "all": "All",
    "name": "Name",
    "category": "Category",
    "price": "Price",
    "stock": "Stock",
    "units": "{{count}} units",
    "clicks": "Clicks",
    "conversions": "Conversions",
    "type": "Type",
    "value": "Value",
    "target": "Target",
    "search": "Search..."
  },
  "sidebar": {
    "title": "E-commerce",
    "dashboard": "Dashboard",
    "products": "Products",
    "orders": "Orders",
    "clients": "Clients",
    "campaigns": "Campaigns",
    "discounts": "Discounts",
    "copyright": "© 2024 E-commerce Inc.",
    "rightsReserved": "All rights reserved."
  },
  "header": {
    "titles": {
      "dashboard": "Dashboard Overview",
      "products": "Product Management",
      "orders": "Order Tracking",
      "clients": "Client Management",
      "campaigns": "Campaign Management",
      "discounts": "Discount Management",
      "default": "Dashboard"
    }
  },
  "dashboard": {
    "timeFilters": {
      "today": "Today",
      "7d": "Last 7 Days",
      "30d": "Last 30 Days",
      "1y": "Last Year"
    },
    "cards": {
      "totalRevenue": "Total Revenue",
      "sales": "Sales",
      "newOrders": "New Orders",
      "newCustomers": "New Customers"
    },
    "changeLabels": {
      "today": "from yesterday",
      "7d": "from prev. 7 days",
      "30d": "from prev. 30 days",
      "1y": "from last year"
    },
    "salesTrend": {
      "title": "Sales Trend"
    },
    "recentOrders": {
      "title": "Recent Orders",
      "headers": {
        "orderId": "Order ID",
        "orderNumber": "Order Number",
        "customer": "Customer",
        "date": "Date",
        "status": "Status",
        "total": "Total"
      },
      "noOrders": "No orders found for this period."
    }
  },
  "products": {
    "title": "All Products",
    "description": "Manage your product inventory and details.",
    "addProduct": "Add Product",
    "searchPlaceholder": "Search by product name...",
    "table": {
      "productName": "Product Name"
    },
    "noProducts": "No products found. Try adjusting your filters.",
    "showingCount": "Showing {{count}} of {{total}} products",
    "messages": {
      "created": "Product '{{name}}' created successfully",
      "updated": "Product '{{name}}' updated successfully",
      "deleted": "Product '{{name}}' deleted successfully",
      "error": "Error saving product. Please try again.",
      "deleteError": "Error deleting product. Please try again."
    }
  },
  "orders": {
    "title": "All Orders",
    "description": "Track and manage customer orders.",
    "export": "Export CSV",
    "headers": {
      "orderId": "Order ID",
      "orderNumber": "Order Number",
      "customerName": "Customer Name",
      "date": "Date",
      "items": "Items",
      "total": "Total"
    },
    "showingCount": "Showing {{count}} of {{total}} orders",
    "searchPlaceholder": "Search by Order Number or Customer...",
    "filterByStatus": "Filter by status",
    "allStatuses": "All Statuses",
    "noOrders": "No orders found. Try adjusting your filters.",
    "timeFilters": {
      "today": "Today",
      "7d": "Last 7 Days",
      "30d": "Last 30 Days",
      "allTime": "All Time"
    },
    "messages": {
      "updated": "Order {{id}} updated successfully",
      "updateError": "Error updating order",
      "loadError": "Error loading orders"
    }
  },
  "productStatus": {
    "Active": "Active",
    "Archived": "Archived",
    "Out of Stock": "Out of Stock"
  },
  "clients": {
    "title": "All Clients",
    "description": "Manage your client information.",
    "addClient": "Add Client",
    "searchPlaceholder": "Search by name or email...",
    "headers": {
      "client": "Client",
      "phone": "Phone",
      "joinDate": "Join Date",
      "totalSpent": "Total Spent"
    },
    "noClients": "No clients found. Try adjusting your search.",
    "showingCount": "Showing {{count}} of {{total}} clients",
    "back": "Back to All Clients",
    "totalSpentLabel": "Total Spent",
    "orderHistory": "Order History",
    "orderHistoryDesc": "A list of all purchases made by {{name}}.",
    "noOrders": "This client has not made any purchases yet.",
    "foundOrders": "Found {{count}} order(s) for this client.",
    "joinedOn": "Joined on {{date}}"
  },
  "campaigns": {
    "title": "All Campaigns",
    "description": "Manage your marketing campaigns.",
    "addCampaign": "Add Campaign",
    "headers": {
      "campaign": "Campaign",
      "period": "Period",
      "products": "Products",
      "budget": "Budget"
    },
    "showingCount": "Showing {{count}} of {{total}} campaigns",
    "messages": {
      "created": "Campaign '{{name}}' created successfully",
      "updated": "Campaign '{{name}}' updated successfully",
      "deleted": "Campaign '{{name}}' deleted successfully",
      "error": "Error saving campaign. Please try again.",
      "deleteError": "Error deleting campaign. Please try again."
    }
  },
  "campaignModal": {
    "addTitle": "Add New Campaign",
    "editTitle": "Edit Campaign",
    "labels": {
      "name": "Campaign Name",
      "startDate": "Start Date",
      "endDate": "End Date",
      "budget": "Budget",
      "productsOnSale": "Products on Sale"
    }
  },
  "discounts": {
    "title": "All Discounts",
    "description": "Create and manage discount rules for your store.",
    "addDiscount": "Add Discount",
    "showingCount": "Showing {{count}} of {{total}} discounts",
    "targets": {
      "all": "All Products",
      "category": "Category: {{name}}",
      "product": "Product: {{name}}"
    },
    "messages": {
      "created": "Discount '{{name}}' created successfully",
      "updated": "Discount '{{name}}' updated successfully",
      "deleted": "Discount '{{name}}' deleted successfully",
      "error": "Error saving discount. Please try again.",
      "deleteError": "Error deleting discount. Please try again."
    }
  },
  "discountModal": {
    "addTitle": "Add New Discount",
    "editTitle": "Edit Discount",
    "labels": {
      "name": "Discount Name",
      "type": "Type",
      "value": "Value",
      "target": "Target",
      "category": "Category",
      "product": "Product",
      "status": "Status"
    },
    "targets": {
      "all": "All Products",
      "category": "Specific Category",
      "product": "Specific Product"
    }
  },
  "confirmationModal": {
    "delete": "Delete",
    "titles": {
      "product": "Delete Product",
      "campaign": "Delete Campaign",
      "discount": "Delete Discount",
      "client": "Delete Client"
    },
    "messages": {
      "product": "Are you sure you want to delete this product? This action cannot be undone.",
      "campaign": "Are you sure you want to delete this campaign? This action cannot be undone.",
      "discount": "Are you sure you want to delete this discount rule? This action cannot be undone.",
      "client": "Are you sure you want to delete this client? This action cannot be undone."
    }
  },
  "productModal": {
    "addTitle": "Add New Product",
    "editTitle": "Edit Product",
    "labels": {
      "productName": "Product Name",
      "category": "Category",
      "status": "Status",
      "price": "Price",
      "salePrice": "Sale Price (Optional)",
      "stock": "Stock"
    }
  },
  "clientModal": {
    "addTitle": "Add New Client",
    "editTitle": "Edit Client",
    "labels": {
      "fullName": "Full Name",
      "email": "Email Address",
      "phone": "Phone Number"
    }
  }
};

const initI18n = () => {
  if (isInitialized) {
    return Promise.resolve(i18next);
  }

  return new Promise((resolve) => {
    i18next
      .use(initReactI18next)
      .init({
        lng: 'es',
        fallbackLng: 'es',
        debug: false,
        interpolation: {
          escapeValue: false,
        },
        resources: {
          en: {
            translation: enTranslations
          },
          es: {
            translation: esTranslations
          }
        }
      }, (err) => {
        if (!err) {
          isInitialized = true;
          i18next.changeLanguage('es');
          console.log('i18n initialized successfully with Spanish');
        } else {
          console.error('i18n initialization failed:', err);
        }
        resolve(i18next);
      });
  });
};

// Initialize immediately and make available globally
window.initI18n = initI18n;
initI18n();

export default i18next;