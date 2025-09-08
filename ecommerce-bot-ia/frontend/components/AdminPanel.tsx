import React, { useState, useEffect } from 'react';
import { useToast } from './Toast';
import { PlusIcon, TrashIcon, PencilIcon, SettingsIcon } from './Icons';

interface TenantClient {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  user_count: number;
  status: string;
}

interface TenantUser {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

interface TenantClientDetail {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  users: TenantUser[];
}

interface CreateClientForm {
  name: string;
  slug: string;
  admin_email: string;
  admin_password: string;
}

interface CreateUserForm {
  email: string;
  password: string;
  role: string;
}

const AdminPanel: React.FC = () => {
  const [clients, setClients] = useState<TenantClient[]>([]);
  const [selectedClient, setSelectedClient] = useState<TenantClientDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateClient, setShowCreateClient] = useState(false);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const { showToast } = useToast();

  // Form states
  const [clientForm, setClientForm] = useState<CreateClientForm>({
    name: '',
    slug: '',
    admin_email: '',
    admin_password: ''
  });
  
  const [userForm, setUserForm] = useState<CreateUserForm>({
    email: '',
    password: '',
    role: 'user'
  });

  // Get API base URL
  const getApiUrl = () => {
    if (process.env.NODE_ENV === 'production') {
      return '';
    }
    return 'http://127.0.0.1:8002';
  };

