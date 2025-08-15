import React, { useState, useMemo, useEffect } from 'react';
import { format, parseISO, isWithinInterval, startOfDay, endOfDay, subDays } from 'date-fns';
import { es, enUS } from 'date-fns/locale';
import { OrderStatusBadge } from './OrderStatusBadge';
import { DownloadIcon, PencilIcon } from './Icons';
import { useTranslation } from 'react-i18next';
import { useCurrency, formatCurrency } from './CurrencyContext';
import { Order, OrderStatus } from '../types';
import { ordersApi } from '../services/api';
import { useToast } from './Toast';

type TimeRange = 'today' | '7d' | '30d' | 'all';

const TimeRangeFilter: React.FC<{ selected: TimeRange, onSelect: (range: TimeRange) => void }> = ({ selected, onSelect }) => {
    const { t } = useTranslation();
    const ranges: { key: TimeRange; label: string }[] = [
        { key: 'today', label: t('orders.timeFilters.today') },
        { key: '7d', label: t('orders.timeFilters.7d') },
        { key: '30d', label: t('orders.timeFilters.30d') },
        { key: 'all', label: t('orders.timeFilters.allTime') },
    ];

    return (
        <div className="flex bg-surface rounded-lg p-1 space-x-1 w-full justify-around md:w-auto">
            {ranges.map(({ key, label }) => (
                <button
                    key={key}
                    onClick={() => onSelect(key)}
                    className={`px-3 py-1.5 rounded-md text-sm font-semibold transition-colors focus:outline-none flex-1 md:flex-none ${
                        selected === key
                            ? 'bg-primary text-white shadow'
                            : 'text-on-surface-secondary hover:bg-white/10'
                    }`}
                >
                    {label}
                </button>
            ))}
        </div>
    );
};

