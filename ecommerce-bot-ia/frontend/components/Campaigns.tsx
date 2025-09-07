
import React, { useState, useEffect } from 'react';
import { Campaign, Product } from '../types';
import { PlusIcon, TrashIcon } from './Icons';
import CampaignModal from './CampaignModal';
import { CampaignStatusBadge } from './CampaignStatusBadge';
import ConfirmationModal from './ConfirmationModal';
import { format, parseISO } from 'date-fns';
import { es, enUS } from 'date-fns/locale';
import { useTranslation } from 'react-i18next';
import { useCurrency, formatCurrency } from './CurrencyContext';
import { campaignsApi, productsApi } from '../services/tenant-api';
import { useToast } from './Toast';

const Campaigns: React.FC = () => {
    const { t, i18n } = useTranslation();
    const { currency } = useCurrency();
    const { showToast } = useToast();
    const dateLocale = i18n.language.startsWith('es') ? es : enUS;

    const [campaigns, setCampaigns] = useState<Campaign[]>([]);
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(true);
    const [isCampaignModalOpen, setIsCampaignModalOpen] = useState(false);
    const [editingCampaign, setEditingCampaign] = useState<Campaign | null>(null);
    const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);
    const [campaignToDelete, setCampaignToDelete] = useState<string | null>(null);

    // Load data from API
    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                const [campaignsData, productsData] = await Promise.all([
                    campaignsApi.getAll(),
                    productsApi.getAll()
                ]);
                
                // Transform API data to match frontend types
                const transformedCampaigns = campaignsData.map(c => ({
                    id: c.id,
                    name: c.name,
                    startDate: c.start_date,
                    endDate: c.end_date,
                    status: c.status,
                    budget: c.budget,
                    clicks: c.clicks,
                    conversions: c.conversions,
                    imageUrl: c.image_url,
                    productIds: c.product_ids || []
                }));
                
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
                
                setCampaigns(transformedCampaigns);
                setProducts(transformedProducts);
            } catch (error) {
                console.error('Error loading campaigns data:', error);
                setCampaigns([]);
                setProducts([]);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    const handleAddCampaign = () => {
        setEditingCampaign(null);
        setIsCampaignModalOpen(true);
    };

    const handleEditCampaign = (campaign: Campaign) => {
        setEditingCampaign(campaign);
        setIsCampaignModalOpen(true);
    };

    const handleCloseCampaignModal = () => {
        setIsCampaignModalOpen(false);
        setEditingCampaign(null);
    };

    const handleSaveCampaign = async (campaign: Campaign) => {
        try {
            // Transform frontend data to API format
            const apiCampaign = {
                name: campaign.name,
                start_date: campaign.startDate,
                end_date: campaign.endDate,
                status: campaign.status,
                budget: campaign.budget,
                clicks: campaign.clicks,
                conversions: campaign.conversions,
                image_url: campaign.imageUrl,
                product_ids: campaign.productIds
            };

            if (editingCampaign) {
                // Update existing campaign
                const updatedCampaign = await campaignsApi.update(campaign.id, apiCampaign);
                const transformedCampaign = {
                    id: updatedCampaign.id,
                    name: updatedCampaign.name,
                    startDate: updatedCampaign.start_date,
                    endDate: updatedCampaign.end_date,
                    status: updatedCampaign.status,
                    budget: updatedCampaign.budget,
                    clicks: updatedCampaign.clicks,
                    conversions: updatedCampaign.conversions,
                    imageUrl: updatedCampaign.image_url,
                    productIds: updatedCampaign.product_ids || []
                };
                setCampaigns(campaigns.map(c => c.id === campaign.id ? transformedCampaign : c));
                showToast(t('campaigns.messages.updated', { name: campaign.name }), 'success');
            } else {
                // Create new campaign
                const newCampaign = await campaignsApi.create(apiCampaign);
                const transformedCampaign = {
                    id: newCampaign.id,
                    name: newCampaign.name,
                    startDate: newCampaign.start_date,
                    endDate: newCampaign.end_date,
                    status: newCampaign.status,
                    budget: newCampaign.budget,
                    clicks: newCampaign.clicks,
                    conversions: newCampaign.conversions,
                    imageUrl: newCampaign.image_url,
                    productIds: newCampaign.product_ids || []
                };
                setCampaigns([transformedCampaign, ...campaigns]);
                showToast(t('campaigns.messages.created', { name: campaign.name }), 'success');
            }
            // Close the modal after successful operation
            handleCloseCampaignModal();
        } catch (error) {
            console.error('Error saving campaign:', error);
            showToast(t('campaigns.messages.error'), 'error');
        }
    };

    const handleInitiateDelete = (campaignId: string) => {
        setCampaignToDelete(campaignId);
        setIsConfirmModalOpen(true);
    };

    const handleConfirmDelete = async () => {
        if (campaignToDelete) {
            try {
                const campaignToDeleteObj = campaigns.find(c => c.id === campaignToDelete);
                await campaignsApi.delete(campaignToDelete);
                setCampaigns(campaigns.filter(c => c.id !== campaignToDelete));
                showToast(t('campaigns.messages.deleted', { name: campaignToDeleteObj?.name || '' }), 'success');
            } catch (error) {
                console.error('Error deleting campaign:', error);
                showToast(t('campaigns.messages.deleteError'), 'error');
            }
        }
        setIsConfirmModalOpen(false);
        setCampaignToDelete(null);
    };

    const handleCancelDelete = () => {
        setIsConfirmModalOpen(false);
        setCampaignToDelete(null);
    };


    return (
        <>
            <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-lg">
                <div className="p-6 border-b border-gray-200 dark:border-white/10 flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">{t('campaigns.title')}</h2>
                        <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">{t('campaigns.description')}</p>
                    </div>
                    <button onClick={handleAddCampaign} className="flex items-center gap-2 bg-primary text-white font-semibold py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors">
                        <PlusIcon className="h-5 w-5" />
                        <span>{t('campaigns.addCampaign')}</span>
                    </button>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-white/5">
                            <tr className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                <th className="py-3 px-6 font-semibold">{t('campaigns.headers.campaign')}</th>
                                <th className="py-3 px-6 font-semibold text-center">{t('common.status')}</th>
                                <th className="py-3 px-6 font-semibold">{t('campaigns.headers.period')}</th>
                                <th className="py-3 px-6 font-semibold text-right">{t('campaigns.headers.products')}</th>
                                <th className="py-3 px-6 font-semibold text-right">{t('campaigns.headers.budget')}</th>
                                <th className="py-3 px-6 font-semibold text-center">Performance</th>
                                <th className="py-3 px-6 font-semibold text-center">{t('common.actions')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={7} className="text-center py-12 text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                        Loading campaigns...
                                    </td>
                                </tr>
                            ) : campaigns.length > 0 ? (
                                campaigns.map((campaign) => (
                                    <tr key={campaign.id} className="border-b border-gray-200 dark:border-white/10 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">
                                        <td className="py-4 px-6">
                                        <div className="flex items-center gap-4">
                                            <img src={campaign.imageUrl} alt={campaign.name} className="h-12 w-12 rounded-lg object-cover" />
                                            <div>
                                                <p className="font-semibold text-on-surface-light dark:text-on-surface-dark">{campaign.name}</p>
                                                <p className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark">{campaign.id}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="py-4 px-6 text-center">
                                        <CampaignStatusBadge status={campaign.status} />
                                    </td>
                                    <td className="py-4 px-6 text-sm">
                                        {format(parseISO(campaign.startDate), 'MMM d, yyyy', { locale: dateLocale })} - {format(parseISO(campaign.endDate), 'MMM d, yyyy', { locale: dateLocale })}
                                    </td>
                                     <td className="py-4 px-6 text-sm text-right font-medium">{campaign.productIds.length}</td>
                                    <td className="py-4 px-6 text-sm text-right font-mono">{formatCurrency(campaign.budget, currency, i18n.language)}</td>
                                    <td className="py-4 px-6 text-sm text-center">
                                        <div>
                                            <p className="font-semibold text-on-surface-light dark:text-on-surface-dark">{campaign.clicks.toLocaleString(i18n.language)} {t('common.clicks')}</p>
                                            <p className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark">{campaign.conversions.toLocaleString(i18n.language)} {t('common.conversions')}</p>
                                        </div>
                                    </td>
                                    <td className="py-4 px-6 text-center">
                                        <div className="flex items-center justify-center gap-2">
                                            <button onClick={() => handleEditCampaign(campaign)} className="text-primary hover:underline text-sm font-semibold">{t('common.edit')}</button>
                                            <button onClick={() => handleInitiateDelete(campaign.id)} aria-label={t('confirmationModal.titles.campaign')} className="text-red-500/80 hover:text-red-500 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-white/10 transition-colors">
                                                <TrashIcon className="h-5 w-5" />
                                            </button>
                                        </div>
                                    </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={7} className="text-center py-12 text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                        No campaigns available
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
                <div className="p-4 border-t border-gray-200 dark:border-white/10 text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark text-center">
                    {t('campaigns.showingCount', { count: campaigns.length, total: campaigns.length })}
                </div>
            </div>
            <CampaignModal 
                isOpen={isCampaignModalOpen}
                onClose={handleCloseCampaignModal}
                onSave={handleSaveCampaign}
                campaign={editingCampaign}
                products={products}
            />
            <ConfirmationModal
                isOpen={isConfirmModalOpen}
                onClose={handleCancelDelete}
                onConfirm={handleConfirmDelete}
                title={t('confirmationModal.titles.campaign')}
                message={t('confirmationModal.messages.campaign')}
            />
        </>
    );
};

export default Campaigns;
