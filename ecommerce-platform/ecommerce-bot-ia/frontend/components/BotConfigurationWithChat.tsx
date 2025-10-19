import React, { useState, useEffect } from 'react';
import { useAuth, ApiClient } from '../auth/AuthContext';
import { useToast } from './Toast';
import ChatInterface from './ChatInterface';

interface StyleOverrides {
  tono: string;
  usar_emojis: boolean;
  limite_respuesta_caracteres: number;
  incluir_contexto_empresa: boolean;
}

interface NLUParams {
  modelo: string;
  temperature_nlu: number;
  max_tokens_nlu: number;
}

interface NLGParams {
  modelo: string;
  temperature_nlg: number;
  max_tokens_nlg: number;
}

interface DatabaseQuery {
  name: string;
  description?: string;
  sql_template: string;
  parameters: string[];
  max_results: number;
  cache_ttl_seconds: number;
  is_active: boolean;
}

interface DatabaseQueries {
  products_query?: DatabaseQuery;
  campaigns_query?: DatabaseQuery;
  discounts_query?: DatabaseQuery;
  custom_queries?: DatabaseQuery[];
}

interface BotConfig {
  system_prompt: string;
  style_overrides: StyleOverrides;
  nlu_params: NLUParams;
  nlg_params: NLGParams;
  database_queries?: DatabaseQueries;
}

