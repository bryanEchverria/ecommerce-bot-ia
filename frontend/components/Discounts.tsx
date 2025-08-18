
import React, { useState, useEffect } from 'react';
import { Discount, DiscountType, Product } from '../types';
import { PlusIcon, TrashIcon } from './Icons';
import ConfirmationModal from './ConfirmationModal';
import DiscountModal from './DiscountModal';
import { DiscountStatusBadge } from './DiscountStatusBadge';
import { useTranslation } from 'react-i18next';
import { useCurrency, formatCurrency } from './CurrencyContext';
import { discountsApi, productsApi } from '../services/api';
import { useToast } from './Toast';
import { useDiscounts } from './DiscountsContext';

const Discounts: React.FC = () => {
    const { t, i18n } = useTranslation();
    const { currency } = useCurrency();
    const { showToast } = useToast();
    const { discounts, loading, updateDiscount, removeDiscount, addDiscount } = useDiscounts();
    const [products, setProducts] = useState<Product[]>([]);
    const [productsLoading, setProductsLoading] = useState(true);
    const [isDiscountModalOpen, setIsDiscountModalOpen] = useState(false);
    const [editingDiscount, setEditingDiscount] = useState<Discount | null>(null);
    const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);
    const [discountToDelete, setDiscountToDelete] = useState<string | null>(null);

    const productCategories = [...new Set(products.map(p => p.category))];

    // Load products from API
    useEffect(() => {
        const loadProducts = async () => {
            try {
                setProductsLoading(true);
                const productsData = await productsApi.getAll();
                
                const transformedProducts = productsData.map(p => ({
                    id: p.id,
                    name: p.name,
                    category: p.category,
                    price: p.price,
                    salePrice: p.sale_price,
                    stock: p.stock,
                    imageUrl: p.image_url,
                    status: p.status
                }));
                
                setProducts(transformedProducts);
            } catch (error) {
                console.error('Error loading products data:', error);
                setProducts([]);
            } finally {
                setProductsLoading(false);
            }
        };

        loadProducts();
    }, []);

    const handleAddDiscount = () => {
        setEditingDiscount(null);
        setIsDiscountModalOpen(true);
    };

    const handleEditDiscount = (discount: Discount) => {
        setEditingDiscount(discount);
        setIsDiscountModalOpen(true);
    };

    const handleCloseDiscountModal = () => {
        setIsDiscountModalOpen(false);
        setEditingDiscount(null);
    };

    const handleSaveDiscount = async (discount: Discount) => {
        try {
            // Transform frontend data to API format
            const apiDiscount = {
                name: discount.name,
                type: discount.type === DiscountType.Percentage ? 'Percentage' : 'FixedAmount',
                value: discount.value,
                target: discount.target,
                category: discount.category,
                product_id: discount.productId,
                is_active: discount.isActive
            };

            if (editingDiscount) {
                // Update existing discount
                const updatedDiscount = await discountsApi.update(discount.id, apiDiscount);
                const transformedDiscount = {
                    id: updatedDiscount.id,
                    name: updatedDiscount.name,
                    type: updatedDiscount.type === 'Percentage' ? DiscountType.Percentage : DiscountType.FixedAmount,
                    value: updatedDiscount.value,
                    target: updatedDiscount.target,
                    category: updatedDiscount.category,
                    productId: updatedDiscount.product_id,
                    isActive: updatedDiscount.is_active
                };
                updateDiscount(transformedDiscount);
                showToast(t('discounts.messages.updated', { name: discount.name }), 'success');
            } else {
                // Create new discount
                const newDiscount = await discountsApi.create(apiDiscount);
                const transformedDiscount = {
                    id: newDiscount.id,
                    name: newDiscount.name,
                    type: newDiscount.type === 'Percentage' ? DiscountType.Percentage : DiscountType.FixedAmount,
                    value: newDiscount.value,
                    target: newDiscount.target,
                    category: newDiscount.category,
                    productId: newDiscount.product_id,
                    isActive: newDiscount.is_active
                };
                addDiscount(transformedDiscount);
                showToast(t('discounts.messages.created', { name: discount.name }), 'success');
            }
            // Close the modal after successful operation
            handleCloseDiscountModal();
        } catch (error) {
            console.error('Error saving discount:', error);
            showToast(t('discounts.messages.error'), 'error');
        }
    };

    const handleInitiateDelete = (discountId: string) => {
        setDiscountToDelete(discountId);
        setIsConfirmModalOpen(true);
    };

    const handleConfirmDelete = async () => {
        if (discountToDelete) {
            try {
                const discountToDeleteObj = discounts.find(d => d.id === discountToDelete);
                await discountsApi.delete(discountToDelete);
                removeDiscount(discountToDelete);
                showToast(t('discounts.messages.deleted', { name: discountToDeleteObj?.name || '' }), 'success');
            } catch (error) {
                console.error('Error deleting discount:', error);
                showToast(t('discounts.messages.deleteError'), 'error');
            }
        }
        setIsConfirmModalOpen(false);
        setDiscountToDelete(null);
    };

    const handleCancelDelete = () => {
        setIsConfirmModalOpen(false);
        setDiscountToDelete(null);
    };
    
    const getTargetName = (discount: Discount) => {
        if (discount.target === 'All') return t('discounts.targets.all');
        if (discount.target === 'Category') return t('discounts.targets.category', {name: discount.category});
        if (discount.target === 'Product') {
            const productName = products.find(p => p.id === discount.productId)?.name;
            return t('discounts.targets.product', {name: productName || 'N/A'});
        }
        return 'N/A';
    }

    return (
        <>
            <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-lg">
                <div className="p-6 border-b border-gray-200 dark:border-white/10 flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">{t('discounts.title')}</h2>
                        <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">{t('discounts.description')}</p>
                    </div>
                    <button onClick={handleAddDiscount} className="flex items-center gap-2 bg-primary text-white font-semibold py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors">
                        <PlusIcon className="h-5 w-5" />
                        <span>{t('discounts.addDiscount')}</span>
                    </button>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-white/5">
                            <tr className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                <th className="py-3 px-6 font-semibold">{t('common.name')}</th>
                                <th className="py-3 px-6 font-semibold">{t('common.type')}</th>
                                <th className="py-3 px-6 font-semibold text-right">{t('common.value')}</th>
                                <th className="py-3 px-6 font-semibold">{t('common.target')}</th>
                                <th className="py-3 px-6 font-semibold text-center">{t('common.status')}</th>
                                <th className="py-3 px-6 font-semibold text-center">{t('common.actions')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading || productsLoading ? (
                                <tr>
                                    <td colSpan={6} className="text-center py-12 text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                        Loading discounts...
                                    </td>
                                </tr>
                            ) : discounts.length > 0 ? (
                                discounts.map((discount) => (
                                <tr key={discount.id} className="border-b border-gray-200 dark:border-white/10 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">
                                    <td className="py-4 px-6">
                                        <p className="font-semibold text-on-surface-light dark:text-on-surface-dark">{discount.name}</p>
                                        <p className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark">{discount.id}</p>
                                    </td>
                                    <td className="py-4 px-6 text-sm">{t(`discountType.${discount.type}`)}</td>
                                    <td className="py-4 px-6 text-sm text-right font-mono">
                                        {discount.type === DiscountType.Percentage ? `${discount.value}%` : formatCurrency(discount.value, currency, i18n.language)}
                                    </td>
                                    <td className="py-4 px-6 text-sm">
                                       {getTargetName(discount)}
                                    </td>
                                    <td className="py-4 px-6 text-center">
                                        <DiscountStatusBadge isActive={discount.isActive} />
                                    </td>
                                    <td className="py-4 px-6 text-center">
                                        <div className="flex items-center justify-center gap-2">
                                            <button onClick={() => handleEditDiscount(discount)} className="text-primary hover:underline text-sm font-semibold">{t('common.edit')}</button>
                                            <button onClick={() => handleInitiateDelete(discount.id)} aria-label={t('confirmationModal.titles.discount')} className="text-red-500/80 hover:text-red-500 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-white/10 transition-colors">
                                                <TrashIcon className="h-5 w-5" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={6} className="text-center py-12 text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                        No discounts available
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
                <div className="p-4 border-t border-gray-200 dark:border-white/10 text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark text-center">
                    {t('discounts.showingCount', { count: discounts.length, total: discounts.length })}
                </div>
            </div>
            <DiscountModal 
                isOpen={isDiscountModalOpen}
                onClose={handleCloseDiscountModal}
                onSave={handleSaveDiscount}
                discount={editingDiscount}
                categories={productCategories}
                products={products}
            />
            <ConfirmationModal
                isOpen={isConfirmModalOpen}
                onClose={handleCancelDelete}
                onConfirm={handleConfirmDelete}
                title={t('confirmationModal.titles.discount')}
                message={t('confirmationModal.messages.discount')}
            />
        </>
    );
};

export default Discounts;
