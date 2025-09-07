import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useToast } from './Toast';
import { SettingsIcon, CheckIcon, CopyIcon, PhoneIcon } from './Icons';
import { tenantTwilioApi } from '../services/tenant-api';

interface TwilioConfig {
  tenant_id: string;
  account_sid: string;
  from_number?: string;
  webhook_url: string;
  status: string;
}

interface TwilioConfigForm {
  account_sid: string;
  auth_token: string;
  from_number?: string;
}

const TwilioSettings: React.FC = () => {
  const { t } = useTranslation();
  const { showToast } = useToast();
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<TwilioConfig | null>(null);
  const [webhookUrl, setWebhookUrl] = useState<string>('');
  
  // Form state
  const [accountSid, setAccountSid] = useState('');
  const [authToken, setAuthToken] = useState('');
  const [fromNumber, setFromNumber] = useState('whatsapp:+14155238886');

  useEffect(() => {
    loadConfig();
    loadWebhookUrl();
  }, []);

  const loadConfig = async () => {
    setLoading(true);
    try {
      const data = await tenantTwilioApi.getConfig();
      setConfig(data);
      setAccountSid(data.account_sid);
      setFromNumber(data.from_number || 'whatsapp:+14155238886');
    } catch (error: any) {
      if (!error.message.includes('404')) {
        console.error('Error loading Twilio config:', error);
        showToast('Error cargando configuración de Twilio', 'error');
      }
      // Si es 404, no hay configuración guardada (estado inicial válido)
      setConfig(null);
    } finally {
      setLoading(false);
    }
  };

  const loadWebhookUrl = async () => {
    try {
      const data = await tenantTwilioApi.getWebhookUrl();
      setWebhookUrl(data.webhook_url);
    } catch (error) {
      console.error('Error loading webhook URL:', error);
    }
  };

  const saveConfig = async () => {
    if (!accountSid.trim() || !authToken.trim()) {
      showToast('Account SID y Auth Token son requeridos', 'error');
      return;
    }

    setSaving(true);
    try {
      const formData: TwilioConfigForm = {
        account_sid: accountSid.trim(),
        auth_token: authToken.trim(),
        from_number: fromNumber.trim() || undefined,
      };

      const savedConfig = await tenantTwilioApi.upsertConfig(formData);
      setConfig(savedConfig);
      
      // Limpiar token después de guardar por seguridad
      setAuthToken('');
      
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

  const copyWebhookUrl = async () => {
    if (!webhookUrl) return;
    
    try {
      await navigator.clipboard.writeText(webhookUrl);
      showToast('URL de webhook copiada al portapapeles', 'success');
    } catch (error) {
      console.error('Error copying to clipboard:', error);
      showToast('Error copiando al portapapeles', 'error');
    }
  };

  const deleteConfig = async () => {
    if (!config) return;
    
    if (!confirm('¿Está seguro de que desea eliminar la configuración de Twilio?')) {
      return;
    }

    try {
      await tenantTwilioApi.deleteConfig();
      setConfig(null);
      setAccountSid('');
      setAuthToken('');
      setFromNumber('whatsapp:+14155238886');
      showToast('Configuración de Twilio eliminada exitosamente', 'success');
    } catch (error: any) {
      console.error('Error deleting Twilio config:', error);
      showToast(
        error.message || 'Error eliminando configuración de Twilio', 
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
            Configuración Twilio
          </h1>
          <p className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">
            Configure la integración de WhatsApp con Twilio para su tenant
          </p>
        </div>
        <SettingsIcon className="h-8 w-8 text-primary" />
      </div>

      {/* Current Status */}
      {config && (
        <div className="bg-surface-light dark:bg-surface-dark p-4 rounded-lg border border-outline-light dark:border-outline-dark">
          <h3 className="font-semibold text-on-surface-light dark:text-on-surface-dark mb-2">
            Estado Actual
          </h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                Account SID:
              </span>
              <span className="ml-2 font-mono text-on-surface-light dark:text-on-surface-dark">
                {config.account_sid}
              </span>
            </div>
            <div>
              <span className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                Estado:
              </span>
              <span className={`ml-2 font-semibold ${config.status === 'active' ? 'text-green-600' : 'text-red-600'}`}>
                {config.status === 'active' ? 'Activo' : 'Inactivo'}
              </span>
            </div>
            <div className="col-span-2">
              <span className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                Número:
              </span>
              <span className="ml-2 font-mono text-on-surface-light dark:text-on-surface-dark">
                {config.from_number || 'No configurado'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Webhook URL */}
      {webhookUrl && (
        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-700">
          <h3 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">
            URL de Webhook para Twilio
          </h3>
          <div className="flex items-center gap-2">
            <code className="flex-1 px-3 py-2 bg-white dark:bg-gray-800 border border-blue-200 dark:border-blue-600 rounded text-sm font-mono text-blue-900 dark:text-blue-100">
              {webhookUrl}
            </code>
            <button
              onClick={copyWebhookUrl}
              className="flex items-center px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              title="Copiar URL"
            >
              <CopyIcon className="h-4 w-4" />
            </button>
            <button
              onClick={() => {
                const slug = webhookUrl.split('.')[0].replace('https://', '');
                window.open(`https://${slug}.sintestesia.cl/twilio/test`, '_blank');
              }}
              className="flex items-center px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              title="Probar Webhook"
            >
              <PhoneIcon className="h-4 w-4" />
            </button>
          </div>
          <p className="text-xs text-blue-600 dark:text-blue-300 mt-2">
            Configure esta URL como webhook en su cuenta de Twilio para recibir mensajes de WhatsApp
          </p>
          <div className="text-xs text-blue-500 dark:text-blue-400 mt-2 space-y-1">
            <div><strong>Instrucciones:</strong></div>
            <div>1. Twilio Console → Messaging → Sandbox/WhatsApp → "When a message comes in" (POST)</div>
            <div>2. Status callback (opcional): https://{webhookUrl.split('.')[0].replace('https://', '')}.sintestesia.cl/twilio/status</div>
          </div>
        </div>
      )}

      {/* Configuration Form */}
      <div className="bg-secondary-light dark:bg-secondary-dark p-6 rounded-lg border border-outline-light dark:border-outline-dark">
        <h2 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark mb-6">
          Configuración
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
              Account SID <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={accountSid}
              onChange={(e) => setAccountSid(e.target.value)}
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
              value={authToken}
              onChange={(e) => setAuthToken(e.target.value)}
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
              value={fromNumber}
              onChange={(e) => setFromNumber(e.target.value)}
              placeholder="whatsapp:+14155238886"
              className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark font-mono text-sm"
            />
            <p className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">
              Número de WhatsApp proporcionado por Twilio (formato: whatsapp:+número)
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between mt-6">
          <div>
            {config && (
              <button
                onClick={deleteConfig}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Eliminar Configuración
              </button>
            )}
          </div>
          
          <button
            onClick={saveConfig}
            disabled={saving || !accountSid.trim() || !authToken.trim()}
            className="flex items-center px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/80 disabled:opacity-50"
          >
            {saving ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            ) : (
              <CheckIcon className="h-4 w-4 mr-2" />
            )}
            {saving ? 'Guardando...' : (config ? 'Actualizar' : 'Guardar')}
          </button>
        </div>
      </div>

      {/* Help Section */}
      <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-700">
        <h3 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
          Instrucciones de Configuración
        </h3>
        <div className="text-sm text-yellow-700 dark:text-yellow-300 space-y-2">
          <p>
            <strong>1.</strong> Obtenga su Account SID y Auth Token desde la consola de Twilio
          </p>
          <p>
            <strong>2.</strong> Configure el número de WhatsApp en Twilio Sandbox o con un número aprobado
          </p>
          <p>
            <strong>3.</strong> Copie la URL de webhook y configúrela en su cuenta de Twilio
          </p>
          <p>
            <strong>4.</strong> Asegúrese de que los webhooks estén habilitados en Twilio para mensajes entrantes
          </p>
        </div>
      </div>
    </div>
  );
};

export default TwilioSettings;