interface BotConfigResponse extends BotConfig {
  id: string;
  tenant_id: string;
  version: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const BotConfigurationWithChat: React.FC = () => {
  const authContext = useAuth();
  const { user, client, access_token } = authContext;
  const { showToast } = useToast();
  const apiClient = ApiClient.getInstance();
  
  // Configurar el contexto de autenticación en el ApiClient
  useEffect(() => {
    apiClient.setAuthContext(authContext);
  }, [authContext, apiClient]);
  
  const [config, setConfig] = useState<BotConfig>({
    system_prompt: '',
    style_overrides: {
      tono: 'amigable',
      usar_emojis: true,
      limite_respuesta_caracteres: 300,
      incluir_contexto_empresa: true
    },
    nlu_params: {
      modelo: 'gpt-4o-mini',
      temperature_nlu: 0.3,
      max_tokens_nlu: 150
    },
    nlg_params: {
      modelo: 'gpt-4o-mini', 
      temperature_nlg: 0.7,
      max_tokens_nlg: 200
    },
    database_queries: {
      products_query: {
        name: "productos_catalogo",
        description: "Consulta productos disponibles por categoría",
        sql_template: "SELECT name, description, price, sale_price, stock, category FROM products WHERE client_id = $client_id AND status = 'active' AND category ILIKE $category ORDER BY name LIMIT $limit",
        parameters: ["client_id", "category", "limit"],
        max_results: 20,
        cache_ttl_seconds: 300,
        is_active: true
      },
      campaigns_query: {
        name: "campanas_activas",
        description: "Consulta campañas publicitarias activas",
        sql_template: "SELECT name, start_date, end_date, budget, status FROM campaigns WHERE client_id = $client_id AND status = 'active' AND end_date > NOW() ORDER BY start_date LIMIT $limit",
        parameters: ["client_id", "limit"],
        max_results: 10,
        cache_ttl_seconds: 300,
        is_active: true
      },
      discounts_query: {
        name: "descuentos_vigentes",
        description: "Consulta descuentos y promociones vigentes",
        sql_template: "SELECT name, type, value, target, category FROM discounts WHERE client_id = $client_id AND is_active = true ORDER BY value DESC LIMIT $limit",
        parameters: ["client_id", "limit"],
        max_results: 15,
        cache_ttl_seconds: 300,
        is_active: true
      },
      custom_queries: []
    }
  });

  const [loading, setLoading] = useState(false);
  const [tenantId, setTenantId] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'config' | 'database' | 'chat'>('config');
  
  // Estados para pruebas de queries
  const [testingQuery, setTestingQuery] = useState<string>('');
  const [testResults, setTestResults] = useState<any>(null);
  const [testLoading, setTestLoading] = useState(false);
  const [testParameters, setTestParameters] = useState<Record<string, string>>({});
  
  // Estados para drag & drop de queries
  const [draggedQuery, setDraggedQuery] = useState<string>('');

  // Obtener tenant ID dinámicamente
  useEffect(() => {
    const hostname = window.location.hostname;
    if (hostname.includes('acme')) {
      setTenantId('acme-cannabis-2024');
    } else if (hostname.includes('bravo')) {
      setTenantId('bravo-gaming-2024');
    } else {
      setTenantId('acme-cannabis-2024'); // Default
    }
  }, []);

  const loadConfiguration = async () => {
    if (!tenantId) return;
    
    try {
      setLoading(true);
      const response = await apiClient.get(`/api/tenants/${tenantId}/prompt`);
      if (response.ok) {
        const data: BotConfigResponse = await response.json();
        setConfig({
          system_prompt: data.system_prompt,
          style_overrides: data.style_overrides,
          nlu_params: data.nlu_params,
          nlg_params: data.nlg_params,
          database_queries: data.database_queries || config.database_queries
        });
        showToast('Configuración cargada exitosamente', 'success');
      } else if (response.status === 404) {
        showToast('No hay configuración guardada, usando valores por defecto', 'info');
      }
    } catch (error) {
      console.error('Error loading configuration:', error);
      showToast('Error al cargar la configuración', 'error');
    } finally {
      setLoading(false);
    }
  };

  const saveConfiguration = async () => {
    if (!tenantId) return;
    
    try {
      if (config.system_prompt.length < 50) {
        showToast('El prompt del sistema debe tener al menos 50 caracteres', 'error');
        return;
      }

      setLoading(true);
      
      // Intentar actualizar primero
      let response = await apiClient.post(`/api/tenants/${tenantId}/prompt`, config);

      // Si no existe, crear nuevo
      if (response.status === 404) {
        response = await apiClient.post(`/api/tenants/${tenantId}/prompt`, config);
      }

      if (response.ok) {
        const result: BotConfigResponse = await response.json();
        showToast(`Configuración guardada exitosamente (Versión ${result.version})`, 'success');
      } else {
        let errorMessage = `Error ${response.status}`;
        try {
          const error = await response.json();
          errorMessage = error.detail || error.message || errorMessage;
          console.error('Server error details:', error);
        } catch (parseError) {
          console.error('Could not parse error response:', parseError);
        }
        throw new Error(errorMessage);
      }
    } catch (error: any) {
      console.error('Error saving configuration:', error);
      
      // Mostrar error más específico
      let displayMessage = error.message;
      if (error.message.includes('Not authenticated')) {
        displayMessage = 'Error de autenticación. Por favor, inicia sesión nuevamente.';
      } else if (error.message.includes('422')) {
        displayMessage = 'Error de validación en los datos enviados.';
      } else if (error.message.includes('500')) {
        displayMessage = 'Error interno del servidor.';
      }
      
      showToast(`Error al guardar: ${displayMessage}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleChatMessage = async (message: string, history: any[]): Promise<string> => {
    if (!tenantId) {
      throw new Error('Tenant ID no disponible');
    }
    
    try {
      // DETECTAR SUBDOMINIO Y USAR ENDPOINT MULTI-TENANT CORRECTO
      const hostname = window.location.hostname;
      // Formatear historial para el bot
      const formattedHistory = history.map(msg => ({
        role: msg.type === 'user' ? 'user' : 'bot',
        content: msg.content,
        timestamp: msg.timestamp
      }));

      const requestBody = {
        telefono: '+56950915617',
        mensaje: message,
        historial: formattedHistory
      };
      
      console.log(`🌐 Hostname: ${hostname}, Testing message: ${message}`);
      console.log('📤 Request body:', requestBody);
      
      // Usar endpoint directo del bot con formato JSON
      const response = await fetch('/bot-proxy/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });
      
      console.log('📥 Response status:', response.status, response.statusText);

      if (response.ok) {
        const result = await response.json();
        console.log('🤖 Bot response:', result);
        return result.respuesta || 'Sin respuesta del bot';
      } else {
        const errorText = await response.text();
        console.error('❌ Response error:', response.status, response.statusText, errorText);
        throw new Error(`Error ${response.status}: ${errorText || response.statusText}`);
      }
    } catch (error: any) {
      console.error('Error testing configuration:', error);
      throw new Error(`Error en la prueba: ${error.message}`);
    }
  };

  const resetConfiguration = () => {
    if (confirm('¿Estás seguro de resetear a los valores por defecto?')) {
      setConfig({
        system_prompt: `Eres un asistente especializado para ${client?.name || 'nuestra empresa'}. Ayudas a los clientes con información sobre productos, disponibilidad y precios de manera amigable y profesional.`,
        style_overrides: {
          tono: 'amigable',
          usar_emojis: true,
          limite_respuesta_caracteres: 300,
          incluir_contexto_empresa: true
        },
        nlu_params: {
          modelo: 'gpt-4o-mini',
          temperature_nlu: 0.3,
          max_tokens_nlu: 150
        },
        nlg_params: {
          modelo: 'gpt-4o-mini',
          temperature_nlg: 0.7,
          max_tokens_nlg: 200
        },
        database_queries: {
          products_query: {
            name: "productos_catalogo",
            description: "Consulta productos disponibles por categoría",
            sql_template: "SELECT name, description, price, sale_price, stock, category FROM products WHERE client_id = $client_id AND status = 'active' AND category ILIKE $category ORDER BY name LIMIT $limit",
            parameters: ["client_id", "category", "limit"],
            max_results: 20,
            cache_ttl_seconds: 300,
            is_active: true
          },
          campaigns_query: {
            name: "campanas_activas",
            description: "Consulta campañas publicitarias activas",
            sql_template: "SELECT name, start_date, end_date, budget, status FROM campaigns WHERE client_id = $client_id AND status = 'active' AND end_date > NOW() ORDER BY start_date LIMIT $limit",
            parameters: ["client_id", "limit"],
            max_results: 10,
            cache_ttl_seconds: 300,
            is_active: true
          },
          discounts_query: {
            name: "descuentos_vigentes",
            description: "Consulta descuentos y promociones vigentes",
            sql_template: "SELECT name, type, value, target, category FROM discounts WHERE client_id = $client_id AND is_active = true ORDER BY value DESC LIMIT $limit",
            parameters: ["client_id", "limit"],
            max_results: 15,
            cache_ttl_seconds: 300,
            is_active: true
          },
          custom_queries: []
        }
      });
      showToast('Configuración reseteada a valores por defecto', 'success');
    }
  };

  const testQuery = async (queryType: string) => {
    if (!tenantId) {
      showToast('No hay tenant ID configurado', 'error');
      return;
    }

    setTestLoading(true);
    setTestingQuery(queryType);
    
    try {
      const response = await apiClient.post('/debug/test-db-queries', {
        tenant_id: tenantId,
        query_name: queryType,
        parameters: testParameters
      });

      if (response.ok) {
        const data = await response.json();
        setTestResults(data);
        showToast(`Query ${queryType} ejecutada exitosamente`, 'success');
      } else {
        const errorData = await response.json();
        setTestResults({
          status: 'error',
          message: errorData.detail || 'Error ejecutando query'
        });
        showToast('Error ejecutando query', 'error');
      }
    } catch (error) {
      setTestResults({
        status: 'error',
        message: 'Error de conexión'
      });
      showToast('Error de conexión al servidor', 'error');
    } finally {
      setTestLoading(false);
      setTestingQuery('');
    }
  };

  // Función para generar plantillas de prompts más naturales
  const generateQueryInstruction = (queryType: string) => {
    const clientName = client?.name || 'nuestro cliente';
    
    const templates = {
      productos: `

Eres un asistente especializado de ${clientName}. Con la query de productos configurada vas a recorrer todos los productos disponibles y dar una respuesta según lo que el cliente quiera consultar.

Cuando el cliente pregunte sobre productos, utiliza la información actualizada de la base de datos para:
- Mostrar productos disponibles con precios y stock real
- Buscar por categorías específicas que el cliente solicite
- Recomendar productos relacionados o alternativos
- Informar sobre disponibilidad y características

Siempre proporciona información precisa basada en los datos actuales del inventario.`,

      campanas: `

Eres un asistente especializado de ${clientName}. Con la query de campañas configurada vas a consultar todas las promociones activas y dar una respuesta según lo que el cliente necesite saber.

Cuando el cliente pregunte sobre promociones, utiliza la información actualizada para:
- Informar sobre campañas vigentes y sus beneficios
- Explicar fechas de inicio y fin de las promociones
- Detallar condiciones y términos de cada campaña
- Sugerir las mejores ofertas disponibles para el cliente

Mantén al cliente informado sobre todas las oportunidades de ahorro disponibles.`,

      descuentos: `

Eres un asistente especializado de ${clientName}. Con la query de descuentos configurada vas a revisar todas las ofertas vigentes y dar una respuesta según lo que el cliente busque.

Cuando el cliente pregunte sobre descuentos, utiliza la información actualizada para:
- Mostrar descuentos disponibles por categoría o producto
- Explicar porcentajes y montos de descuento aplicables
- Informar sobre condiciones y restricciones de cada oferta
- Ayudar a combinar descuentos para maximizar el ahorro

Asegúrate de ofrecer las mejores opciones de precio para cada consulta del cliente.`
    };
    
    return templates[queryType as keyof typeof templates] || '';
  };

  // Función para insertar instrucción de query en el prompt
  const insertQueryIntoPrompt = (queryType: string) => {
    const instruction = generateQueryInstruction(queryType);
    const currentPrompt = config.system_prompt;
    
    // Insertar al final del prompt actual
    setConfig({
      ...config,
      system_prompt: currentPrompt + instruction
    });
    
    showToast(`Instrucciones de ${queryType} agregadas al prompt`, 'success');
  };

  // Funciones para drag & drop
  const handleDragStart = (e: React.DragEvent, queryType: string) => {
    setDraggedQuery(queryType);
    e.dataTransfer.setData('text/plain', queryType);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const queryType = e.dataTransfer.getData('text/plain');
    if (queryType) {
      insertQueryIntoPrompt(queryType);
    }
    setDraggedQuery('');
  };

  useEffect(() => {
    if (tenantId) {
      loadConfiguration();
    }
  }, [tenantId]);

  if (loading && !config.system_prompt) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-surface-light dark:bg-surface-dark rounded-lg p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-primary p-2 rounded-lg">
            <span className="text-white text-xl">🤖</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface-light dark:text-on-surface-dark">
              Configuración del Bot
            </h1>
            <p className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
              Cliente: {client?.name || tenantId}
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setActiveTab('config')}
            className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'config'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
            }`}
          >
            ⚙️ Configuración
          </button>
          <button
            onClick={() => setActiveTab('database')}
            className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'database'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
            }`}
          >
            🗃️ Base de Datos
          </button>
          <button
            onClick={() => setActiveTab('chat')}
            className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'chat'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
            }`}
          >
            💬 Prueba Interactiva
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'config' && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Menú Vertical de Queries */}
            <div className="lg:col-span-1">
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 sticky top-4">
                <h3 className="text-lg font-semibold mb-4 text-on-surface-light dark:text-on-surface-dark">
                  🗃️ Queries Disponibles
                </h3>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-4">
                  Arrastra al prompt para integrar
                </p>
                
