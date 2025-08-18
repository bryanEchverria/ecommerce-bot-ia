
import React, { useState, useMemo, useEffect } from 'react';
import { mockDiscounts } from '../constants';
import { Product, Discount, DiscountType } from '../types';
import { PlusIcon, TrashIcon } from './Icons';
import ProductModal from './ProductModal';
import { ProductStatusBadge } from './ProductStatusBadge';
import ConfirmationModal from './ConfirmationModal';
import { useTranslation } from 'react-i18next';
import { useCurrency, formatCurrency } from './CurrencyContext';
import { productsApi } from '../services/api';
import { useToast } from './Toast';
import { useDiscounts } from './DiscountsContext';

const getProductDisplayPrice = (product: Product, activeDiscounts: Discount[]) => {
    let basePrice = product.price;
    let finalPrice = product.price;
    
    // First apply sale price if it exists
    if (product.salePrice && product.salePrice < product.price) {
        finalPrice = product.salePrice;
        basePrice = product.salePrice;
    }

    // Then apply discounts to the current price (either regular price or sale price)
    for (const discount of activeDiscounts) {
        if (!discount.isActive) continue;

        const appliesToProduct = 
            discount.target === 'All' || 
            (discount.target === 'Category' && discount.category === product.category) ||
            (discount.target === 'Product' && discount.productId === product.id);

        if (appliesToProduct) {
            let discountedPrice;
            if (discount.type === DiscountType.Percentage) {
                // Apply percentage discount to the current price (base price)
                discountedPrice = basePrice * (1 - discount.value / 100);
            } else { // Fixed Amount
                // Apply fixed amount discount to the current price
                discountedPrice = basePrice - discount.value;
            }

            if (discountedPrice < finalPrice) {
                finalPrice = discountedPrice;
            }
        }
    }
    
    finalPrice = Math.max(0, finalPrice);

    return {
        originalPrice: product.price,
        displayPrice: finalPrice,
        isDiscounted: finalPrice < basePrice || basePrice < product.price,
    };
};