  const apiRequest = async (endpoint: string, options?: RequestInit) => {
    const url = `${getApiUrl()}/api${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error ${response.status}: ${errorText}`);
    }

    return response.json();
  };

  const loadClients = async () => {
    try {
      const data = await apiRequest('/admin/clients');
      setClients(data);
    } catch (error: any) {
      console.error('Error loading clients:', error);
      showToast('Error cargando clientes: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadClientDetail = async (clientId: string) => {
    try {
      const data = await apiRequest(`/admin/clients/${clientId}`);
      setSelectedClient(data);
    } catch (error: any) {
      console.error('Error loading client detail:', error);
      showToast('Error cargando detalles del cliente: ' + error.message, 'error');
    }
  };

  const createClient = async () => {
    try {
      // Validate slug format
      const slugRegex = /^[a-z0-9-]+$/;
      if (!slugRegex.test(clientForm.slug)) {
        showToast('El slug debe contener solo letras minúsculas, números y guiones', 'error');
        return;
      }

      await apiRequest('/admin/clients', {
        method: 'POST',
        body: JSON.stringify(clientForm),
      });

      showToast('Cliente creado exitosamente', 'success');
      setShowCreateClient(false);
      setClientForm({ name: '', slug: '', admin_email: '', admin_password: '' });
      loadClients();
    } catch (error: any) {
      console.error('Error creating client:', error);
      showToast('Error creando cliente: ' + error.message, 'error');
    }
  };

  const createUser = async () => {
    if (!selectedClient) return;

    try {
      await apiRequest(`/admin/clients/${selectedClient.id}/users`, {
        method: 'POST',
        body: JSON.stringify(userForm),
      });

      showToast('Usuario creado exitosamente', 'success');
      setShowCreateUser(false);
      setUserForm({ email: '', password: '', role: 'user' });
      loadClientDetail(selectedClient.id);
    } catch (error: any) {
      console.error('Error creating user:', error);
      showToast('Error creando usuario: ' + error.message, 'error');
    }
  };

  const deleteClient = async (clientId: string, slug: string) => {
    if (!confirm(`¿Está seguro de eliminar el cliente "${slug}" y todos sus usuarios? Esta acción no se puede deshacer.`)) {
      return;
    }

    try {
      await apiRequest(`/admin/clients/${clientId}`, {
        method: 'DELETE',
      });

      showToast('Cliente eliminado exitosamente', 'success');
      loadClients();
      if (selectedClient?.id === clientId) {
        setSelectedClient(null);
      }
    } catch (error: any) {
      console.error('Error deleting client:', error);
      showToast('Error eliminando cliente: ' + error.message, 'error');
    }
  };

  const deleteUser = async (userId: string, email: string) => {
    if (!confirm(`¿Está seguro de eliminar el usuario "${email}"?`)) {
      return;
    }

    try {
      await apiRequest(`/admin/users/${userId}`, {
        method: 'DELETE',
      });

      showToast('Usuario eliminado exitosamente', 'success');
      if (selectedClient) {
        loadClientDetail(selectedClient.id);
      }
    } catch (error: any) {
      console.error('Error deleting user:', error);
      showToast('Error eliminando usuario: ' + error.message, 'error');
    }
  };

  const generateSlug = (name: string) => {
    return name
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Remove accents
      .replace(/[^a-z0-9\s-]/g, '') // Remove special chars
      .replace(/\s+/g, '-') // Replace spaces with hyphens
      .replace(/-+/g, '-') // Remove duplicate hyphens
      .trim();
  };

  useEffect(() => {
    loadClients();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface-light dark:text-on-surface-dark">
            Panel de Administración
          </h1>
          <p className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">
            Gestión de clientes y usuarios del sistema multi-tenant
          </p>
        </div>
        <SettingsIcon className="h-8 w-8 text-primary" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Clients List */}
        <div className="bg-surface-light dark:bg-surface-dark rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">
              Clientes ({clients.length})
            </h2>
            <button
              onClick={() => setShowCreateClient(true)}
              className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
            >
              <PlusIcon className="h-4 w-4" />
              Nuevo Cliente
            </button>
          </div>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {clients.map((client) => (
              <div
                key={client.id}
                className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                  selectedClient?.id === client.id
                    ? 'border-primary bg-primary/10'
                    : 'border-outline-light dark:border-outline-dark hover:bg-surface-light/50 dark:hover:bg-surface-dark/50'
                }`}
                onClick={() => loadClientDetail(client.id)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-on-surface-light dark:text-on-surface-dark">
                      {client.name}
                    </h3>
                    <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                      {client.slug} • {client.user_count} usuarios
                    </p>
                    <p className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                      Creado: {new Date(client.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteClient(client.id, client.slug);
                    }}
                    className="text-red-500 hover:text-red-700 p-1"
                    title="Eliminar cliente"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Client Detail */}
        <div className="bg-surface-light dark:bg-surface-dark rounded-lg p-6">
          {selectedClient ? (
            <>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">
                    {selectedClient.name}
                  </h2>
                  <p className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                    {selectedClient.slug} • {selectedClient.users.length} usuarios
                  </p>
                </div>
                <button
                  onClick={() => setShowCreateUser(true)}
                  className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                >
                  <PlusIcon className="h-4 w-4" />
                  Nuevo Usuario
                </button>
              </div>

              <div className="space-y-3 max-h-80 overflow-y-auto">
                {selectedClient.users.map((user) => (
                  <div
                    key={user.id}
                    className="p-3 rounded-lg border border-outline-light dark:border-outline-dark"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium text-on-surface-light dark:text-on-surface-dark">
                            {user.email}
                          </p>
                          <span
                            className={`px-2 py-1 rounded-full text-xs ${
                              user.role === 'admin'
                                ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
                                : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                            }`}
                          >
                            {user.role}
                          </span>
                          <span
                            className={`px-2 py-1 rounded-full text-xs ${
                              user.is_active
                                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                                : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                            }`}
                          >
                            {user.is_active ? 'Activo' : 'Inactivo'}
                          </span>
                        </div>
                        <p className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                          Creado: {new Date(user.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <button
                        onClick={() => deleteUser(user.id, user.email)}
                        className="text-red-500 hover:text-red-700 p-1"
                        title="Eliminar usuario"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-4 pt-4 border-t border-outline-light dark:border-outline-dark">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                    URL del cliente:
                  </span>
                  <code className="bg-background-light dark:bg-background-dark px-2 py-1 rounded text-on-surface-light dark:text-on-surface-dark">
                    https://{selectedClient.slug}.sintestesia.cl
                  </code>
                </div>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-64 text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
              Selecciona un cliente para ver sus detalles
            </div>
          )}
        </div>
      </div>

      {/* Create Client Modal */}
      {showCreateClient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-surface-light dark:bg-surface-dark rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-on-surface-light dark:text-on-surface-dark mb-4">
              Crear Nuevo Cliente
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                  Nombre del Cliente
                </label>
                <input
                  type="text"
                  value={clientForm.name}
                  onChange={(e) => {
                    const name = e.target.value;
                    setClientForm({
                      ...clientForm,
                      name,
                      slug: generateSlug(name)
                    });
                  }}
                  className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-lg bg-background-light dark:bg-background-dark text-on-surface-light dark:text-on-surface-dark"
                  placeholder="Ej: ACME Corporation"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                  Slug (Subdominio)
                </label>
                <input
                  type="text"
                  value={clientForm.slug}
                  onChange={(e) => setClientForm({ ...clientForm, slug: e.target.value })}
                  className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-lg bg-background-light dark:bg-background-dark text-on-surface-light dark:text-on-surface-dark"
                  placeholder="acme"
                />
                <p className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">
                  URL: https://{clientForm.slug || 'slug'}.sintestesia.cl
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                  Email del Administrador
                </label>
                <input
                  type="email"
                  value={clientForm.admin_email}
                  onChange={(e) => setClientForm({ ...clientForm, admin_email: e.target.value })}
                  className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-lg bg-background-light dark:bg-background-dark text-on-surface-light dark:text-on-surface-dark"
                  placeholder="admin@acme.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                  Contraseña del Administrador
                </label>
                <input
                  type="password"
                  value={clientForm.admin_password}
                  onChange={(e) => setClientForm({ ...clientForm, admin_password: e.target.value })}
                  className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-lg bg-background-light dark:bg-background-dark text-on-surface-light dark:text-on-surface-dark"
                  placeholder="Contraseña segura"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowCreateClient(false)}
                className="flex-1 px-4 py-2 border border-outline-light dark:border-outline-dark rounded-lg text-on-surface-light dark:text-on-surface-dark hover:bg-surface-light/50 dark:hover:bg-surface-dark/50"
              >
                Cancelar
              </button>
              <button
                onClick={createClient}
                disabled={!clientForm.name || !clientForm.slug || !clientForm.admin_email || !clientForm.admin_password}
                className="flex-1 px-4 py-2 bg-primary hover:bg-primary/90 disabled:bg-primary/50 text-white rounded-lg"
              >
                Crear Cliente
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create User Modal */}
      {showCreateUser && selectedClient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-surface-light dark:bg-surface-dark rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-on-surface-light dark:text-on-surface-dark mb-4">
              Crear Usuario para {selectedClient.name}
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                  Email del Usuario
                </label>
                <input
                  type="email"
                  value={userForm.email}
                  onChange={(e) => setUserForm({ ...userForm, email: e.target.value })}
                  className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-lg bg-background-light dark:bg-background-dark text-on-surface-light dark:text-on-surface-dark"
                  placeholder="usuario@ejemplo.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                  Contraseña
                </label>
                <input
                  type="password"
                  value={userForm.password}
                  onChange={(e) => setUserForm({ ...userForm, password: e.target.value })}
                  className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-lg bg-background-light dark:bg-background-dark text-on-surface-light dark:text-on-surface-dark"
                  placeholder="Contraseña segura"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                  Rol
                </label>
                <select
                  value={userForm.role}
                  onChange={(e) => setUserForm({ ...userForm, role: e.target.value })}
                  className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-lg bg-background-light dark:bg-background-dark text-on-surface-light dark:text-on-surface-dark"
                >
                  <option value="user">Usuario</option>
                  <option value="admin">Administrador</option>
                </select>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowCreateUser(false)}
                className="flex-1 px-4 py-2 border border-outline-light dark:border-outline-dark rounded-lg text-on-surface-light dark:text-on-surface-dark hover:bg-surface-light/50 dark:hover:bg-surface-dark/50"
              >
                Cancelar
              </button>
              <button
                onClick={createUser}
                disabled={!userForm.email || !userForm.password}
                className="flex-1 px-4 py-2 bg-primary hover:bg-primary/90 disabled:bg-primary/50 text-white rounded-lg"
              >
                Crear Usuario
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;