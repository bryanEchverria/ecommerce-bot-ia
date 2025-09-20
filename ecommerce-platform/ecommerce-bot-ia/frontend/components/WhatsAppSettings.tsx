import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useToast } from './Toast';
import { SettingsIcon, CheckIcon, XIcon, PhoneIcon } from './Icons';

interface TwilioSettings {
  account_sid: string;
  auth_token: string;
  from_number: string;
}

interface MetaSettings {
  token: string;
  phone_number_id: string;
  graph_api_version: string;
}

interface WhatsAppSettingsData {
  id?: number;
  provider: 'twilio' | 'meta';
  is_active: boolean;
  has_twilio_config?: boolean;
  has_meta_config?: boolean;
  twilio_from?: string;
  meta_phone_number_id?: string;
  meta_graph_api_version?: string;
  created_at?: string;
  updated_at?: string;
}

interface WhatsAppSettingsFormData {
  provider: 'twilio' | 'meta';
  is_active: boolean;
  twilio_settings?: TwilioSettings;
  meta_settings?: MetaSettings;
}

const WhatsAppSettings: React.FC = () => {
  const { t } = useTranslation();
  const { showToast } = useToast();
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [settings, setSettings] = useState<WhatsAppSettingsData | null>(null);
  
  // Form state
  const [provider, setProvider] = useState<'twilio' | 'meta'>('twilio');
  const [isActive, setIsActive] = useState(true);
  
  // Twilio form state
  const [twilioAccountSid, setTwilioAccountSid] = useState('');
  const [twilioAuthToken, setTwilioAuthToken] = useState('');
  const [twilioFromNumber, setTwilioFromNumber] = useState('+14155238886');
  
  // Meta form state
  const [metaToken, setMetaToken] = useState('');
  const [metaPhoneNumberId, setMetaPhoneNumberId] = useState('');
  const [metaGraphVersion, setMetaGraphVersion] = useState('v21.0');
  
  // Test form state
  const [testPhoneNumber, setTestPhoneNumber] = useState('');
  const [testMessage, setTestMessage] = useState('Mensaje de prueba desde configuración WhatsApp');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/settings/whatsapp', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data: WhatsAppSettingsData = await response.json();
        setSettings(data);
        setProvider(data.provider);
        setIsActive(data.is_active);
        
        // Set display values for existing config (sin exponer tokens)
        if (data.provider === 'twilio') {
          // Remove whatsapp: prefix from display
          let displayFromNumber = data.twilio_from || '+14155238886';
          if (displayFromNumber.startsWith('whatsapp:')) {
            displayFromNumber = displayFromNumber.replace('whatsapp:', '');
          }
          setTwilioFromNumber(displayFromNumber);
        } else if (data.provider === 'meta') {
          setMetaPhoneNumberId(data.meta_phone_number_id || '');
          setMetaGraphVersion(data.meta_graph_api_version || 'v21.0');
        }
      } else if (response.status === 404) {
        // No hay configuración, usar valores por defecto
        setSettings(null);
      } else {
        throw new Error('Error cargando configuración');
      }
    } catch (error) {
      console.error('Error loading WhatsApp settings:', error);
      showToast('Error cargando configuración de WhatsApp', 'error');
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      const formData: WhatsAppSettingsFormData = {
        provider,
        is_active: isActive,
      };

      if (provider === 'twilio') {
        if (!twilioAccountSid || !twilioAuthToken) {
          throw new Error('Account SID y Auth Token son requeridos para Twilio');
        }
        
        // Process the from_number to ensure correct format
        let processedFromNumber = twilioFromNumber.trim();
        if (processedFromNumber && !processedFromNumber.startsWith('whatsapp:')) {
          // Add whatsapp: prefix if it's a phone number without prefix
          if (processedFromNumber.startsWith('+')) {
            processedFromNumber = `whatsapp:${processedFromNumber}`;
          }
        }
        
        formData.twilio_settings = {
          account_sid: twilioAccountSid,
          auth_token: twilioAuthToken,
          from_number: processedFromNumber,
        };
      } else if (provider === 'meta') {
        if (!metaToken || !metaPhoneNumberId) {
          throw new Error('Token y Phone Number ID son requeridos para Meta');
        }
        formData.meta_settings = {
          token: metaToken,
          phone_number_id: metaPhoneNumberId,
          graph_api_version: metaGraphVersion,
        };
      }

      const response = await fetch('/api/settings/whatsapp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const savedSettings: WhatsAppSettingsData = await response.json();
        setSettings(savedSettings);
        showToast('Configuración de WhatsApp guardada exitosamente', 'success');
        
        // Limpiar tokens después de guardar por seguridad
        setTwilioAuthToken('');
        setMetaToken('');
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Error guardando configuración');
      }
    } catch (error) {
      console.error('Error saving WhatsApp settings:', error);
      showToast(error instanceof Error ? error.message : 'Error guardando configuración', 'error');
    } finally {
      setSaving(false);
    }
  };

  const testConnection = async () => {
    if (!testPhoneNumber) {
      showToast('Ingrese un número de teléfono para la prueba', 'error');
      return;
    }

    setTesting(true);
    try {
      const response = await fetch('/api/settings/whatsapp/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          phone_number: testPhoneNumber,
          message: testMessage,
        }),
      });

      const result = await response.json();

      if (result.success) {
        showToast(`Mensaje enviado exitosamente via ${result.provider_used}`, 'success');
      } else {
        showToast(`Error: ${result.message}`, 'error');
      }
    } catch (error) {
      console.error('Error testing connection:', error);
      showToast('Error probando conexión', 'error');
    } finally {
      setTesting(false);
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
            {t('whatsapp.title')}
          </h1>
          <p className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">
            {t('whatsapp.description')}
          </p>
        </div>
        <SettingsIcon className="h-8 w-8 text-primary" />
      </div>

      {/* Current Status */}
      {settings && (
        <div className="bg-surface-light dark:bg-surface-dark p-4 rounded-lg border border-outline-light dark:border-outline-dark">
          <h3 className="font-semibold text-on-surface-light dark:text-on-surface-dark mb-2">
            {t('whatsapp.currentStatus')}
          </h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                {t('whatsapp.provider')}:
              </span>
              <span className="ml-2 font-semibold capitalize text-on-surface-light dark:text-on-surface-dark">
                {settings.provider}
              </span>
            </div>
            <div>
              <span className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                {t('whatsapp.status')}:
              </span>
              <span className={`ml-2 font-semibold ${settings.is_active ? 'text-green-600' : 'text-red-600'}`}>
                {settings.is_active ? t('whatsapp.active') : t('whatsapp.inactive')}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Configuration Form */}
      <div className="bg-secondary-light dark:bg-secondary-dark p-6 rounded-lg border border-outline-light dark:border-outline-dark">
        <h2 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark mb-6">
          {t('whatsapp.configuration')}
        </h2>

        {/* Provider Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-2">
            {t('whatsapp.selectProvider')}
          </label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="twilio"
                checked={provider === 'twilio'}
                onChange={(e) => setProvider(e.target.value as 'twilio' | 'meta')}
                className="mr-2"
              />
              <span className="text-on-surface-light dark:text-on-surface-dark">Twilio</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="meta"
                checked={provider === 'meta'}
                onChange={(e) => setProvider(e.target.value as 'twilio' | 'meta')}
                className="mr-2"
              />
              <span className="text-on-surface-light dark:text-on-surface-dark">Meta WhatsApp Cloud API</span>
            </label>
          </div>
        </div>

        {/* Active Toggle */}
        <div className="mb-6">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
              className="mr-2"
            />
            <span className="text-on-surface-light dark:text-on-surface-dark">
              {t('whatsapp.activateChannel')}
            </span>
          </label>
        </div>

        {/* Twilio Configuration */}
        {provider === 'twilio' && (
          <div className="space-y-4 mb-6">
            <h3 className="text-lg font-semibold text-on-surface-light dark:text-on-surface-dark">
              {t('whatsapp.twilioConfig')}
            </h3>
            
            <div>
              <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                Account SID
              </label>
              <input
                type="text"
                value={twilioAccountSid}
                onChange={(e) => setTwilioAccountSid(e.target.value)}
                placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                Auth Token
              </label>
              <input
                type="password"
                value={twilioAuthToken}
                onChange={(e) => setTwilioAuthToken(e.target.value)}
                placeholder="••••••••••••••••"
                className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                From Number
              </label>
              <input
                type="text"
                value={twilioFromNumber}
                onChange={(e) => setTwilioFromNumber(e.target.value)}
                placeholder="+14155238886"
                className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark"
              />
            </div>
          </div>
        )}

        {/* Meta Configuration */}
        {provider === 'meta' && (
          <div className="space-y-4 mb-6">
            <h3 className="text-lg font-semibold text-on-surface-light dark:text-on-surface-dark">
              {t('whatsapp.metaConfig')}
            </h3>
            
            <div>
              <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                WhatsApp Business Token
              </label>
              <input
                type="password"
                value={metaToken}
                onChange={(e) => setMetaToken(e.target.value)}
                placeholder="EAAG••••••••"
                className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                Phone Number ID
              </label>
              <input
                type="text"
                value={metaPhoneNumberId}
                onChange={(e) => setMetaPhoneNumberId(e.target.value)}
                placeholder="123456789012345"
                className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                Graph API Version
              </label>
              <input
                type="text"
                value={metaGraphVersion}
                onChange={(e) => setMetaGraphVersion(e.target.value)}
                placeholder="v21.0"
                className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark"
              />
            </div>
          </div>
        )}

        {/* Save Button */}
        <div className="flex justify-end mb-6">
          <button
            onClick={saveSettings}
            disabled={saving}
            className="flex items-center px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/80 disabled:opacity-50"
          >
            {saving ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            ) : (
              <CheckIcon className="h-4 w-4 mr-2" />
            )}
            {saving ? t('whatsapp.saving') : t('whatsapp.save')}
          </button>
        </div>

        {/* Test Connection */}
        {settings && (
          <div className="border-t border-outline-light dark:border-outline-dark pt-6">
            <h3 className="text-lg font-semibold text-on-surface-light dark:text-on-surface-dark mb-4">
              {t('whatsapp.testConnection')}
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                  {t('whatsapp.testPhoneNumber')}
                </label>
                <input
                  type="text"
                  value={testPhoneNumber}
                  onChange={(e) => setTestPhoneNumber(e.target.value)}
                  placeholder="+56912345678"
                  className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-on-surface-light dark:text-on-surface-dark mb-1">
                  {t('whatsapp.testMessage')}
                </label>
                <input
                  type="text"
                  value={testMessage}
                  onChange={(e) => setTestMessage(e.target.value)}
                  className="w-full px-3 py-2 border border-outline-light dark:border-outline-dark rounded-md bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark"
                />
              </div>
            </div>
            
            <button
              onClick={testConnection}
              disabled={testing || !testPhoneNumber}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {testing ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <PhoneIcon className="h-4 w-4 mr-2" />
              )}
              {testing ? t('whatsapp.testing') : t('whatsapp.testSend')}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default WhatsAppSettings;