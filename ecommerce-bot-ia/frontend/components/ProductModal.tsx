
import React, { useState, useEffect } from 'react';
import { Product, ProductStatus } from '../types';
import { XIcon } from './Icons';
import { useTranslation } from 'react-i18next';
import { useCurrency, getCurrencySymbol } from './CurrencyContext';

interface ProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (product: Product) => void;
  product: Product | null;
  categories: string[];
}

const ProductModal: React.FC<ProductModalProps> = ({ isOpen, onClose, onSave, product, categories }) => {
  const { t, i18n } = useTranslation();
  const { currency } = useCurrency();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: '',
    price: 0,
    salePrice: undefined as number | undefined,
    stock: 0,
    widthCm: undefined as number | undefined,
    heightCm: undefined as number | undefined,
    imageUrl: '',
    status: ProductStatus.Active,
  });
  
  const currencySymbol = getCurrencySymbol(currency, i18n.language);

  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name,
        description: product.description || '',
        category: product.category,
        price: product.price,
        salePrice: product.salePrice,
        stock: product.stock,
        widthCm: product.widthCm,
        heightCm: product.heightCm,
        imageUrl: product.imageUrl,
        status: product.status,
      });
    } else {
      setFormData({ 
        name: '', 
        description: '', 
        category: '', 
        price: 0, 
        salePrice: undefined, 
        stock: 0, 
        widthCm: undefined,
        heightCm: undefined,
        imageUrl: '',
        status: ProductStatus.Active 
      });
    }
  }, [product, isOpen]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    if (name === 'salePrice' || name === 'widthCm' || name === 'heightCm') {
        setFormData(prev => ({ ...prev, [name]: value ? parseFloat(value) : undefined }));
    } else if (type === 'number') {
        setFormData(prev => ({ ...prev, [name]: parseFloat(value) || 0 }));
    } else {
        setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Use the status exactly as the user selected it
    // No automatic status logic - respect user's choice
    const finalProduct: Product = {
      ...formData,
      salePrice: formData.salePrice || undefined,
      widthCm: formData.widthCm || undefined,
      heightCm: formData.heightCm || undefined,
      imageUrl: formData.imageUrl || `https://picsum.photos/seed/new${Date.now()}/400/400`,
      status: formData.status, // Use the status directly from form
      id: product ? product.id : `P${Date.now().toString().slice(-4)}`,
    };
    onSave(finalProduct);
    // Note: Modal will be closed by the parent component after successful save
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex justify-center items-center p-4" aria-modal="true" role="dialog">
      <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-2xl w-full max-w-lg animate-fade-in-up">
        <form onSubmit={handleSubmit}>
          <div className="p-6 border-b border-gray-200 dark:border-white/10 flex justify-between items-center">
            <h3 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">{product ? t('productModal.editTitle') : t('productModal.addTitle')}</h3>
            <button type="button" onClick={onClose} className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark hover:text-on-surface-light dark:text-on-surface-dark transition-colors p-1 rounded-full hover:bg-gray-100 dark:hover:bg-white/10">
              <XIcon className="h-6 w-6" />
            </button>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('productModal.labels.productName')}</label>
              <input type="text" name="name" id="name" value={formData.name} onChange={handleChange} required className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary" />
            </div>
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">Descripción</label>
              <textarea 
                name="description" 
                id="description" 
                value={formData.description} 
                onChange={handleChange} 
                rows={3}
                className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                placeholder="Descripción detallada del producto..."
              />
            </div>
            <div>
              <label htmlFor="imageUrl" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">URL de Imagen</label>
              <input 
                type="url" 
                name="imageUrl" 
                id="imageUrl" 
                value={formData.imageUrl} 
                onChange={handleChange} 
                className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="https://ejemplo.com/imagen.jpg"
              />
            </div>
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('productModal.labels.category')}</label>
              <input 
                type="text" 
                name="category" 
                id="category" 
                value={formData.category} 
                onChange={handleChange} 
                required 
                className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary"
                list="category-list"
              />
              <datalist id="category-list">
                {categories.map(cat => (
                  <option key={cat} value={cat} />
                ))}
              </datalist>
            </div>
             <div>
              <label htmlFor="status" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('productModal.labels.status')}</label>
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
                {Object.values(ProductStatus).map(status => (
                  <option key={status} value={status}>{t(`productStatus.${status}`)}</option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="price" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('productModal.labels.price')}</label>
                <div className="relative">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                        <span className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark sm:text-sm">{currencySymbol}</span>
                    </div>
                    <input type="number" name="price" id="price" value={formData.price} onChange={handleChange} required min="0" step="0.01" className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 pl-7 focus:outline-none focus:ring-2 focus:ring-primary" />
                </div>
              </div>
               <div>
                <label htmlFor="salePrice" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('productModal.labels.salePrice')}</label>
                <div className="relative">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                        <span className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark sm:text-sm">{currencySymbol}</span>
                    </div>
                    <input type="number" name="salePrice" id="salePrice" value={formData.salePrice ?? ''} onChange={handleChange} min="0" step="0.01" className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 pl-7 focus:outline-none focus:ring-2 focus:ring-primary" />
                </div>
              </div>
            </div>
             <div>
                <label htmlFor="stock" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">{t('productModal.labels.stock')}</label>
                <input type="number" name="stock" id="stock" value={formData.stock} onChange={handleChange} required min="0" className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="widthCm" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">Ancho (cm)</label>
                  <input 
                    type="number" 
                    name="widthCm" 
                    id="widthCm" 
                    value={formData.widthCm ?? ''} 
                    onChange={handleChange} 
                    min="0" 
                    step="0.1" 
                    className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Opcional"
                  />
                </div>
                <div>
                  <label htmlFor="heightCm" className="block text-sm font-medium text-on-surface-secondary-light dark:text-on-surface-secondary-dark mb-2">Alto (cm)</label>
                  <input 
                    type="number" 
                    name="heightCm" 
                    id="heightCm" 
                    value={formData.heightCm ?? ''} 
                    onChange={handleChange} 
                    min="0" 
                    step="0.1" 
                    className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Opcional"
                  />
                </div>
              </div>
          </div>
          <div className="p-4 bg-secondary-light dark:bg-secondary-dark/50 rounded-b-xl flex justify-end gap-4">
            <button type="button" onClick={onClose} className="bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark font-semibold py-2 px-4 rounded-lg border border-gray-300 dark:border-white/20 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">{t('common.cancel')}</button>
            <button type="submit" className="bg-primary text-white font-semibold py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors">{t('common.saveProduct')}</button>
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

export default ProductModal;
