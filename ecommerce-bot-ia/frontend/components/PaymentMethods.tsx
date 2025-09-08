import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useToast } from './Toast';
import { SettingsIcon, CheckIcon, CopyIcon, PhoneIcon, CreditCardIcon } from './Icons';
import { tenantTwilioApi, tenantFlowApi, tenantPaymentMethodsApi } from '../services/tenant-api';

interface TwilioConfig {
  account_sid: string;
  from_number?: string;
  webhook_url: string;
  status: string;
}

interface FlowConfig {
  api_key: string;
  base_url: string;
  webhook_base_url?: string;
  confirm_url: string;
  return_url: string;
  environment: string;
  status: string;
}

interface PaymentMethodsConfig {
  twilio_config?: TwilioConfig;
  flow_config?: FlowConfig;
  tenant_id: string;
  tenant_slug: string;
}

interface TwilioConfigForm {
  account_sid: string;
  auth_token: string;
  from_number?: string;
}

interface FlowConfigForm {
  api_key: string;
  secret_key: string;
  base_url?: string;
  webhook_base_url?: string;
}

const PaymentMethods: React.FC = () => {
  const { t } = useTranslation();
  const { showToast } = useToast();
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<PaymentMethodsConfig | null>(null);
  
  // Twilio form state
  const [twilioAccountSid, setTwilioAccountSid] = useState('');
  const [twilioAuthToken, setTwilioAuthToken] = useState('');
  const [twilioFromNumber, setTwilioFromNumber] = useState('whatsapp:+14155238886');
  
  // Flow form state
  const [flowApiKey, setFlowApiKey] = useState('');
  const [flowSecretKey, setFlowSecretKey] = useState('');
  const [flowBaseUrl, setFlowBaseUrl] = useState('https://sandbox.flow.cl/api');
  const [flowWebhookBaseUrl, setFlowWebhookBaseUrl] = useState('https://webhook.sintestesia.cl');

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setLoading(true);
    try {
      const data = await tenantPaymentMethodsApi.getConfig();
      setConfig(data);
      
      // Set Twilio form values
      if (data.twilio_config) {
        setTwilioAccountSid(data.twilio_config.account_sid || '');
        setTwilioFromNumber(data.twilio_config.from_number || 'whatsapp:+14155238886');
      }
      
      // Set Flow form values
      if (data.flow_config) {
        setFlowApiKey(data.flow_config.api_key || '');
        setFlowBaseUrl(data.flow_config.base_url || 'https://sandbox.flow.cl/api');
        setFlowWebhookBaseUrl(data.flow_config.webhook_base_url || 'https://webhook.sintestesia.cl');
      }
      
    } catch (error: any) {
      if (!error.message.includes('404')) {
        console.error('Error loading payment methods config:', error);
        showToast('Error cargando configuración de métodos de pago', 'error');
      }
      setConfig(null);
    } finally {
      setLoading(false);
    }
  };

  const saveTwilioConfig = async () => {
    if (!twilioAccountSid.trim() || !twilioAuthToken.trim()) {
      showToast('Account SID y Auth Token son requeridos para Twilio', 'error');
      return;
    }

    setSaving(true);
    try {
      const formData: TwilioConfigForm = {
        account_sid: twilioAccountSid.trim(),
        auth_token: twilioAuthToken.trim(),
        from_number: twilioFromNumber.trim() || undefined,
      };

      await tenantTwilioApi.upsertConfig(formData);
      
      // Clear token after saving for security
      setTwilioAuthToken('');
      
      // Reload config to get updated data
      await loadConfig();
      
      showToast('Configuración de Twilio guardada exitosamente', 'success');
    } catch (error: any) {
      console.error('Error saving Twilio config:', error);
      showToast(
        error.message || 'Error guardando configuración de Twilio', 
        'error'
      );
    } finally {
      setSaving(false);
    }
  };

  const saveFlowConfig = async () => {
    if (!flowApiKey.trim() || !flowSecretKey.trim()) {
      showToast('API Key y Secret Key son requeridos para Flow', 'error');
      return;
    }

    setSaving(true);
    try {
      const formData: FlowConfigForm = {
        api_key: flowApiKey.trim(),
        secret_key: flowSecretKey.trim(),
        base_url: flowBaseUrl.trim() || 'https://sandbox.flow.cl/api',
        webhook_base_url: flowWebhookBaseUrl.trim() || 'https://webhook.sintestesia.cl',
      };

      await tenantFlowApi.upsertConfig(formData);
      
      // Clear secret key after saving for security
      setFlowSecretKey('');
      
      // Reload config to get updated data
      await loadConfig();
      
      showToast('Configuración de Flow guardada exitosamente', 'success');
    } catch (error: any) {
      console.error('Error saving Flow config:', error);
      showToast(
        error.message || 'Error guardando configuración de Flow', 
        'error'
      );
    } finally {
      setSaving(false);
    }
  };

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      showToast(`${label} copiado`, 'success');
    } catch (error) {
      console.error('Error copying to clipboard:', error);
      showToast('Error copiando al portapapeles', 'error');
    }
  };

  const deleteTwilioConfig = async () => {
    if (!config?.twilio_config) return;
    
    if (!confirm('¿Está seguro de que desea eliminar la configuración de Twilio?')) {
      return;
    }

    try {
      await tenantTwilioApi.deleteConfig();
      await loadConfig();
      setTwilioAccountSid('');
      setTwilioAuthToken('');
      setTwilioFromNumber('whatsapp:+14155238886');
      showToast('Configuración de Twilio eliminada exitosamente', 'success');
    } catch (error: any) {
      console.error('Error deleting Twilio config:', error);
      showToast(
        error.message || 'Error eliminando configuración de Twilio', 
        'error'
      );
    }
  };

  const deleteFlowConfig = async () => {
    if (!config?.flow_config) return;
    
    if (!confirm('¿Está seguro de que desea eliminar la configuración de Flow?')) {
      return;
    }

    try {
      await tenantFlowApi.deleteConfig();
      await loadConfig();
      setFlowApiKey('');
      setFlowSecretKey('');
      setFlowBaseUrl('https://sandbox.flow.cl/api');
      setFlowWebhookBaseUrl('https://webhook.sintestesia.cl');
      showToast('Configuración de Flow eliminada exitosamente', 'success');
    } catch (error: any) {
      console.error('Error deleting Flow config:', error);
      showToast(
        error.message || 'Error eliminando configuración de Flow', 
        'error'
      );
    }
  };

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
            Métodos de Pago
          </h1>
          <p className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">
            Configure las integraciones de WhatsApp (Twilio) y pagos (Flow) para su tenant
          </p>
        </div>
        <SettingsIcon className="h-8 w-8 text-primary" />
      </div>

      {/* Current Status */}
      <div className="bg-surface-light dark:bg-surface-dark p-4 rounded-lg border border-outline-light dark:border-outline-dark">
        <h3 className="font-semibold text-on-surface-light dark:text-on-surface-dark mb-2">
          Estado Actual
        </h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <PhoneIcon className="h-4 w-4 text-blue-600" />
            <span className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
              Twilio (WhatsApp):
            </span>
            <span className={`font-semibold ${config?.twilio_config ? 'text-green-600' : 'text-red-600'}`}>
              {config?.twilio_config ? 'Configurado' : 'No configurado'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <CreditCardIcon className="h-4 w-4 text-green-600" />
            <span className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
              Flow (Pagos):
            </span>
            <span className={`font-semibold ${config?.flow_config ? 'text-green-600' : 'text-red-600'}`}>
              {config?.flow_config ? 'Configurado' : 'No configurado'}
            </span>
          </div>
        </div>
      </div>

      {/* Twilio Configuration */}
      <div className="bg-secondary-light dark:bg-secondary-dark p-6 rounded-lg border border-outline-light dark:border-outline-dark">
        <div className="flex items-center gap-2 mb-6">
          <PhoneIcon className="h-6 w-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">
            Configuración Twilio (WhatsApp)
          </h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
              Account SID <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={twilioAccountSid}
              onChange={(e) => setTwilioAccountSid(e.target.value)}
              placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
              className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark font-mono text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
              Auth Token <span className="text-red-500">*</span>
            </label>
            <input
              type="password"
              value={twilioAuthToken}
              onChange={(e) => setTwilioAuthToken(e.target.value)}
              placeholder="••••••••••••••••••••••••••••••••"
              className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark"
            />
            <p className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">
              El token se almacena cifrado y no se muestra por seguridad
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
              From Number (WhatsApp)
            </label>
            <input
              type="text"
              value={twilioFromNumber}
              onChange={(e) => setTwilioFromNumber(e.target.value)}
              placeholder="whatsapp:+14155238886"
              className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark font-mono text-sm"
            />
          </div>

          {config?.twilio_config && (
            <div>
              <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                Webhook URL
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={config.twilio_config.webhook_url || ''}
                  readOnly
                  className="flex-1 px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-gray-50 dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark font-mono text-sm cursor-default"
                />
                <button
                  onClick={() => copyToClipboard(config.twilio_config!.webhook_url, 'Webhook URL')}
                  className="px-3 py-2 bg-primary text-white rounded-md hover:bg-primary/80 text-sm font-medium"
                >
                  Copiar
                </button>
              </div>
            </div>
          )}

          <div className="flex justify-between">
            <div>
              {config?.twilio_config && (
                <button
                  onClick={deleteTwilioConfig}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Eliminar Twilio
                </button>
              )}
            </div>
            
            <button
              onClick={saveTwilioConfig}
              disabled={saving || !twilioAccountSid.trim() || !twilioAuthToken.trim()}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <CheckIcon className="h-4 w-4 mr-2" />
              )}
              {saving ? 'Guardando...' : (config?.twilio_config ? 'Actualizar Twilio' : 'Guardar Twilio')}
            </button>
          </div>
        </div>
      </div>

      {/* Flow Configuration */}
      <div className="bg-secondary-light dark:bg-secondary-dark p-6 rounded-lg border border-outline-light dark:border-outline-dark">
        <div className="flex items-center gap-2 mb-6">
          <CreditCardIcon className="h-6 w-6 text-green-600" />
          <h2 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">
            Configuración Flow (Pagos)
          </h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
              API Key <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={flowApiKey}
              onChange={(e) => setFlowApiKey(e.target.value)}
              placeholder="749C736F-E427-482B-8400-7630D11L7766"
              className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark font-mono text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
              Secret Key <span className="text-red-500">*</span>
            </label>
            <input
              type="password"
              value={flowSecretKey}
              onChange={(e) => setFlowSecretKey(e.target.value)}
              placeholder="••••••••••••••••••••••••••••••••"
              className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark"
            />
            <p className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">
              La clave se almacena cifrada y no se muestra por seguridad
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
              Environment
            </label>
            <select
              value={flowBaseUrl}
              onChange={(e) => setFlowBaseUrl(e.target.value)}
              className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark"
            >
              <option value="https://sandbox.flow.cl/api">Sandbox (Testing)</option>
              <option value="https://www.flow.cl/api">Production</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
              Webhook Base URL
            </label>
            <input
              type="text"
              value={flowWebhookBaseUrl}
              onChange={(e) => setFlowWebhookBaseUrl(e.target.value)}
              placeholder="https://webhook.sintestesia.cl"
              className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark font-mono text-sm"
            />
            <p className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">
              URL base para los webhooks de confirmación y retorno
            </p>
          </div>

          {config?.flow_config && (
            <>
              <div>
                <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                  Confirmation URL
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={config.flow_config.confirm_url || ''}
                    readOnly
                    className="flex-1 px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-gray-50 dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark font-mono text-sm cursor-default"
                  />
                  <button
                    onClick={() => copyToClipboard(config.flow_config!.confirm_url, 'Confirmation URL')}
                    className="px-3 py-2 bg-primary text-white rounded-md hover:bg-primary/80 text-sm font-medium"
                  >
                    Copiar
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                  Return URL
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={config.flow_config.return_url || ''}
                    readOnly
                    className="flex-1 px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-gray-50 dark:bg-gray-800 text-on-surface-light dark:text-on-surface-dark font-mono text-sm cursor-default"
                  />
                  <button
                    onClick={() => copyToClipboard(config.flow_config!.return_url, 'Return URL')}
                    className="px-3 py-2 bg-primary text-white rounded-md hover:bg-primary/80 text-sm font-medium"
                  >
                    Copiar
                  </button>
                </div>
              </div>
            </>
          )}

          <div className="flex justify-between">
            <div>
              {config?.flow_config && (
                <button
                  onClick={deleteFlowConfig}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Eliminar Flow
                </button>
              )}
            </div>
            
            <button
              onClick={saveFlowConfig}
              disabled={saving || !flowApiKey.trim() || !flowSecretKey.trim()}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {saving ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <CheckIcon className="h-4 w-4 mr-2" />
              )}
              {saving ? 'Guardando...' : (config?.flow_config ? 'Actualizar Flow' : 'Guardar Flow')}
            </button>
          </div>
        </div>
      </div>

      {/* Help Section */}
      <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-700">
        <h3 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
          Instrucciones de Configuración
        </h3>
        <div className="text-sm text-yellow-700 dark:text-yellow-300 space-y-2">
          <p><strong>Twilio (WhatsApp):</strong></p>
          <ul className="list-disc list-inside ml-4 space-y-1">
            <li>Obtenga su Account SID y Auth Token desde la consola de Twilio</li>
            <li>Configure el número de WhatsApp en Twilio Sandbox o con un número aprobado</li>
            <li>Configure el webhook URL en su cuenta de Twilio para mensajes entrantes</li>
          </ul>
          <p><strong>Flow (Pagos):</strong></p>
          <ul className="list-disc list-inside ml-4 space-y-1">
            <li>Obtenga su API Key y Secret Key desde el panel de Flow</li>
            <li>Use Sandbox para pruebas y Production para pagos reales</li>
            <li>Configure las URLs de confirmación y retorno en su cuenta de Flow</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default PaymentMethods;