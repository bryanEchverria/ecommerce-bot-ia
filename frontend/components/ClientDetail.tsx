
import React from 'react';
import { Client } from '../types';
import { ArrowLeftIcon, CalendarIcon, MailIcon, PhoneIcon } from './Icons';
import { format, parseISO } from 'date-fns';
import { es, enUS } from 'date-fns/locale';
import { mockOrders } from '../constants';
import { OrderStatusBadge } from './OrderStatusBadge';
import { useTranslation } from 'react-i18next';
import { useCurrency, formatCurrency } from './CurrencyContext';

interface ClientDetailProps {
  client: Client;
  onBack: () => void;
}

const ClientDetail: React.FC<ClientDetailProps> = ({ client, onBack }) => {
    const { t, i18n } = useTranslation();
    const { currency } = useCurrency();
    const dateLocale = i18n.language.startsWith('es') ? es : enUS;
    const clientOrders = mockOrders.filter(order => order.customerName === client.name);

    return (
        <div className="space-y-6 animate-fade-in">
             <button
                onClick={onBack}
                className="flex items-center gap-2 text-on-surface-secondary-light dark:text-on-surface-secondary-dark hover:text-on-surface-light dark:text-on-surface-dark font-semibold py-2 px-3 rounded-lg hover:bg-surface-light dark:bg-surface-dark transition-colors mb-4 -ml-3"
            >
                <ArrowLeftIcon className="h-5 w-5" />
                <span>{t('clients.back')}</span>
            </button>

            {/* Client Info Card */}
            <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-lg p-6 flex flex-col md:flex-row items-start gap-6">
                <img src={client.avatarUrl} alt={client.name} className="h-24 w-24 rounded-full border-4 border-primary" />
                <div className="flex-grow">
                    <h2 className="text-2xl font-bold text-on-surface-light dark:text-on-surface-dark">{client.name}</h2>
                    <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                         <div className="flex items-center gap-2">
                             <MailIcon className="h-4 w-4" />
                            <span className="text-sm">{client.email}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <PhoneIcon className="h-4 w-4" />
                            <span className="text-sm">{client.phone}</span>
                        </div>
                         <div className="flex items-center gap-2">
                            <CalendarIcon className="h-4 w-4" />
                            <span className="text-sm">{t('clients.joinedOn', { date: format(parseISO(client.joinDate), 'MMM d, yyyy', { locale: dateLocale }) })}</span>
                        </div>
                    </div>
                </div>
                <div className="w-full md:w-auto text-center md:text-right border-t md:border-t-0 md:border-l border-gray-200 dark:border-white/10 pt-4 md:pt-0 md:pl-6 mt-4 md:mt-0">
                    <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark font-medium">{t('clients.totalSpentLabel')}</p>
                    <p className="text-3xl font-bold text-primary mt-1">{formatCurrency(client.totalSpent, currency, i18n.language)}</p>
                </div>
            </div>

            {/* Order History */}
            <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-lg">
                <div className="p-6 border-b border-gray-200 dark:border-white/10">
                    <h3 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">{t('clients.orderHistory')}</h3>
                    <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">{t('clients.orderHistoryDesc', { name: client.name })}</p>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                         <thead className="bg-white/5">
                            <tr className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                <th className="py-3 px-6 font-semibold">{t('orders.headers.orderId')}</th>
                                <th className="py-3 px-6 font-semibold">{t('orders.headers.date')}</th>
                                <th className="py-3 px-6 font-semibold text-center">{t('orders.headers.items')}</th>
                                <th className="py-3 px-6 font-semibold">{t('common.status')}</th>
                                <th className="py-3 px-6 font-semibold text-right">{t('orders.headers.total')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {clientOrders.length > 0 ? (
                                clientOrders.map((order) => (
                                    <tr key={order.id} className="border-b border-gray-200 dark:border-white/10 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">
                                        <td className="py-4 px-6 font-medium text-primary">{order.id}</td>
                                        <td className="py-4 px-6 text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">{format(parseISO(order.date), 'MMM d, yyyy, h:mm a', { locale: dateLocale })}</td>
                                        <td className="py-4 px-6 text-center">{order.items}</td>
                                        <td className="py-4 px-6">
                                            <OrderStatusBadge status={order.status} />
                                        </td>
                                        <td className="py-4 px-6 text-right font-semibold font-mono">{formatCurrency(order.total, currency, i18n.language)}</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={5} className="text-center py-12 text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                        {t('clients.noOrders')}
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
                 <div className="p-4 border-t border-gray-200 dark:border-white/10 text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark text-center">
                    {t('clients.foundOrders', { count: clientOrders.length })}
                </div>
            </div>
             <style>{`
                @keyframes fade-in {
                    from { opacity: 0; transform: translateY(-10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .animate-fade-in {
                    animation: fade-in 0.3s ease-out forwards;
                }
            `}</style>
        </div>
    );
};

export default ClientDetail;