const Orders: React.FC = () => {
    const { t, i18n } = useTranslation();
    const { currency } = useCurrency();
    const { showToast } = useToast();
    const dateLocale = i18n.language.startsWith('es') ? es : enUS;

    const [orders, setOrders] = useState<Order[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState<OrderStatus | 'All'>('All');
    const [timeRange, setTimeRange] = useState<TimeRange>('all');
    const [editingOrderId, setEditingOrderId] = useState<string | null>(null);

    // Load data from API
    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                const ordersData = await ordersApi.getAll();
                
                // Transform API data to match frontend types
                const transformedOrders = ordersData.map(o => ({
                    id: o.id,
                    customerName: o.customer_name,
                    date: o.date,
                    items: o.items,
                    status: o.status,
                    total: o.total
                }));
                
                setOrders(transformedOrders);
            } catch (error) {
                console.error('Error loading orders data:', error);
                setOrders([]);
                showToast(t('orders.messages.loadError'), 'error');
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    const handleUpdateOrderStatus = async (orderId: string, newStatus: OrderStatus) => {
        try {
            const orderToUpdate = orders.find(o => o.id === orderId);
            if (!orderToUpdate) return;

            // Transform frontend data to API format
            const apiOrder = {
                customer_name: orderToUpdate.customerName,
                date: orderToUpdate.date,
                items: orderToUpdate.items,
                status: newStatus,
                total: orderToUpdate.total
            };

            const updatedOrder = await ordersApi.update(orderId, apiOrder);
            const transformedOrder = {
                id: updatedOrder.id,
                customerName: updatedOrder.customer_name,
                date: updatedOrder.date,
                items: updatedOrder.items,
                status: updatedOrder.status,
                total: updatedOrder.total
            };

            setOrders(orders.map(o => o.id === orderId ? transformedOrder : o));
            setEditingOrderId(null);
            showToast(t('orders.messages.updated', { id: orderId }), 'success');
        } catch (error) {
            console.error('Error updating order status:', error);
            showToast(t('orders.messages.updateError'), 'error');
        }
    };

    const filteredOrders = useMemo(() => {
        const now = new Date();
        let interval: { start: Date, end: Date } | null = null;

        switch (timeRange) {
            case 'today':
                interval = { start: startOfDay(now), end: endOfDay(now) };
                break;
            case '7d':
                interval = { start: startOfDay(subDays(now, 6)), end: endOfDay(now) };
                break;
            case '30d':
                interval = { start: startOfDay(subDays(now, 29)), end: endOfDay(now) };
                break;
            case 'all':
            default:
                interval = null;
                break;
        }

        return orders.filter(order => {
            const matchesSearch =
                order.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                order.customerName.toLowerCase().includes(searchTerm.toLowerCase());

            const matchesStatus = statusFilter === 'All' || order.status === statusFilter;

            const matchesDate = !interval || isWithinInterval(parseISO(order.date), interval);

            return matchesSearch && matchesStatus && matchesDate;
        });
    }, [searchTerm, statusFilter, timeRange, orders]);

    return (
        <div className="bg-surface rounded-xl shadow-lg">
            <div className="p-6 border-b border-white/10">
                 <div className="flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-semibold text-on-surface">{t('orders.title')}</h2>
                        <p className="text-sm text-on-surface-secondary mt-1">{t('orders.description')}</p>
                    </div>
                    <button className="flex items-center gap-2 bg-secondary text-on-surface font-semibold py-2 px-4 rounded-lg border border-white/20 hover:bg-white/5 transition-colors">
                        <DownloadIcon className="h-5 w-5" />
                        <span>{t('orders.export')}</span>
                    </button>
                </div>
                <div className="mt-6 px-6 pb-6 flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
                    <div className="flex flex-col sm:flex-row gap-4 w-full lg:flex-grow">
                        <input
                            type="text"
                            placeholder={t('orders.searchPlaceholder')}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full sm:flex-grow bg-background border border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary"
                        />
                        <select
                            aria-label={t('orders.filterByStatus')}
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value as OrderStatus | 'All')}
                            className="w-full sm:w-auto bg-background border border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary appearance-none"
                            style={{
                                backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%239ca3af' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                                backgroundPosition: 'right 0.5rem center',
                                backgroundRepeat: 'no-repeat',
                                backgroundSize: '1.5em 1.5em',
                                paddingRight: '2.5rem'
                            }}
                        >
                            <option value="All">{t('orders.allStatuses')}</option>
                            {Object.values(OrderStatus).map(status => (
                                <option key={status} value={status}>{t(`orderStatus.${status}`)}</option>
                            ))}
                        </select>
                    </div>
                    <div className="w-full lg:w-auto">
                        <TimeRangeFilter selected={timeRange} onSelect={setTimeRange} />
                    </div>
                </div>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-left">
                    <thead className="bg-white/5">
                        <tr className="text-sm text-on-surface-secondary">
                            <th className="py-3 px-6 font-semibold">{t('orders.headers.orderId')}</th>
                            <th className="py-3 px-6 font-semibold">{t('orders.headers.customerName')}</th>
                            <th className="py-3 px-6 font-semibold">{t('orders.headers.date')}</th>
                            <th className="py-3 px-6 font-semibold text-center">{t('orders.headers.items')}</th>
                            <th className="py-3 px-6 font-semibold">{t('common.status')}</th>
                            <th className="py-3 px-6 font-semibold text-right">{t('orders.headers.total')}</th>
                            <th className="py-3 px-6 font-semibold text-center">{t('common.actions')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td colSpan={7} className="text-center py-12 text-on-surface-secondary">
                                    {t('common.loading')}...
                                </td>
                            </tr>
                        ) : filteredOrders.length > 0 ? (
                            filteredOrders.map((order) => (
                                <tr key={order.id} className="border-b border-white/10 hover:bg-white/5 transition-colors">
                                    <td className="py-4 px-6 font-medium text-primary">{order.id}</td>
                                    <td className="py-4 px-6">{order.customerName}</td>
                                    <td className="py-4 px-6 text-sm text-on-surface-secondary">{format(parseISO(order.date), 'MMM d, yyyy, h:mm a', { locale: dateLocale })}</td>
                                    <td className="py-4 px-6 text-center">{order.items}</td>
                                    <td className="py-4 px-6">
                                        {editingOrderId === order.id ? (
                                            <select
                                                value={order.status}
                                                onChange={(e) => handleUpdateOrderStatus(order.id, e.target.value as OrderStatus)}
                                                onBlur={() => setEditingOrderId(null)}
                                                autoFocus
                                                className="bg-background border border-white/10 rounded-lg py-1 px-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary appearance-none"
                                                style={{
                                                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%239ca3af' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                                                    backgroundPosition: 'right 0.5rem center',
                                                    backgroundRepeat: 'no-repeat',
                                                    backgroundSize: '1em 1em',
                                                    paddingRight: '1.5rem'
                                                }}
                                            >
                                                {Object.values(OrderStatus).map(status => (
                                                    <option key={status} value={status}>{t(`orderStatus.${status}`)}</option>
                                                ))}
                                            </select>
                                        ) : (
                                            <OrderStatusBadge status={order.status} />
                                        )}
                                    </td>
                                    <td className="py-4 px-6 text-right font-semibold font-mono">{formatCurrency(order.total, currency, i18n.language)}</td>
                                    <td className="py-4 px-6 text-center">
                                        <button 
                                            onClick={() => setEditingOrderId(order.id)}
                                            className="text-primary hover:underline text-sm font-semibold flex items-center gap-1"
                                            disabled={editingOrderId === order.id}
                                        >
                                            <PencilIcon className="h-4 w-4" />
                                            {t('common.edit')}
                                        </button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                             <tr>
                                <td colSpan={7} className="text-center py-12 text-on-surface-secondary">
                                    {t('orders.noOrders')}
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
             <div className="p-4 border-t border-white/10 text-sm text-on-surface-secondary text-center">
                {t('orders.showingCount', { count: filteredOrders.length, total: orders.length })}
            </div>
        </div>
    );
};

export default Orders;