                <div className="space-y-3">
                  {/* Query de Productos */}
                  {config.database_queries?.products_query?.is_active && (
                    <div
                      draggable
                      onDragStart={(e) => handleDragStart(e, 'productos')}
                      className="cursor-move p-3 bg-white dark:bg-gray-700 border border-green-300 dark:border-green-600 rounded-lg hover:shadow-lg transition-all hover:border-green-400 group"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-lg">📦</span>
                        <span className="font-medium text-green-700 dark:text-green-300 text-sm">Productos</span>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {config.database_queries.products_query.description}
                      </p>
                      <div className="text-xs text-green-600 dark:text-green-400 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        🖱️ Arrastra al prompt
                      </div>
                    </div>
                  )}
                  
                  {/* Query de Campañas */}
                  {config.database_queries?.campaigns_query?.is_active && (
                    <div
                      draggable
                      onDragStart={(e) => handleDragStart(e, 'campanas')}
                      className="cursor-move p-3 bg-white dark:bg-gray-700 border border-purple-300 dark:border-purple-600 rounded-lg hover:shadow-lg transition-all hover:border-purple-400 group"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-lg">📢</span>
                        <span className="font-medium text-purple-700 dark:text-purple-300 text-sm">Campañas</span>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {config.database_queries.campaigns_query.description}
                      </p>
                      <div className="text-xs text-purple-600 dark:text-purple-400 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        🖱️ Arrastra al prompt
                      </div>
                    </div>
                  )}
                  
