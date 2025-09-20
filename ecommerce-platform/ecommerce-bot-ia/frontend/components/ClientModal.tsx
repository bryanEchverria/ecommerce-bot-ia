
import React, { useState, useEffect } from 'react';
import { Client } from '../types';
import { XIcon } from './Icons';
import { useTranslation } from 'react-i18next';

interface ClientModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (client: Client) => void;
  client: Client | null;
}

const ClientModal: React.FC<ClientModalProps> = ({ isOpen, onClose, onSave, client }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
  });

  useEffect(() => {
    if (client) {
      setFormData({
        name: client.name,
        email: client.email,
        phone: client.phone,
      });
    } else {
      setFormData({ name: '', email: '', phone: '' });
    }
  }, [client, isOpen]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const finalClient: Client = {
      id: client ? client.id : `C${Date.now().toString().slice(-4)}`,
      name: formData.name,
      email: formData.email,
      phone: formData.phone,
      joinDate: client ? client.joinDate : new Date().toISOString().split('T')[0],
      totalSpent: client ? client.totalSpent : 0,
      avatarUrl: client ? client.avatarUrl : `https://i.pravatar.cc/150?u=C${Date.now().toString().slice(-4)}`,
    };
    onSave(finalClient);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex justify-center items-center p-4" aria-modal="true" role="dialog">
      <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-2xl w-full max-w-lg animate-fade-in-up">
        <form onSubmit={handleSubmit}>
          <div className="p-6 border-b border-gray-200 dark:border-white/10 flex justify-between items-center">
            <h3 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">{client ? t('clientModal.editTitle') : t('clientModal.addTitle')}</h3>
            <button type="button" onClick={onClose} className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark hover:text-on-surface-light dark:text-on-surface-dark transition-colors p-1 rounded-full hover:bg-gray-100 dark:hover:bg-white/10">
              <XIcon className="h-6 w-6" />
            </button>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('clientModal.labels.fullName')}</label>
              <input type="text" name="name" id="name" value={formData.name} onChange={handleChange} required className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary" />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('clientModal.labels.email')}</label>
              <input type="email" name="email" id="email" value={formData.email} onChange={handleChange} required className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary" />
            </div>
             <div>
              <label htmlFor="phone" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('clientModal.labels.phone')}</label>
              <input type="tel" name="phone" id="phone" value={formData.phone} onChange={handleChange} required className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary" />
            </div>
          </div>
          <div className="p-4 bg-secondary-light dark:bg-secondary-dark/50 rounded-b-xl flex justify-end gap-4">
            <button type="button" onClick={onClose} className="bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark font-semibold py-2 px-4 rounded-lg border border-gray-300 dark:border-white/20 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">{t('common.cancel')}</button>
            <button type="submit" className="bg-primary text-white font-semibold py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors">{t('common.saveClient')}</button>
          </div>
        </form>
      </div>
      <style>{`
        @keyframes fade-in-up {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in-up {
            animation: fade-in-up 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default ClientModal;