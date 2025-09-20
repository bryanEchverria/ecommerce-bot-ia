
import React, { useState, useEffect } from 'react';
import { Discount, DiscountType, Product } from '../types';
import { XIcon } from './Icons';
import { useTranslation } from 'react-i18next';
import { useCurrency, getCurrencySymbol } from './CurrencyContext';

interface DiscountModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (discount: Discount) => void;
  discount: Discount | null;
  categories: string[];
  products: Product[];
}

const DiscountModal: React.FC<DiscountModalProps> = ({ isOpen, onClose, onSave, discount, categories, products }) => {
  const { t, i18n } = useTranslation();
  const { currency } = useCurrency();
  const [formData, setFormData] = useState({
    name: '',
    type: DiscountType.Percentage,
    value: 0,
    target: 'All' as 'All' | 'Category' | 'Product',
    category: '',
    productId: '',
    isActive: true,
  });

  const currencySymbol = getCurrencySymbol(currency, i18n.language);

  useEffect(() => {
    if (discount) {
      setFormData({
        name: discount.name,
        type: discount.type,
        value: discount.value,
        target: discount.target,
        category: discount.category || '',
        productId: discount.productId || '',
        isActive: discount.isActive,
      });
    } else {
      setFormData({
        name: '',
        type: DiscountType.Percentage,
        value: 0,
        target: 'All',
        category: categories[0] || '',
        productId: products[0]?.id || '',
        isActive: true,
      });
    }
  }, [discount, isOpen, categories, products]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'number') {
        setFormData(prev => ({ ...prev, [name]: parseFloat(value) || 0 }));
    } else {
        setFormData(prev => ({ ...prev, [name]: value as DiscountType | 'All' | 'Category' | 'Product' }));
    }
  };

  const handleToggle = () => {
      setFormData(prev => ({ ...prev, isActive: !prev.isActive }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const finalDiscount: Discount = {
      ...formData,
      id: discount ? discount.id : `D${Date.now().toString().slice(-4)}`,
      category: formData.target === 'Category' ? formData.category : undefined,
      productId: formData.target === 'Product' ? formData.productId : undefined,
    };
    onSave(finalDiscount);
    // Note: Modal will be closed by the parent component after successful save
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex justify-center items-center p-4" aria-modal="true" role="dialog">
      <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-2xl w-full max-w-lg animate-fade-in-up">
        <form onSubmit={handleSubmit}>
          <div className="p-6 border-b border-gray-200 dark:border-white/10 flex justify-between items-center">
            <h3 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">{discount ? t('discountModal.editTitle') : t('discountModal.addTitle')}</h3>
            <button type="button" onClick={onClose} className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark hover:text-on-surface-light dark:text-on-surface-dark transition-colors p-1 rounded-full hover:bg-gray-100 dark:hover:bg-white/10">
              <XIcon className="h-6 w-6" />
            </button>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('discountModal.labels.name')}</label>
              <input type="text" name="name" id="name" value={formData.name} onChange={handleChange} required className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary" />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="type" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('discountModal.labels.type')}</label>
                <select name="type" id="type" value={formData.type} onChange={handleChange} className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary appearance-none custom-select">
                    {Object.values(DiscountType).map(type => ( <option key={type} value={type}>{t(`discountType.${type}`)}</option>))}
                </select>
              </div>
              <div>
                <label htmlFor="value" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('discountModal.labels.value')}</label>
                <div className="relative">
                    {formData.type === DiscountType.FixedAmount && (
                        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                            <span className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark sm:text-sm">{currencySymbol}</span>
                        </div>
                    )}
                    <input 
                        type="number" 
                        name="value" 
                        id="value" 
                        value={formData.value} 
                        onChange={handleChange} 
                        required 
                        min="0" 
                        step={formData.type === DiscountType.Percentage ? "1" : "0.01"}
                        className={`w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary ${formData.type === DiscountType.FixedAmount ? 'pl-7' : 'pr-7'}`}
                    />
                    {formData.type === DiscountType.Percentage && (
                        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                            <span className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark sm:text-sm">%</span>
                        </div>
                    )}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="target" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('discountModal.labels.target')}</label>
                <select name="target" id="target" value={formData.target} onChange={handleChange} className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary appearance-none custom-select">
                    <option value="All">{t('discountModal.targets.all')}</option>
                    <option value="Category">{t('discountModal.targets.category')}</option>
                    <option value="Product">{t('discountModal.targets.product')}</option>
                </select>
              </div>
              {formData.target === 'Category' && (
                <div>
                    <label htmlFor="category" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('discountModal.labels.category')}</label>
                     <select name="category" id="category" value={formData.category} onChange={handleChange} className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary appearance-none custom-select">
                        {categories.map(cat => ( <option key={cat} value={cat}>{cat}</option>))}
                    </select>
                </div>
              )}
               {formData.target === 'Product' && (
                <div>
                    <label htmlFor="productId" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('discountModal.labels.product')}</label>
                     <select name="productId" id="productId" value={formData.productId} onChange={handleChange} className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary appearance-none custom-select">
                        {products.map(prod => ( <option key={prod.id} value={prod.id}>{prod.name}</option>))}
                    </select>
                </div>
              )}
            </div>

            <div className="flex items-center justify-between">
                <label htmlFor="isActive" className="text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark">{t('discountModal.labels.status')}</label>
                <button type="button" onClick={handleToggle} className={`relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary ${formData.isActive ? 'bg-primary' : 'bg-gray-600'}`}>
                    <span className={`inline-block w-5 h-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200 ${formData.isActive ? 'translate-x-5' : 'translate-x-0'}`}></span>
                </button>
            </div>
          </div>
          <div className="p-4 bg-secondary-light dark:bg-secondary-dark/50 rounded-b-xl flex justify-end gap-4">
            <button type="button" onClick={onClose} className="bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark font-semibold py-2 px-4 rounded-lg border border-gray-300 dark:border-white/20 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">{t('common.cancel')}</button>
            <button type="submit" className="bg-primary text-white font-semibold py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors">{t('common.saveDiscount')}</button>
          </div>
        </form>
      </div>
      <style>{`
        .custom-select {
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%239ca3af' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
            background-position: right 0.5rem center;
            background-repeat: no-repeat;
            background-size: 1.5em 1.5em;
            padding-right: 2.5rem;
        }
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

export default DiscountModal;
