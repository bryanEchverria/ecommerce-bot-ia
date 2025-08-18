
import React, { useState, useMemo } from 'react';
import { mockClients, mockOrders } from '../constants';
import { Client } from '../types';
import { PlusIcon, TrashIcon } from './Icons';
import ClientModal from './ClientModal';
import ConfirmationModal from './ConfirmationModal';
import { format, parseISO } from 'date-fns';
import { es, enUS } from 'date-fns/locale';
import ClientDetail from './ClientDetail';
import { useTranslation } from 'react-i18next';
import { useCurrency, formatCurrency } from './CurrencyContext';

const Clients: React.FC = () => {
    const { t, i18n } = useTranslation();
    const { currency } = useCurrency();
    const dateLocale = i18n.language.startsWith('es') ? es : enUS;

    const [clients, setClients] = useState<Client[]>(mockClients);
    const [selectedClient, setSelectedClient] = useState<Client | null>(null);
    const [isClientModalOpen, setIsClientModalOpen] = useState(false);
    const [editingClient, setEditingClient] = useState<Client | null>(null);
    const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);
    const [clientToDelete, setClientToDelete] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    const filteredClients = useMemo(() => {
        return clients.filter(client =>
            client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            client.email.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [clients, searchTerm]);

    const handleViewClient = (client: Client) => {
        setSelectedClient(client);
    };

    const handleBackToList = () => {
        setSelectedClient(null);
    };

    const handleAddClient = () => {
        setEditingClient(null);
        setIsClientModalOpen(true);
    };

    const handleEditClient = (client: Client) => {
        setEditingClient(client);
        setIsClientModalOpen(true);
    };

    const handleCloseClientModal = () => {
        setIsClientModalOpen(false);
        setEditingClient(null);
    };

    const handleSaveClient = (client: Client) => {
        if (editingClient) {
            setClients(clients.map(c => c.id === client.id ? client : c));
        } else {
            setClients([client, ...clients]);
        }
    };

    const handleInitiateDelete = (clientId: string) => {
        setClientToDelete(clientId);
        setIsConfirmModalOpen(true);
    };

    const handleConfirmDelete = () => {
        if (clientToDelete) {
            setClients(clients.filter(c => c.id !== clientToDelete));
            if (selectedClient && selectedClient.id === clientToDelete) {
                setSelectedClient(null);
            }
        }
        setIsConfirmModalOpen(false);
        setClientToDelete(null);
    };

    const handleCancelDelete = () => {
        setIsConfirmModalOpen(false);
        setClientToDelete(null);
    };
    
    if (selectedClient) {
        return <ClientDetail client={selectedClient} onBack={handleBackToList} />;
    }

    return (
        <>
            <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-lg">
                <div className="p-6 border-b border-gray-200 dark:border-white/10">
                    <div className="flex justify-between items-center">
                        <div>
                            <h2 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">{t('clients.title')}</h2>
                            <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">{t('clients.description')}</p>
                        </div>
                        <button onClick={handleAddClient} className="flex items-center gap-2 bg-primary text-white font-semibold py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors">
                            <PlusIcon className="h-5 w-5" />
                            <span>{t('clients.addClient')}</span>
                        </button>
                    </div>
                    <div className="mt-6">
                        <input
                            type="text"
                            placeholder={t('clients.searchPlaceholder')}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full bg-background-light dark:bg-background-dark border border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary"
                        />
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-white/5">
                            <tr className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                <th className="py-3 px-6 font-semibold">{t('clients.headers.client')}</th>
                                <th className="py-3 px-6 font-semibold">{t('clients.headers.phone')}</th>
                                <th className="py-3 px-6 font-semibold">{t('clients.headers.joinDate')}</th>
                                <th className="py-3 px-6 font-semibold text-right">{t('clients.headers.totalSpent')}</th>
                                <th className="py-3 px-6 font-semibold text-center">{t('common.actions')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredClients.length > 0 ? (
                                filteredClients.map((client) => (
                                    <tr key={client.id} className="border-b border-gray-200 dark:border-white/10 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors group">
                                        <td className="py-4 px-6">
                                            <div
                                                className="flex items-center gap-4 cursor-pointer"
                                                onClick={() => handleViewClient(client)}
                                            >
                                                <img src={client.avatarUrl} alt={client.name} className="h-10 w-10 rounded-full object-cover" />
                                                <div>
                                                    <p className="font-semibold text-on-surface-light dark:text-on-surface-dark group-hover:text-primary transition-colors">{client.name}</p>
                                                    <p className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark">{client.email}</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="py-4 px-6 text-sm">{client.phone}</td>
                                        <td className="py-4 px-6 text-sm">{format(parseISO(client.joinDate), 'MMM d, yyyy', { locale: dateLocale })}</td>
                                        <td className="py-4 px-6 text-sm text-right font-mono">{formatCurrency(client.totalSpent, currency, i18n.language)}</td>
                                        <td className="py-4 px-6 text-center">
                                            <div className="flex items-center justify-center gap-2">
                                                <button onClick={() => handleEditClient(client)} className="text-primary hover:underline text-sm font-semibold">{t('common.edit')}</button>
                                                <button onClick={() => handleInitiateDelete(client.id)} aria-label={t('confirmationModal.titles.client')} className="text-red-500/80 hover:text-red-500 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-white/10 transition-colors">
                                                    <TrashIcon className="h-5 w-5" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={5} className="text-center py-12 text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                        {t('clients.noClients')}
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
                <div className="p-4 border-t border-gray-200 dark:border-white/10 text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark text-center">
                    {t('clients.showingCount', { count: filteredClients.length, total: clients.length })}
                </div>
            </div>
            <ClientModal 
                isOpen={isClientModalOpen}
                onClose={handleCloseClientModal}
                onSave={handleSaveClient}
                client={editingClient}
            />
            <ConfirmationModal
                isOpen={isConfirmModalOpen}
                onClose={handleCancelDelete}
                onConfirm={handleConfirmDelete}
                title={t('confirmationModal.titles.client')}
                message={t('confirmationModal.messages.client')}
            />
        </>
    );
};

export default Clients;