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

interface BotConfig {
  system_prompt: string;
  style_overrides: StyleOverrides;
  nlu_params: NLUParams;
  nlg_params: NLGParams;
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
  const { user, client, access_token } = useAuth();
  const { showToast } = useToast();
  const apiClient = ApiClient.getInstance();
  
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
      max_tokens_nlg: 300
    }
  });

  const [loading, setLoading] = useState(false);
  const [tenantId, setTenantId] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'config' | 'chat'>('config');

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
          nlg_params: data.nlg_params
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
        const error = await response.json();
        throw new Error(error.detail || `Error ${response.status}`);
      }
    } catch (error: any) {
      console.error('Error saving configuration:', error);
      showToast(`Error al guardar: ${error.message}`, 'error');
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
          max_tokens_nlg: 300
        }
      });
      showToast('Configuración reseteada a valores por defecto', 'success');
    }
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
          <div className="space-y-6">
            {/* Prompt del Sistema */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">
                📝 Prompt del Sistema
              </label>
              <textarea
                value={config.system_prompt}
                onChange={(e) => setConfig({ ...config, system_prompt: e.target.value })}
                className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark"
                rows={4}
                placeholder={`Eres un asistente especializado para ${client?.name || 'nuestra empresa'}...`}
              />
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
                    <option value="profesional">Profesional</option>
                    <option value="casual">Casual</option>
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
                    max="1000"
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