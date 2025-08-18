// Tenant-aware API services with JWT authentication
// This file replaces the legacy api.ts for multi-tenant operations

const API_BASE_URL = 'http://127.0.0.1:8002';

// Get auth token from localStorage
function getAuthToken(): string | null {
  const authState = localStorage.getItem('authState');
  if (authState) {
    const parsed = JSON.parse(authState);
    return parsed.access_token;
  }
  return null;
}

// Generic API request function with JWT authentication
async function tenantApiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAuthToken();
  
  const config: RequestInit = {
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options?.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Tenant API Error ${response.status}:`, errorText);
      
      // If unauthorized, clear auth state and redirect to login
      if (response.status === 401) {
        localStorage.removeItem('authState');
        window.location.reload();
      }
      
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Tenant API request failed: ${endpoint}`, error);
    throw error;
  }
}

// Tenant Orders API (isolated by tenant)
export const tenantOrdersApi = {
  getAll: () => tenantApiRequest<any[]>('/api/tenant-orders/'),
  
  getById: (id: string) => tenantApiRequest<any>(`/api/tenant-orders/${id}`),
  
  create: (order: any) =>
    tenantApiRequest<any>('/api/tenant-orders/', {
      method: 'POST',
      body: JSON.stringify(order),
    }),
  
  update: (id: string, order: any) =>
    tenantApiRequest<any>(`/api/tenant-orders/${id}`, {
      method: 'PUT',
      body: JSON.stringify(order),
    }),
  
  delete: (id: string) =>
    tenantApiRequest<any>(`/api/tenant-orders/${id}`, {
      method: 'DELETE',
    }),
};

// Auth API (for authentication operations)
export const authApi = {
  login: (email: string, password: string, clientSlug?: string) =>
    tenantApiRequest<any>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password, client_slug: clientSlug }),
    }),
  
  register: (email: string, password: string, clientName?: string, clientSlug?: string) =>
    tenantApiRequest<any>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ 
        email, 
        password, 
        client_name: clientName,
        client_slug: clientSlug 
      }),
    }),
  
  refresh: (refreshToken: string) =>
    tenantApiRequest<any>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),
  
  getMe: () => tenantApiRequest<any>('/auth/me'),
};

// Legacy API compatibility layer - for gradual migration
// These should be used sparingly and eventually removed
export const legacyApi = {
  // Orders (without tenant filtering - UNSAFE)
  orders: {
    getAll: () => tenantApiRequest<any[]>('/api/orders'),
    create: (order: any) =>
      tenantApiRequest<any>('/api/orders', {
        method: 'POST',
        body: JSON.stringify(order),
      }),
  },
  
  // Clients (without tenant filtering - UNSAFE)
  clients: {
    getAll: () => tenantApiRequest<any[]>('/api/clients'),
  },
  
  // Products (without tenant filtering - UNSAFE)
  products: {
    getAll: () => tenantApiRequest<any[]>('/api/products'),
    create: (product: any) =>
      tenantApiRequest<any>('/api/products', {
        method: 'POST',
        body: JSON.stringify(product),
      }),
  },
};

// Dashboard API - should use tenant-aware data
export const tenantDashboardApi = {
  // For now, use tenant orders as the primary data source
  getStats: async () => {
    const orders = await tenantOrdersApi.getAll();
    
    // Calculate stats from tenant orders
    const totalRevenue = orders.reduce((sum, order) => 
      sum + (order.status !== 'Cancelled' ? (order.total || 0) : 0), 0);
    const totalOrders = orders.length;
    const completedOrders = orders.filter(o => o.status === 'Completed').length;
    const pendingOrders = orders.filter(o => o.status === 'Pending').length;
    
    return {
      totalRevenue,
      totalOrders,
      completedOrders,
      pendingOrders,
    };
  },
  
  getRecentOrders: async (limit = 10) => {
    const orders = await tenantOrdersApi.getAll();
    return orders
      .sort((a, b) => new Date(b.created_at || b.date).getTime() - new Date(a.created_at || a.date).getTime())
      .slice(0, limit);
  },
};

// Export for backward compatibility (gradual migration)
export const ordersApi = tenantOrdersApi;
export const dashboardApi = tenantDashboardApi;

// Mark legacy clients API as unsafe - should not be used in multi-tenant context
export const clientsApi = {
  getAll: () => {
    console.warn('WARNING: Using legacy clientsApi.getAll() - this is not tenant-aware!');
    console.warn('In multi-tenant context, client data should come from auth context, not API calls');
    return Promise.resolve([]);
  },
  
  create: (client: any) => {
    console.warn('WARNING: Using legacy clientsApi.create() - use auth registration instead');
    return Promise.reject(new Error('Use auth registration for client creation in multi-tenant setup'));
  },
  
  update: (id: string, client: any) => {
    console.warn('WARNING: Using legacy clientsApi.update() - not implemented in multi-tenant setup');
    return Promise.reject(new Error('Client updates not available in multi-tenant setup'));
  },
  
  delete: (id: string) => {
    console.warn('WARNING: Using legacy clientsApi.delete() - not implemented in multi-tenant setup');
    return Promise.reject(new Error('Client deletion not available in multi-tenant setup'));
  },
};