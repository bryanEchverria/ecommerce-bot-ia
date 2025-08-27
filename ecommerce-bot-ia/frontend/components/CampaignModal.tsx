
import React, { useState, useEffect } from 'react';
import { Campaign, CampaignStatus, Product } from '../types';
import { XIcon } from './Icons';
import { useTranslation } from 'react-i18next';
import { useCurrency, getCurrencySymbol } from './CurrencyContext';

interface CampaignModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (campaign: Campaign) => void;
  campaign: Campaign | null;
  products: Product[];
}

const CampaignModal: React.FC<CampaignModalProps> = ({ isOpen, onClose, onSave, campaign, products }) => {
  const { t, i18n } = useTranslation();
  const { currency } = useCurrency();
  const [formData, setFormData] = useState({
    name: '',
    startDate: '',
    endDate: '',
    status: CampaignStatus.Active,
    budget: 0,
    productIds: [] as string[],
  });

  const currencySymbol = getCurrencySymbol(currency, i18n.language);

  useEffect(() => {
    if (campaign) {
      setFormData({
        name: campaign.name,
        startDate: campaign.startDate,
        endDate: campaign.endDate,
        status: campaign.status,
        budget: campaign.budget,
        productIds: campaign.productIds || [],
      });
    } else {
      setFormData({ 
          name: '', 
          startDate: new Date().toISOString().split('T')[0],
          endDate: new Date(new Date().setDate(new Date().getDate() + 30)).toISOString().split('T')[0],
          status: CampaignStatus.Active, 
          budget: 0,
          productIds: [],
      });
    }
  }, [campaign, isOpen]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'number') {
        setFormData(prev => ({ ...prev, [name]: parseFloat(value) || 0 }));
    } else {
        setFormData(prev => ({ ...prev, [name]: value as CampaignStatus }));
    }
  };
  
  const handleProductSelection = (productId: string) => {
    setFormData(prev => {
      const newProductIds = prev.productIds.includes(productId)
        ? prev.productIds.filter(id => id !== productId)
        : [...prev.productIds, productId];
      return { ...prev, productIds: newProductIds };
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const finalCampaign: Campaign = {
      ...formData,
      id: campaign ? campaign.id : `CAMP-${Date.now().toString().slice(-4)}`,
      imageUrl: campaign ? campaign.imageUrl : `https://picsum.photos/seed/new-camp-${Date.now()}/400/400`,
      clicks: campaign ? campaign.clicks : 0,
      conversions: campaign ? campaign.conversions : 0,
    };
    onSave(finalCampaign);
    // Note: Modal will be closed by the parent component after successful save
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex justify-center items-center p-4" aria-modal="true" role="dialog">
      <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-2xl w-full max-w-2xl animate-fade-in-up">
        <form onSubmit={handleSubmit}>
          <div className="p-6 border-b border-gray-200 dark:border-white/10 flex justify-between items-center">
            <h3 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">{campaign ? t('campaignModal.editTitle') : t('campaignModal.addTitle')}</h3>
            <button type="button" onClick={onClose} className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark hover:text-on-surface-light dark:text-on-surface-dark transition-colors p-1 rounded-full hover:bg-gray-100 dark:hover:bg-white/10">
              <XIcon className="h-6 w-6" />
            </button>
          </div>
          <div className="p-6 max-h-[70vh] overflow-y-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-x-6 gap-y-4">
                <div className="space-y-4">
                    <div>
                        <label htmlFor="name" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('campaignModal.labels.name')}</label>
                        <input type="text" name="name" id="name" value={formData.name} onChange={handleChange} required className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary" />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label htmlFor="startDate" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('campaignModal.labels.startDate')}</label>
                            <input type="date" name="startDate" id="startDate" value={formData.startDate} onChange={handleChange} required className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary" />
                        </div>
                        <div>
                            <label htmlFor="endDate" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('campaignModal.labels.endDate')}</label>
                            <input type="date" name="endDate" id="endDate" value={formData.endDate} onChange={handleChange} required className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary" />
                        </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label htmlFor="status" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('common.status')}</label>
                            <select 
                                name="status" 
                                id="status" 
                                value={formData.status} 
                                onChange={handleChange} 
                                className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary appearance-none"
                                style={{
                                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%239ca3af' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                                    backgroundPosition: 'right 0.5rem center',
                                    backgroundRepeat: 'no-repeat',
                                    backgroundSize: '1.5em 1.5em',
                                    paddingRight: '2.5rem'
                                }}
                            >
                                {Object.values(CampaignStatus).map(status => (
                                <option key={status} value={status}>{t(`campaignStatus.${status}`)}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="budget" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('campaignModal.labels.budget')}</label>
                            <div className="relative">
                                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                                    <span className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark sm:text-sm">{currencySymbol}</span>
                                </div>
                                <input type="number" name="budget" id="budget" value={formData.budget} onChange={handleChange} required min="0" step="0.01" className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 pl-7 focus:outline-none focus:ring-2 focus:ring-primary" />
                            </div>
                        </div>
                    </div>
                </div>
                <div className="space-y-2">
                    <label className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark">{t('campaignModal.labels.productsOnSale')}</label>
                    <div className="bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg p-3 max-h-56 overflow-y-auto space-y-2">
                        {products.map(product => (
                            <div key={product.id} className="flex items-center gap-3 p-2 rounded-md hover:bg-gray-50 dark:hover:bg-white/5">
                                <input
                                    type="checkbox"
                                    id={`product-${product.id}`}
                                    checked={formData.productIds.includes(product.id)}
                                    onChange={() => handleProductSelection(product.id)}
                                    className="h-4 w-4 rounded bg-surface-light dark:bg-surface-dark border-gray-300 dark:border-white/20 text-primary focus:ring-primary"
                                />
                                 <img src={product.imageUrl} alt={product.name} className="h-8 w-8 rounded-md object-cover" />
                                <label htmlFor={`product-${product.id}`} className="text-sm text-on-surface-light dark:text-on-surface-dark cursor-pointer flex-grow">{product.name}</label>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
          </div>
          <div className="p-4 bg-secondary-light dark:bg-secondary-dark/50 rounded-b-xl flex justify-end gap-4">
            <button type="button" onClick={onClose} className="bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark font-semibold py-2 px-4 rounded-lg border border-gray-300 dark:border-white/20 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">{t('common.cancel')}</button>
            <button type="submit" className="bg-primary text-white font-semibold py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors">{t('common.saveCampaign')}</button>
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

export default CampaignModal;
