import React, { useState, useEffect } from 'react';
import { useAuth, ApiClient } from '../auth/AuthContext';
import { useToast } from './Toast';

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

const BotConfiguration: React.FC = () => {
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
  const [testMessage, setTestMessage] = useState('');
  const [testResult, setTestResult] = useState<string | null>(null);
  const [testing, setTesting] = useState(false);
  const [tenantId, setTenantId] = useState<string>('');

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

  const testConfiguration = async () => {
    if (!tenantId) return;
    
    try {
      if (!testMessage.trim()) {
        showToast('Ingresa un mensaje de prueba', 'error');
        return;
      }

      setTesting(true);
      setTestResult(null);

      // DETECTAR SUBDOMINIO Y USAR ENDPOINT MULTI-TENANT CORRECTO
      const hostname = window.location.hostname;
      const subdomain = hostname.split('.')[0];
      
      console.log(`🌐 Hostname: ${hostname}, Subdominio: ${subdomain}`);
      
      // Usar endpoint multi-tenant específico para cada subdominio
      const response = await fetch('/bot-proxy/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Host': hostname, // Pasar host header para identificación de tenant
        },
        body: new URLSearchParams({
          From: 'whatsapp:+56950915617',
          Body: testMessage
        })
      });

      if (response.ok) {
        const result = await response.json();
        setTestResult(result.respuesta); // Nginx proxy devuelve respuesta directa del bot
        showToast('Prueba completada exitosamente (datos reales de BD)', 'success');
      } else {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
    } catch (error: any) {
      console.error('Error testing configuration:', error);
      showToast(`Error en la prueba: ${error.message}`, 'error');
    } finally {
      setTesting(false);
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
    <div className="max-w-6xl mx-auto space-y-6">
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

        {/* Prueba de Configuración */}
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold mb-4 text-on-surface-light dark:text-on-surface-dark">
            🔍 Prueba de Configuración
          </h3>
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              placeholder="Hola, ¿qué productos tienen disponibles?"
              className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark"
            />
            <button
              onClick={testConfiguration}
              disabled={testing}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {testing ? '🔄' : '🧪'} Probar
            </button>
          </div>
          {testResult && (
            <div className="bg-white dark:bg-gray-700 p-3 rounded-lg border-l-4 border-blue-500">
              <h4 className="font-medium mb-2 text-on-surface-light dark:text-on-surface-dark">🤖 Respuesta del Bot:</h4>
              <p className="text-on-surface-light dark:text-on-surface-dark">{testResult}</p>
            </div>
          )}
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
  );
};

export default BotConfiguration;