const Products: React.FC = () => {
    const { t, i18n } = useTranslation();
    const { currency } = useCurrency();
    const { showToast } = useToast();
    const { discounts } = useDiscounts();
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(true);
    const [isProductModalOpen, setIsProductModalOpen] = useState(false);
    const [editingProduct, setEditingProduct] = useState<Product | null>(null);
    const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);
    const [productToDelete, setProductToDelete] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('');

    const categories = useMemo(() => [t('common.all'), ...new Set(products.map(p => p.category))], [products, t]);
    
    // Initialize selectedCategory with translated 'All' value once translation is loaded
    useEffect(() => {
        if (!selectedCategory) {
            setSelectedCategory(t('common.all'));
        }
    }, [t, selectedCategory]);
    const productCategories = useMemo(() => [...new Set(products.map(p => p.category))], [products]);

    const filteredProducts = useMemo(() => {
        return products.filter(product => {
            const matchesCategory = selectedCategory === t('common.all') || product.category === selectedCategory;
            const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase());
            return matchesCategory && matchesSearch;
        });
    }, [products, searchTerm, selectedCategory, t]);
    
    const activeDiscounts = useMemo(() => discounts.filter(d => d.isActive), [discounts]);

    // Load products from API
    useEffect(() => {
        const loadProducts = async () => {
            try {
                setLoading(true);
                const productsData = await productsApi.getAll();
                
                // Transform API data to match frontend types
                const transformedProducts = productsData.map(p => ({
                    id: p.id,
                    name: p.name,
                    description: p.description,
                    category: p.category,
                    price: p.price,
                    salePrice: p.sale_price,
                    stock: p.stock,
                    widthCm: p.width_cm,
                    heightCm: p.height_cm,
                    imageUrl: p.image_url,
                    status: p.status
                }));
                
                setProducts(transformedProducts);
            } catch (error) {
                console.error('Error loading products:', error);
                setProducts([]);
            } finally {
                setLoading(false);
            }
        };

        loadProducts();
    }, []);

    const handleAddProduct = () => {
        setEditingProduct(null);
        setIsProductModalOpen(true);
    };

    const handleEditProduct = (product: Product) => {
        setEditingProduct(product);
        setIsProductModalOpen(true);
    };

    const handleCloseProductModal = () => {
        setIsProductModalOpen(false);
        setEditingProduct(null);
    };

    const handleSaveProduct = async (product: Product) => {
        try {
            // Transform frontend data to API format
            const apiProduct = {
                name: product.name,
                description: product.description || null,
                category: product.category,
                price: product.price,
                sale_price: product.salePrice || null,
                stock: product.stock,
                width_cm: product.widthCm || null,
                height_cm: product.heightCm || null,
                image_url: product.imageUrl,
                status: product.status
            };

            if (editingProduct) {
                // Update existing product
                const updatedProduct = await productsApi.update(product.id, apiProduct);
                const transformedProduct = {
                    id: updatedProduct.id,
                    name: updatedProduct.name,
                    description: updatedProduct.description,
                    category: updatedProduct.category,
                    price: updatedProduct.price,
                    salePrice: updatedProduct.sale_price,
                    stock: updatedProduct.stock,
                    widthCm: updatedProduct.width_cm,
                    heightCm: updatedProduct.height_cm,
                    imageUrl: updatedProduct.image_url,
                    status: updatedProduct.status
                };
                setProducts(products.map(p => p.id === product.id ? transformedProduct : p));
                showToast(t('products.messages.updated', { name: product.name }), 'success');
            } else {
                // Create new product
                const newProduct = await productsApi.create(apiProduct);
                const transformedProduct = {
                    id: newProduct.id,
                    name: newProduct.name,
                    description: newProduct.description,
                    category: newProduct.category,
                    price: newProduct.price,
                    salePrice: newProduct.sale_price,
                    stock: newProduct.stock,
                    widthCm: newProduct.width_cm,
                    heightCm: newProduct.height_cm,
                    imageUrl: newProduct.image_url,
                    status: newProduct.status
                };
                setProducts([transformedProduct, ...products]);
                
                // Reset filters to show the new product
                setSelectedCategory(t('common.all'));
                setSearchTerm('');
                
                showToast(t('products.messages.created', { name: product.name }), 'success');
            }
            // Close the modal after successful operation
            handleCloseProductModal();
        } catch (error) {
            console.error('Error saving product:', error);
            showToast(t('products.messages.error'), 'error');
        }
    };

    const handleInitiateDelete = (productId: string) => {
        setProductToDelete(productId);
        setIsConfirmModalOpen(true);
    };

    const handleConfirmDelete = async () => {
        if (productToDelete) {
            try {
                const productToDeleteObj = products.find(p => p.id === productToDelete);
                await productsApi.delete(productToDelete);
                setProducts(products.filter(p => p.id !== productToDelete));
                showToast(t('products.messages.deleted', { name: productToDeleteObj?.name || '' }), 'success');
            } catch (error) {
                console.error('Error deleting product:', error);
                showToast(t('products.messages.deleteError'), 'error');
            }
        }
        setIsConfirmModalOpen(false);
        setProductToDelete(null);
    };

    const handleCancelDelete = () => {
        setIsConfirmModalOpen(false);
        setProductToDelete(null);
    };


    return (
        <>
            <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-lg">
                <div className="p-6 border-b border-gray-200 dark:border-white/10">
                    <div className="flex justify-between items-center">
                        <div>
                            <h2 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">{t('products.title')}</h2>
                            <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">{t('products.description')}</p>
                        </div>
                        <button onClick={handleAddProduct} className="flex items-center gap-2 bg-primary text-white font-semibold py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors">
                            <PlusIcon className="h-5 w-5" />
                            <span>{t('products.addProduct')}</span>
                        </button>
                    </div>
                    <div className="mt-6 flex gap-4">
                        <input
                            type="text"
                            placeholder={t('products.searchPlaceholder')}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="flex-grow bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary"
                        />
                        <select
                            value={selectedCategory}
                            onChange={(e) => setSelectedCategory(e.target.value)}
                            className="bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary appearance-none"
                            style={{
                                backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%239ca3af' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                                backgroundPosition: 'right 0.5rem center',
                                backgroundRepeat: 'no-repeat',
                                backgroundSize: '1.5em 1.5em',
                                paddingRight: '2.5rem'
                            }}
                        >
                            {categories.map(category => (
                                <option key={category} value={category}>{category}</option>
                            ))}
                        </select>
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-white/5">
                            <tr className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                <th className="py-3 px-6 font-semibold">{t('products.table.productName')}</th>
                                <th className="py-3 px-6 font-semibold">{t('common.category')}</th>
                                <th className="py-3 px-6 font-semibold text-right">{t('common.price')}</th>
                                <th className="py-3 px-6 font-semibold text-center">{t('common.stock')}</th>
                                <th className="py-3 px-6 font-semibold text-center">{t('common.status')}</th>
                                <th className="py-3 px-6 font-semibold text-center">{t('common.actions')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={6} className="text-center py-12 text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                        {t('common.loading')}...
                                    </td>
                                </tr>
                            ) : filteredProducts.length > 0 ? (
                                filteredProducts.map((product) => {
                                    const { displayPrice, originalPrice, isDiscounted } = getProductDisplayPrice(product, activeDiscounts);
                                    return (
                                        <tr key={product.id} className="border-b border-gray-200 dark:border-white/10 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">
                                            <td className="py-4 px-6">
                                                <div className="flex items-center gap-4">
                                                    <img src={product.imageUrl} alt={product.name} className="h-12 w-12 rounded-lg object-cover" />
                                                    <div>
                                                        <p className="font-semibold text-on-surface-light dark:text-on-surface-dark">{product.name}</p>
                                                        <p className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark">{product.id}</p>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="py-4 px-6 text-sm">{product.category}</td>
                                            <td className="py-4 px-6 text-sm text-right font-mono">
                                                {isDiscounted ? (
                                                    <div>
                                                        <span className="text-green-400 font-bold">{formatCurrency(displayPrice, currency, i18n.language)}</span>
                                                        <div className="text-xs">
                                                            {product.salePrice && product.salePrice < product.price ? (
                                                                <>
                                                                    <s className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark/60">{formatCurrency(product.salePrice, currency, i18n.language)}</s>
                                                                    <s className="ml-1 text-on-surface-secondary-light dark:text-on-surface-secondary-dark/40">{formatCurrency(originalPrice, currency, i18n.language)}</s>
                                                                </>
                                                            ) : (
                                                                <s className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark/80">{formatCurrency(originalPrice, currency, i18n.language)}</s>
                                                            )}
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <div>
                                                        {product.salePrice && product.salePrice < product.price ? (
                                                            <>
                                                                <span className="text-green-400 font-bold">{formatCurrency(product.salePrice, currency, i18n.language)}</span>
                                                                <div className="text-xs">
                                                                    <s className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark/80">{formatCurrency(originalPrice, currency, i18n.language)}</s>
                                                                </div>
                                                            </>
                                                        ) : (
                                                            formatCurrency(originalPrice, currency, i18n.language)
                                                        )}
                                                    </div>
                                                )}
                                            </td>
                                            <td className="py-4 px-6 text-sm text-center">
                                                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                                                    product.stock > 0 && product.status !== 'Out of Stock'
                                                        ? product.stock > 50 ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                                                        : 'bg-red-500/20 text-red-400'}`}>
                                                    {t('common.units', { count: product.stock })}
                                                </span>
                                            </td>
                                            <td className="py-4 px-6 text-center">
                                                <ProductStatusBadge status={product.status} />
                                            </td>
                                            <td className="py-4 px-6 text-center">
                                                <div className="flex items-center justify-center gap-2">
                                                    <button onClick={() => handleEditProduct(product)} className="text-primary hover:underline text-sm font-semibold">{t('common.edit')}</button>
                                                    <button onClick={() => handleInitiateDelete(product.id)} aria-label={t('confirmationModal.titles.product')} className="text-red-500/80 hover:text-red-500 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-white/10 transition-colors">
                                                        <TrashIcon className="h-5 w-5" />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })
                            ) : (
                                <tr>
                                    <td colSpan={6} className="text-center py-12 text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                        {t('products.noProducts')}
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
                <div className="p-4 border-t border-gray-200 dark:border-white/10 text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark text-center">
                    {t('products.showingCount', { count: filteredProducts.length, total: products.length })}
                </div>
            </div>
            <ProductModal 
                isOpen={isProductModalOpen}
                onClose={handleCloseProductModal}
                onSave={handleSaveProduct}
                product={editingProduct}
                categories={productCategories}
            />
            <ConfirmationModal
                isOpen={isConfirmModalOpen}
                onClose={handleCancelDelete}
                onConfirm={handleConfirmDelete}
                title={t('confirmationModal.titles.product')}
                message={t('confirmationModal.messages.product')}
            />
        </>
    );
};

export default Products;
