import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Types
interface User {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

interface Client {
  id: string;
  name: string;
  slug: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  client: Client | null;
  access_token: string | null;
  refresh_token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string, clientSlug?: string) => Promise<void>;
  register: (email: string, password: string, clientName?: string, clientSlug?: string) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<boolean>;
}

// Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Constants - Use relative URLs in production for multi-tenant support
const BASE_URL = process.env.NODE_ENV === 'production' 
  ? '' 
  : 'http://127.0.0.1:8002';
const TOKEN_REFRESH_THRESHOLD = 60 * 1000; // 60 seconds

// Local Storage Keys
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'auth_access_token',
  REFRESH_TOKEN: 'auth_refresh_token',
  USER: 'auth_user',
  CLIENT: 'auth_client',
  AUTH_STATE: 'authState', // For compatibility with tenant-api.ts
};

// API client with auto-refresh
class ApiClient {
  private static instance: ApiClient;
  private authContext: AuthContextType | null = null;

  static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
    }
    return ApiClient.instance;
  }

  setAuthContext(context: AuthContextType) {
    this.authContext = context;
  }

  private async makeRequest(url: string, options: RequestInit = {}): Promise<Response> {
    const headers = new Headers(options.headers);
    
    // Add auth header if available
    if (this.authContext?.access_token) {
      headers.set('Authorization', `Bearer ${this.authContext.access_token}`);
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle 401 responses
    if (response.status === 401 && this.authContext?.refresh_token) {
      const refreshSuccess = await this.authContext.refreshAccessToken();
      if (refreshSuccess && this.authContext.access_token) {
        // Retry with new token
        headers.set('Authorization', `Bearer ${this.authContext.access_token}`);
        return fetch(url, {
          ...options,
          headers,
        });
      }
    }

    return response;
  }

  async post(url: string, data: any): Promise<Response> {
    return this.makeRequest(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
  }

  async get(url: string): Promise<Response> {
    return this.makeRequest(url);
  }
}

// Token utilities
const isTokenExpiringSoon = (token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000; // Convert to milliseconds
    const now = Date.now();
    return (exp - now) < TOKEN_REFRESH_THRESHOLD;
  } catch {
    return true;
  }
};

const clearStorage = () => {
  Object.values(STORAGE_KEYS).forEach(key => {
    localStorage.removeItem(key);
  });
};

const saveToStorage = (data: {
  access_token: string;
  refresh_token: string;
  user: User;
  client: Client;
}) => {
  localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, data.access_token);
  localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, data.refresh_token);
  localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(data.user));
  localStorage.setItem(STORAGE_KEYS.CLIENT, JSON.stringify(data.client));
  
  // Also save in authState format for compatibility with tenant-api.ts
  localStorage.setItem(STORAGE_KEYS.AUTH_STATE, JSON.stringify({
    access_token: data.access_token,
    refresh_token: data.refresh_token,
    user: data.user,
    client: data.client,
    isAuthenticated: true,
  }));
};

const loadFromStorage = (): Partial<AuthState> => {
  try {
    const access_token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    const refresh_token = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    const userStr = localStorage.getItem(STORAGE_KEYS.USER);
    const clientStr = localStorage.getItem(STORAGE_KEYS.CLIENT);

    if (!access_token || !refresh_token || !userStr || !clientStr) {
      return {};
    }

    return {
      access_token,
      refresh_token,
      user: JSON.parse(userStr),
      client: JSON.parse(clientStr),
    };
  } catch {
    clearStorage();
    return {};
  }
};

// Provider Component
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    client: null,
    access_token: null,
    refresh_token: null,
    isAuthenticated: false,
    isLoading: true,
  });

  const apiClient = ApiClient.getInstance();

  // Load auth state from localStorage on mount
  useEffect(() => {
    const savedData = loadFromStorage();
    if (savedData.access_token && savedData.user && savedData.client) {
      setAuthState({
        ...savedData as AuthState,
        isAuthenticated: true,
        isLoading: false,
      });
    } else {
      setAuthState(prev => ({ ...prev, isLoading: false }));
    }
  }, []);

  // Auto-refresh token when it's about to expire
  useEffect(() => {
    if (!authState.access_token || !authState.isAuthenticated) return;

    const checkTokenExpiry = () => {
      if (isTokenExpiringSoon(authState.access_token!)) {
        refreshAccessToken();
      }
    };

    const interval = setInterval(checkTokenExpiry, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, [authState.access_token, authState.isAuthenticated]);

  const login = async (email: string, password: string, clientSlug?: string): Promise<void> => {
    try {
      const response = await fetch(`${BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, client_slug: clientSlug }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      
      setAuthState({
        user: data.user,
        client: data.client,
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        isAuthenticated: true,
        isLoading: false,
      });

      saveToStorage(data);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (
    email: string, 
    password: string, 
    clientName?: string, 
    clientSlug?: string
  ): Promise<void> => {
    try {
      const response = await fetch(`${BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email, 
          password, 
          client_name: clientName,
          client_slug: clientSlug 
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
      }

      const data = await response.json();
      
      setAuthState({
        user: data.user,
        client: data.client,
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        isAuthenticated: true,
        isLoading: false,
      });

      saveToStorage(data);
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  const logout = (): void => {
    setAuthState({
      user: null,
      client: null,
      access_token: null,
      refresh_token: null,
      isAuthenticated: false,
      isLoading: false,
    });
    clearStorage();
  };

  const refreshAccessToken = async (): Promise<boolean> => {
    if (!authState.refresh_token) {
      logout();
      return false;
    }

    try {
      const response = await fetch(`${BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: authState.refresh_token }),
      });

      if (!response.ok) {
        logout();
        return false;
      }

      const data = await response.json();
      
      const newState = {
        ...authState,
        access_token: data.access_token,
      };

      setAuthState(newState);
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, data.access_token);
      
      // Also update authState for compatibility with tenant-api.ts
      const authStateData = JSON.parse(localStorage.getItem(STORAGE_KEYS.AUTH_STATE) || '{}');
      authStateData.access_token = data.access_token;
      localStorage.setItem(STORAGE_KEYS.AUTH_STATE, JSON.stringify(authStateData));
      
      return true;
    } catch (error) {
      console.error('Token refresh error:', error);
      logout();
      return false;
    }
  };

  const contextValue: AuthContextType = {
    ...authState,
    login,
    register,
    logout,
    refreshAccessToken,
  };

  // Set API client context
  useEffect(() => {
    apiClient.setAuthContext(contextValue);
  }, [authState.access_token]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Export API client for use in components
export { ApiClient };