                  {/* Query de Descuentos */}
                  {config.database_queries?.discounts_query?.is_active && (
                    <div
                      draggable
                      onDragStart={(e) => handleDragStart(e, 'descuentos')}
                      className="cursor-move p-3 bg-white dark:bg-gray-700 border border-orange-300 dark:border-orange-600 rounded-lg hover:shadow-lg transition-all hover:border-orange-400 group"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-lg">💰</span>
                        <span className="font-medium text-orange-700 dark:text-orange-300 text-sm">Descuentos</span>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {config.database_queries.discounts_query.description}
                      </p>
                      <div className="text-xs text-orange-600 dark:text-orange-400 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        🖱️ Arrastra al prompt
                      </div>
                    </div>
                  )}
                  
                  {/* Mensaje si no hay queries activas */}
                  {!config.database_queries?.products_query?.is_active && 
                   !config.database_queries?.campaigns_query?.is_active && 
                   !config.database_queries?.discounts_query?.is_active && (
                    <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                      <p className="text-xs text-yellow-700 dark:text-yellow-300">
                        ⚠️ Ve a la pestaña "🗃️ Base de Datos" para activar queries
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Área Principal de Configuración */}
            <div className="lg:col-span-3 space-y-6">
              {/* Prompt del Sistema con Drop Zone */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                  📝 Prompt del Sistema
                  <span className="ml-2 text-xs text-blue-600 dark:text-blue-400">
                    💡 Arrastra queries desde el menú lateral
                  </span>
                </label>
                <div 
                  className={`relative ${
                    draggedQuery ? 'ring-2 ring-blue-400 ring-opacity-50 bg-blue-50 dark:bg-blue-900/20' : ''
                  }`}
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                >
                  <textarea
                    value={config.system_prompt}
                    onChange={(e) => setConfig({ ...config, system_prompt: e.target.value })}
                    className={`w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark transition-all ${
                      draggedQuery ? 'border-blue-400 border-2' : ''
                    }`}
                    rows={8}
                    placeholder={`Eres un asistente especializado para ${client?.name || 'nuestra empresa'}...`}
                  />
                  {draggedQuery && (
                    <div className="absolute inset-0 flex items-center justify-center bg-blue-100 dark:bg-blue-900/30 bg-opacity-90 rounded-lg border-2 border-dashed border-blue-400 pointer-events-none">
                      <div className="text-center text-blue-700 dark:text-blue-300">
                        <div className="text-3xl mb-2">📥</div>
                        <div className="font-medium text-lg">Suelta aquí la query de {draggedQuery}</div>
                        <div className="text-sm opacity-75">Se generará automáticamente el prompt</div>
                      </div>
                    </div>
                  )}
                </div>
                <p className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">
                  Caracteres: {config.system_prompt.length} (mínimo 50)
                </p>
              </div>

            {/* Grid de configuraciones */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Estilo de Conversación */}
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 space-y-4">
                <h3 className="text-lg font-semibold text-on-surface-light dark:text-on-surface-dark">
                  🎨 Estilo de Conversación
                </h3>
                
                <div>
                  <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                    Tono:
                  </label>
                  <select
                    value={config.style_overrides.tono}
                    onChange={(e) => setConfig({
                      ...config,
                      style_overrides: { ...config.style_overrides, tono: e.target.value }
                    })}
                    className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark"
                  >
                    <option value="amigable">Amigable</option>
                    <option value="super_amigable">Super Amigable</option>
                    <option value="profesional">Profesional</option>
                    <option value="casual">Casual</option>
                    <option value="formal">Formal</option>
                    <option value="experto">Experto</option>
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="emojis"
                    checked={config.style_overrides.usar_emojis}
                    onChange={(e) => setConfig({
                      ...config,
                      style_overrides: { ...config.style_overrides, usar_emojis: e.target.checked }
                    })}
                    className="rounded"
                  />
                  <label htmlFor="emojis" className="text-sm text-on-surface-light dark:text-on-surface-dark">
                    Usar emojis
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                    Límite de caracteres: {config.style_overrides.limite_respuesta_caracteres}
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="1000"
                    step="50"
                    value={config.style_overrides.limite_respuesta_caracteres}
                    onChange={(e) => setConfig({
                      ...config,
                      style_overrides: { ...config.style_overrides, limite_respuesta_caracteres: parseInt(e.target.value) }
                    })}
                    className="w-full"
                  />
                </div>
              </div>

              {/* Parámetros de IA */}
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 space-y-4">
                <h3 className="text-lg font-semibold text-on-surface-light dark:text-on-surface-dark">
                  🧠 Parámetros de IA
                </h3>
                
                <div>
                  <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                    Modelo:
                  </label>
                  <select
                    value={config.nlg_params.modelo}
                    onChange={(e) => setConfig({
                      ...config,
                      nlg_params: { ...config.nlg_params, modelo: e.target.value },
                      nlu_params: { ...config.nlu_params, modelo: e.target.value }
                    })}
                    className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark"
                  >
                    <option value="gpt-4o-mini">GPT-4O Mini</option>
                    <option value="gpt-4o">GPT-4O</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                    Temperature (creatividad): {config.nlg_params.temperature_nlg}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={config.nlg_params.temperature_nlg}
                    onChange={(e) => setConfig({
                      ...config,
                      nlg_params: { ...config.nlg_params, temperature_nlg: parseFloat(e.target.value) }
                    })}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                    Máximo tokens:
                  </label>
                  <input
                    type="number"
                    min="100"
                    max="400"
                    value={config.nlg_params.max_tokens_nlg}
                    onChange={(e) => setConfig({
                      ...config,
                      nlg_params: { ...config.nlg_params, max_tokens_nlg: parseInt(e.target.value) }
                    })}
                    className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark"
                  />
                </div>
              </div>
            </div>

              {/* Botones de acción */}
              <div className="flex flex-wrap gap-4">
                <button
                  onClick={saveConfiguration}
                  disabled={loading}
                  className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50"
                >
                  {loading ? '⏳' : '💾'} Guardar Configuración
                </button>
                <button
                  onClick={loadConfiguration}
                  disabled={loading}
                  className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
                >
                  🔄 Recargar
                </button>
                <button
                  onClick={resetConfiguration}
                  className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  🔄 Resetear
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'database' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-4 text-on-surface-light dark:text-on-surface-dark">
                🗃️ Configuración de Consultas a Base de Datos
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                Configure las queries SQL que el bot puede usar para consultar información en tiempo real sobre productos, campañas y descuentos.
              </p>

              {/* Query de Productos */}
              <div className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <input
                    type="checkbox"
                    checked={config.database_queries?.products_query?.is_active || false}
                    onChange={(e) => setConfig({
                      ...config,
                      database_queries: {
                        ...config.database_queries!,
                        products_query: {
                          ...config.database_queries!.products_query!,
                          is_active: e.target.checked
                        }
                      }
                    })}
                    className="w-4 h-4"
                  />
                  <h4 className="font-medium text-on-surface-light dark:text-on-surface-dark">
                    📦 Consulta de Productos
                  </h4>
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                      Descripción:
                    </label>
                    <input
                      type="text"
                      value={config.database_queries?.products_query?.description || ''}
                      onChange={(e) => setConfig({
                        ...config,
                        database_queries: {
                          ...config.database_queries!,
                          products_query: {
                            ...config.database_queries!.products_query!,
                            description: e.target.value
                          }
                        }
                      })}
                      className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark"
                      placeholder="Descripción de la consulta"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                      Máximo resultados:
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="100"
                      value={config.database_queries?.products_query?.max_results || 20}
                      onChange={(e) => setConfig({
                        ...config,
                        database_queries: {
                          ...config.database_queries!,
                          products_query: {
                            ...config.database_queries!.products_query!,
                            max_results: parseInt(e.target.value)
                          }
                        }
                      })}
                      className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark"
                    />
                  </div>
                </div>
                <div className="mt-4">
                  <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                    SQL Template:
                  </label>
                  <textarea
                    value={config.database_queries?.products_query?.sql_template || ''}
                    onChange={(e) => setConfig({
                      ...config,
                      database_queries: {
                        ...config.database_queries!,
                        products_query: {
                          ...config.database_queries!.products_query!,
                          sql_template: e.target.value
                        }
                      }
                    })}
                    className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark font-mono text-sm"
                    rows={3}
                    placeholder="SELECT ... FROM products WHERE ..."
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Use placeholders como $client_id, $category, $limit
                  </p>
                </div>
              </div>

              {/* Query de Campañas */}
              <div className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <input
                    type="checkbox"
                    checked={config.database_queries?.campaigns_query?.is_active || false}
                    onChange={(e) => setConfig({
                      ...config,
                      database_queries: {
                        ...config.database_queries!,
                        campaigns_query: {
                          ...config.database_queries!.campaigns_query!,
                          is_active: e.target.checked
                        }
                      }
                    })}
                    className="w-4 h-4"
                  />
                  <h4 className="font-medium text-on-surface-light dark:text-on-surface-dark">
                    📢 Consulta de Campañas
                  </h4>
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                      Descripción:
                    </label>
                    <input
                      type="text"
                      value={config.database_queries?.campaigns_query?.description || ''}
                      onChange={(e) => setConfig({
                        ...config,
                        database_queries: {
                          ...config.database_queries!,
                          campaigns_query: {
                            ...config.database_queries!.campaigns_query!,
                            description: e.target.value
                          }
                        }
                      })}
                      className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark"
                      placeholder="Descripción de la consulta"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                      Máximo resultados:
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="100"
                      value={config.database_queries?.campaigns_query?.max_results || 10}
                      onChange={(e) => setConfig({
                        ...config,
                        database_queries: {
                          ...config.database_queries!,
                          campaigns_query: {
                            ...config.database_queries!.campaigns_query!,
                            max_results: parseInt(e.target.value)
                          }
                        }
                      })}
                      className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark"
                    />
                  </div>
                </div>
                <div className="mt-4">
                  <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                    SQL Template:
                  </label>
                  <textarea
                    value={config.database_queries?.campaigns_query?.sql_template || ''}
                    onChange={(e) => setConfig({
                      ...config,
                      database_queries: {
                        ...config.database_queries!,
                        campaigns_query: {
                          ...config.database_queries!.campaigns_query!,
                          sql_template: e.target.value
                        }
                      }
                    })}
                    className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark font-mono text-sm"
                    rows={3}
                    placeholder="SELECT ... FROM campaigns WHERE ..."
                  />
                </div>
              </div>

              {/* Query de Descuentos */}
              <div className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <input
                    type="checkbox"
                    checked={config.database_queries?.discounts_query?.is_active || false}
                    onChange={(e) => setConfig({
                      ...config,
                      database_queries: {
                        ...config.database_queries!,
                        discounts_query: {
                          ...config.database_queries!.discounts_query!,
                          is_active: e.target.checked
                        }
                      }
                    })}
                    className="w-4 h-4"
                  />
                  <h4 className="font-medium text-on-surface-light dark:text-on-surface-dark">
                    💰 Consulta de Descuentos
                  </h4>
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                      Descripción:
                    </label>
                    <input
                      type="text"
                      value={config.database_queries?.discounts_query?.description || ''}
                      onChange={(e) => setConfig({
                        ...config,
                        database_queries: {
                          ...config.database_queries!,
                          discounts_query: {
                            ...config.database_queries!.discounts_query!,
                            description: e.target.value
                          }
                        }
                      })}
                      className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark"
                      placeholder="Descripción de la consulta"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                      Máximo resultados:
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="100"
                      value={config.database_queries?.discounts_query?.max_results || 15}
                      onChange={(e) => setConfig({
                        ...config,
                        database_queries: {
                          ...config.database_queries!,
                          discounts_query: {
                            ...config.database_queries!.discounts_query!,
                            max_results: parseInt(e.target.value)
                          }
                        }
                      })}
                      className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark"
                    />
                  </div>
                </div>
                <div className="mt-4">
                  <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                    SQL Template:
                  </label>
                  <textarea
                    value={config.database_queries?.discounts_query?.sql_template || ''}
                    onChange={(e) => setConfig({
                      ...config,
                      database_queries: {
                        ...config.database_queries!,
                        discounts_query: {
                          ...config.database_queries!.discounts_query!,
                          sql_template: e.target.value
                        }
                      }
                    })}
                    className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark font-mono text-sm"
                    rows={3}
                    placeholder="SELECT ... FROM discounts WHERE ..."
                  />
                </div>
              </div>

              {/* Sección de Integración Drag & Drop */}
              <div className="mt-8 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <h4 className="text-lg font-semibold mb-4 text-green-800 dark:text-green-200">
                  🔗 Integrar Queries con Prompts
                </h4>
                <p className="text-sm text-green-600 dark:text-green-300 mb-4">
                  Arrastra las queries activas hacia el prompt del sistema en la pestaña "⚙️ Configuración" para integrar automáticamente las capacidades de base de datos.
                </p>
                
                {/* Bloques de queries arrastrables */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  {config.database_queries?.products_query?.is_active && (
                    <div
                      draggable
                      onDragStart={(e) => handleDragStart(e, 'productos')}
                      className="cursor-move p-3 bg-white dark:bg-gray-800 border border-green-300 dark:border-green-700 rounded-lg hover:shadow-lg transition-all hover:border-green-400 group"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-lg">📦</span>
                        <span className="font-medium text-green-700 dark:text-green-300">Productos</span>
                        <span className="text-xs text-gray-500 group-hover:text-green-600">🤏 Arrastra</span>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {config.database_queries.products_query.description}
                      </p>
                    </div>
                  )}
                  
                  {config.database_queries?.campaigns_query?.is_active && (
                    <div
                      draggable
                      onDragStart={(e) => handleDragStart(e, 'campanas')}
                      className="cursor-move p-3 bg-white dark:bg-gray-800 border border-green-300 dark:border-green-700 rounded-lg hover:shadow-lg transition-all hover:border-green-400 group"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-lg">📢</span>
                        <span className="font-medium text-green-700 dark:text-green-300">Campañas</span>
                        <span className="text-xs text-gray-500 group-hover:text-green-600">🤏 Arrastra</span>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {config.database_queries.campaigns_query.description}
                      </p>
                    </div>
                  )}
                  
                  {config.database_queries?.discounts_query?.is_active && (
                    <div
                      draggable
                      onDragStart={(e) => handleDragStart(e, 'descuentos')}
                      className="cursor-move p-3 bg-white dark:bg-gray-800 border border-green-300 dark:border-green-700 rounded-lg hover:shadow-lg transition-all hover:border-green-400 group"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-lg">💰</span>
                        <span className="font-medium text-green-700 dark:text-green-300">Descuentos</span>
                        <span className="text-xs text-gray-500 group-hover:text-green-600">🤏 Arrastra</span>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {config.database_queries.discounts_query.description}
                      </p>
                    </div>
                  )}
                </div>
                
                {/* Instrucciones de uso */}
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border border-green-200 dark:border-green-700">
                  <h5 className="font-medium text-green-800 dark:text-green-200 mb-2">📋 Cómo usar:</h5>
                  <ol className="text-sm text-green-700 dark:text-green-300 space-y-1">
                    <li>1️⃣ Activa las queries que quieres usar marcando los checkboxes</li>
                    <li>2️⃣ Arrastra los bloques de queries hacia el campo "Prompt del Sistema" en la pestaña Configuración</li>
                    <li>3️⃣ Las instrucciones se insertarán automáticamente en tu prompt</li>
                    <li>4️⃣ Guarda la configuración para aplicar los cambios</li>
                  </ol>
                </div>
              </div>
              
              {/* Sección de Pruebas */}
              <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <h4 className="text-lg font-semibold mb-4 text-blue-800 dark:text-blue-200">
                  🧪 Probar Queries en Tiempo Real
                </h4>
                <p className="text-sm text-blue-600 dark:text-blue-300 mb-4">
                  Ejecuta las queries configuradas para ver los resultados en tiempo real desde tu base de datos.
                </p>

                {/* Parámetros de prueba */}
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                    Parámetros de prueba (opcional):
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <input
                        type="text"
                        placeholder="category (ej: cannabis, %)"
                        value={testParameters.category || ''}
                        onChange={(e) => setTestParameters({
                          ...testParameters,
                          category: e.target.value
                        })}
                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark text-sm"
                      />
                    </div>
                    <div>
                      <input
                        type="number"
                        placeholder="limit (ej: 5)"
                        value={testParameters.limit || ''}
                        onChange={(e) => setTestParameters({
                          ...testParameters,
                          limit: e.target.value
                        })}
                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark text-sm"
                      />
                    </div>
                    <div>
                      <input
                        type="text"
                        placeholder="Otro parámetro"
                        value={testParameters.other || ''}
                        onChange={(e) => setTestParameters({
                          ...testParameters,
                          other: e.target.value
                        })}
                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark text-sm"
                      />
                    </div>
                  </div>
                </div>

                {/* Botones de prueba */}
                <div className="flex flex-wrap gap-3 mb-4">
                  <button
                    onClick={() => testQuery('productos')}
                    disabled={testLoading}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                  >
                    {testLoading && testingQuery === 'productos' ? (
                      <>⏳ Probando...</>
                    ) : (
                      <>📦 Probar Productos</>
                    )}
                  </button>
                  <button
                    onClick={() => testQuery('campanas')}
                    disabled={testLoading}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
                  >
                    {testLoading && testingQuery === 'campanas' ? (
                      <>⏳ Probando...</>
                    ) : (
                      <>📢 Probar Campañas</>
                    )}
                  </button>
                  <button
                    onClick={() => testQuery('descuentos')}
                    disabled={testLoading}
                    className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 flex items-center gap-2"
                  >
                    {testLoading && testingQuery === 'descuentos' ? (
                      <>⏳ Probando...</>
                    ) : (
                      <>💰 Probar Descuentos</>
                    )}
                  </button>
                  <button
                    onClick={() => setTestResults(null)}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    🗑️ Limpiar
                  </button>
                </div>

                {/* Resultados de prueba */}
                {testResults && (
                  <div className="mt-4 p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <div className="flex items-center gap-2 mb-3">
                      <span className={`text-sm font-medium ${
                        testResults.status === 'success' 
                          ? 'text-green-600 dark:text-green-400' 
                          : 'text-red-600 dark:text-red-400'
                      }`}>
                        {testResults.status === 'success' ? '✅ Éxito' : '❌ Error'}
                      </span>
                      {testResults.status === 'success' && (
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          ({testResults.results_count} resultados)
                        </span>
                      )}
                    </div>

                    {testResults.status === 'success' ? (
                      <div>
                        <div className="mb-3">
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            <strong>Tenant:</strong> {testResults.tenant_id} | 
                            <strong> Query:</strong> {testResults.query_name} | 
                            <strong> Parámetros:</strong> {JSON.stringify(testResults.parameters)}
                          </p>
                        </div>
                        
                        {testResults.results && testResults.results.length > 0 ? (
                          <div className="space-y-2">
                            <h5 className="text-sm font-medium text-on-surface-light dark:text-on-surface-dark">
                              Resultados (mostrando primeros 3):
                            </h5>
                            <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded-lg overflow-x-auto">
                              <pre className="text-xs text-gray-700 dark:text-gray-300">
                                {JSON.stringify(testResults.results, null, 2)}
                              </pre>
                            </div>
                          </div>
                        ) : (
                          <div className="text-sm text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-900 p-3 rounded-lg">
                            No se encontraron resultados para esta consulta.
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
                        <strong>Error:</strong> {testResults.message}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Botones de acción */}
              <div className="flex flex-wrap gap-4 mt-6">
                <button
                  onClick={saveConfiguration}
                  disabled={loading}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {loading ? '⏳ Guardando...' : '💾 Guardar Configuración'}
                </button>
                <button
                  onClick={loadConfiguration}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  🔄 Recargar
                </button>
                <button
                  onClick={resetConfiguration}
                  className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  🔄 Resetear
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="space-y-4">
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  <span className="text-blue-500">ℹ️</span>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                    Prueba Interactiva del Bot
                  </h3>
                  <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                    Esta interfaz te permite probar las respuestas del bot en tiempo real con datos reales de la base de datos. 
                    Los cambios de configuración se aplican automáticamente en las pruebas.
                  </p>
                </div>
              </div>
            </div>
            
            <ChatInterface 
              onTestMessage={handleChatMessage}
              className="shadow-lg border-2 border-gray-200 dark:border-gray-700"
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default BotConfigurationWithChat;