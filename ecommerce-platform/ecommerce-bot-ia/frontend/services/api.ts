// ⚠️ DEPRECATED: This file is deprecated and unsafe for multi-tenant use
// Use 'tenant-api.ts' instead for proper tenant isolation
// This file will be removed in future versions

console.warn('WARNING: Using deprecated api.ts - migrate to tenant-api.ts for multi-tenant safety');

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '' 
  : 'http://127.0.0.1:8001';

// Get auth token from localStorage
function getAuthToken(): string | null {
  // Try the AuthContext storage key first
  const token = localStorage.getItem('auth_access_token');
  if (token) {
    return token;
  }
  
  // Fallback to old format for backwards compatibility
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
async function apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
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
      console.error(`API Error ${response.status}:`, errorText);
      
      // If unauthorized, clear auth state and redirect to login
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

    // Handle responses - try to parse JSON, fallback to success indicator
    try {
      const text = await response.text();
      if (text) {
        return JSON.parse(text);
      } else {
        // Empty response body
        return { success: true, status: response.status } as T;
      }
    } catch (jsonError) {
      // If JSON parsing fails, return success indicator for successful HTTP status
      return { success: true, status: response.status } as T;
    }
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error);
    throw error;
  }
}

// Products API
export const productsApi = {
  getAll: () => apiRequest<any[]>('/products'),
  
  create: (product: any) => 
    apiRequest<any>('/products', {
      method: 'POST',
      body: JSON.stringify(product),
    }),
  
  update: (id: string, product: any) =>
    apiRequest<any>(`/products/${id}`, {
      method: 'PUT',
      body: JSON.stringify(product),
    }),
  
  delete: (id: string) =>
    apiRequest<any>(`/products/${id}`, {
      method: 'DELETE',
    }),
};

// Orders API
export const ordersApi = {
  getAll: () => apiRequest<any[]>('/orders'),
  
  create: (order: any) =>
    apiRequest<any>('/orders', {
      method: 'POST',
      body: JSON.stringify(order),
    }),
  
  update: (id: string, order: any) =>
    apiRequest<any>(`/orders/${id}`, {
      method: 'PUT',
      body: JSON.stringify(order),
    }),
  
  delete: (id: string) =>
    apiRequest<any>(`/orders/${id}`, {
      method: 'DELETE',
    }),
};

// Clients API
export const clientsApi = {
  getAll: () => apiRequest<any[]>('/clients'),
  
  create: (client: any) =>
    apiRequest<any>('/clients', {
      method: 'POST',
      body: JSON.stringify(client),
    }),
  
  update: (id: string, client: any) =>
    apiRequest<any>(`/clients/${id}`, {
      method: 'PUT',
      body: JSON.stringify(client),
    }),
  
  delete: (id: string) =>
    apiRequest<any>(`/clients/${id}`, {
      method: 'DELETE',
    }),
};

// Campaigns API
export const campaignsApi = {
  getAll: () => apiRequest<any[]>('/campaigns'),
  
  create: (campaign: any) =>
    apiRequest<any>('/campaigns', {
      method: 'POST',
      body: JSON.stringify(campaign),
    }),
  
  update: (id: string, campaign: any) =>
    apiRequest<any>(`/campaigns/${id}`, {
      method: 'PUT',
      body: JSON.stringify(campaign),
    }),
  
  delete: (id: string) =>
    apiRequest<any>(`/campaigns/${id}`, {
      method: 'DELETE',
    }),
};

// Discounts API
export const discountsApi = {
  getAll: () => apiRequest<any[]>('/discounts'),
  
  create: (discount: any) =>
    apiRequest<any>('/discounts', {
      method: 'POST',
      body: JSON.stringify(discount),
    }),
  
  update: (id: string, discount: any) =>
    apiRequest<any>(`/discounts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(discount),
    }),
  
  delete: (id: string) =>
    apiRequest<any>(`/discounts/${id}`, {
      method: 'DELETE',
    }),
};

// Dashboard API
export const dashboardApi = {
  getStats: () => apiRequest<any>('/dashboard/stats'),
  getRecentOrders: (limit = 10) => apiRequest<any[]>(`/dashboard/recent-orders?limit=${limit}`),
  getLowStockProducts: (threshold = 10) => apiRequest<any[]>(`/dashboard/low-stock-products?threshold=${threshold}`),
  getRevenueSummary: () => apiRequest<any>('/dashboard/revenue-summary'),
};

// Assistant API
export const assistantApi = {
  query: (query: string) =>
    apiRequest<any>('/assistant/query', {
      method: 'POST',
      body: JSON.stringify({ query }),
    }),
  
  getStats: () => apiRequest<any>('/assistant/stats'),
};