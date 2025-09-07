// Tenant-aware API services with JWT authentication and automatic subdomain detection
// This file provides multi-tenant API support with dynamic URL configuration

// Auto-detect current hostname for API calls
function getCurrentHostname(): string {
  if (typeof window !== 'undefined') {
    return window.location.hostname;
  }
  return 'localhost';
}

// Get the appropriate API base URL based on environment and current hostname
function getApiBaseUrl(): string {
  if (process.env.NODE_ENV === 'production') {
    // Use relative URLs in production - nginx will proxy to backend
    // This allows each subdomain to proxy to the same backend with different tenant context
    return '';
  }
  // In development, use localhost with port 8001
  return 'http://127.0.0.1:8001';
}

const API_BASE_URL = getApiBaseUrl();
const AUTH_BASE_URL = getApiBaseUrl();

// Get auth token from localStorage with fallback support
function getAuthToken(): string | null {
  // Try new format first (AuthContext)
  const token = localStorage.getItem('auth_access_token');
  if (token) {
    return token;
  }
  
  // Fallback to old format for compatibility
  const authState = localStorage.getItem('authState');
  if (authState) {
    try {
      const parsed = JSON.parse(authState);
      return parsed.access_token;
    } catch {
      return null;
    }
  }
  return null;
}

// Generic API request function with JWT authentication
async function tenantApiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}/api${endpoint}`;
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
      
      // If unauthorized, clear all auth state and redirect to login
      if (response.status === 401) {
        localStorage.removeItem('authState');
        localStorage.removeItem('auth_access_token');
        localStorage.removeItem('auth_refresh_token');
        localStorage.removeItem('auth_user');
        localStorage.removeItem('auth_client');
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

// Auth-specific request function (uses different base URL)
async function authApiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${AUTH_BASE_URL}${endpoint}`;
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
      console.error(`Auth API Error ${response.status}:`, errorText);
      
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Auth API request failed: ${endpoint}`, error);
    throw error;
  }
}

// Tenant Orders API (isolated by tenant)
export const tenantOrdersApi = {
  getAll: async () => {
    const response = await tenantApiRequest<{pedidos: any[]}>('/flow-orders/');
    return response.pedidos;
  },
  
  getById: (id: string) => tenantApiRequest<any>(`/flow-orders/${id}`),
  
  create: (order: any) =>
    tenantApiRequest<any>('/tenant-orders/', {
      method: 'POST',
      body: JSON.stringify(order),
    }),
  
  update: (id: string, order: any) =>
    tenantApiRequest<any>(`/tenant-orders/${id}`, {
      method: 'PUT',
      body: JSON.stringify(order),
    }),
  
  delete: (id: string) =>
    tenantApiRequest<any>(`/tenant-orders/${id}`, {
      method: 'DELETE',
    }),
};

// Auth API (for authentication operations)
export const authApi = {
  login: (email: string, password: string, clientSlug?: string) =>
    authApiRequest<any>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password, client_slug: clientSlug }),
    }),
  
  register: (email: string, password: string, clientName?: string, clientSlug?: string) =>
    authApiRequest<any>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ 
        email, 
        password, 
        client_name: clientName,
        client_slug: clientSlug 
      }),
    }),
  
  refresh: (refreshToken: string) =>
    authApiRequest<any>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),
  
  getMe: () => authApiRequest<any>('/auth/me'),
};

// Legacy API compatibility layer - for gradual migration
// These should be used sparingly and eventually removed
export const legacyApi = {
  // Orders (without tenant filtering - UNSAFE)
  orders: {
    getAll: () => tenantApiRequest<any[]>('/orders'),
    create: (order: any) =>
      tenantApiRequest<any>('/orders', {
        method: 'POST',
        body: JSON.stringify(order),
      }),
  },
  
  // Clients (without tenant filtering - UNSAFE)
  clients: {
    getAll: () => tenantApiRequest<any[]>('/clients'),
  },
  
  // Products (without tenant filtering - UNSAFE)
  products: {
    getAll: () => tenantApiRequest<any[]>('/products'),
    create: (product: any) =>
      tenantApiRequest<any>('/products', {
        method: 'POST',
        body: JSON.stringify(product),
      }),
  },
};

// Dashboard API - tenant-aware with dynamic URLs
export const tenantDashboardApi = {
  // Use Flow orders with tenant-aware API calls
  getStats: async () => {
    try {
      const response = await tenantApiRequest<{pedidos: any[]}>('/flow-orders/');
      const orders = response.pedidos || [];
      
      // Calculate stats from Flow orders
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
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      return { totalRevenue: 0, totalOrders: 0, completedOrders: 0, pendingOrders: 0 };
    }
  },
  
  getRecentOrders: async (limit = 10) => {
    try {
      const response = await tenantApiRequest<{pedidos: any[]}>('/flow-orders/');
      const orders = response.pedidos || [];
      return orders
        .sort((a, b) => new Date(b.created_at || b.date).getTime() - new Date(a.created_at || a.date).getTime())
        .slice(0, limit);
    } catch (error) {
      console.error('Error fetching recent orders:', error);
      return [];
    }
  },
};

// Tenant-aware Products API (automatically filtered by backend tenant middleware)
export const tenantProductsApi = {
  getAll: () => tenantApiRequest<any[]>('/products'),
  
  getById: (id: string) => tenantApiRequest<any>(`/products/${id}`),
  
  create: (product: any) =>
    tenantApiRequest<any>('/products', {
      method: 'POST',
      body: JSON.stringify(product),
    }),
  
  update: (id: string, product: any) =>
    tenantApiRequest<any>(`/products/${id}`, {
      method: 'PUT',
      body: JSON.stringify(product),
    }),
  
  delete: (id: string) =>
    tenantApiRequest<any>(`/products/${id}`, {
      method: 'DELETE',
    }),
};

// Tenant-aware Campaigns API (automatically filtered by backend tenant middleware)
export const tenantCampaignsApi = {
  getAll: () => tenantApiRequest<any[]>('/campaigns'),
  
  getById: (id: string) => tenantApiRequest<any>(`/campaigns/${id}`),
  
  create: (campaign: any) =>
    tenantApiRequest<any>('/campaigns', {
      method: 'POST',
      body: JSON.stringify(campaign),
    }),
  
  update: (id: string, campaign: any) =>
    tenantApiRequest<any>(`/campaigns/${id}`, {
      method: 'PUT',
      body: JSON.stringify(campaign),
    }),
  
  delete: (id: string) =>
    tenantApiRequest<any>(`/campaigns/${id}`, {
      method: 'DELETE',
    }),
};

// Tenant-aware Discounts API (automatically filtered by backend tenant middleware)
export const tenantDiscountsApi = {
  getAll: () => tenantApiRequest<any[]>('/discounts'),
  
  getById: (id: string) => tenantApiRequest<any>(`/discounts/${id}`),
  
  create: (discount: any) =>
    tenantApiRequest<any>('/discounts', {
      method: 'POST',
      body: JSON.stringify(discount),
    }),
  
  update: (id: string, discount: any) =>
    tenantApiRequest<any>(`/discounts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(discount),
    }),
  
  delete: (id: string) =>
    tenantApiRequest<any>(`/discounts/${id}`, {
      method: 'DELETE',
    }),
};

// Export for backward compatibility (gradual migration)
export const ordersApi = tenantOrdersApi;
export const dashboardApi = tenantDashboardApi;

// NEW SECURE API EXPORTS - Use these instead of legacy api.ts
export const productsApi = tenantProductsApi;
export const campaignsApi = tenantCampaignsApi;
export const discountsApi = tenantDiscountsApi;

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