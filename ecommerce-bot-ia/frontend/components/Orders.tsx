import React, { useState, useMemo, useEffect } from 'react';
import { format, parseISO, isWithinInterval, startOfDay, endOfDay, subDays } from 'date-fns';
import { es, enUS } from 'date-fns/locale';
import { OrderStatusBadge } from './OrderStatusBadge';
import { DownloadIcon, PencilIcon } from './Icons';
import { useTranslation } from 'react-i18next';
import { useCurrency, formatCurrency } from './CurrencyContext';
import { Order, OrderStatus } from '../types';
import { tenantOrdersApi } from '../services/tenant-api';

const ordersApi = {
  getAll: async () => {
    try {
      const response = await fetch('/api/flow-orders/');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      return data.pedidos || [];
    } catch (error) {
      console.error('Error fetching flow orders:', error);
      return [];
    }
  }
};
import { useToast } from './Toast';
import OrderDetailsModal from './OrderDetailsModal';

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
        <div className="flex bg-surface-light dark:bg-surface-dark rounded-lg p-1 gap-1 max-w-full overflow-hidden">
            {ranges.map(({ key, label }) => (
                <button
                    key={key}
                    onClick={() => onSelect(key)}
                    className={`px-2 sm:px-3 py-1.5 rounded-md text-xs sm:text-sm font-semibold transition-colors focus:outline-none whitespace-nowrap ${
                        selected === key
                            ? 'bg-primary text-white shadow'
                            : 'text-on-surface-secondary-light dark:text-on-surface-secondary-dark hover:bg-gray-100 dark:hover:bg-white/10'
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
    const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
    const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);

    // Load data from API
    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                const ordersData = await ordersApi.getAll();
                
                // Transform tenant API data to match frontend types
                const transformedOrders = ordersData.map(o => ({
                    id: o.id,
                    orderNumber: o.code, // tenant API uses 'code' instead of 'order_number'
                    customerName: o.customer_name,
                    date: o.created_at || o.date, // tenant API uses 'created_at' instead of 'date'
                    items: o.items || 1, // default to 1 if not present
                    status: o.status,
                    total: typeof o.total === 'string' ? parseFloat(o.total) : o.total // tenant API sends total as string
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

            // Transform frontend data to tenant API format
            const apiOrder = {
                code: orderToUpdate.orderNumber,
                customer_name: orderToUpdate.customerName,
                status: newStatus,
                total: orderToUpdate.total.toString() // tenant API expects string
            };

            const updatedOrder = await ordersApi.update(orderId, apiOrder);
            const transformedOrder = {
                id: updatedOrder.id,
                orderNumber: updatedOrder.code, // tenant API uses 'code'
                customerName: updatedOrder.customer_name,
                date: updatedOrder.created_at || updatedOrder.date, // tenant API uses 'created_at'
                items: updatedOrder.items || 1,
                status: updatedOrder.status,
                total: typeof updatedOrder.total === 'string' ? parseFloat(updatedOrder.total) : updatedOrder.total
            };

            setOrders(orders.map(o => o.id === orderId ? transformedOrder : o));
            setEditingOrderId(null);
            showToast(t('orders.messages.updated', { id: orderId }), 'success');
        } catch (error) {
            console.error('Error updating order status:', error);
            showToast(t('orders.messages.updateError'), 'error');
        }
    };

    const handleOrderDoubleClick = (order: Order) => {
        setSelectedOrder(order);
        setIsDetailsModalOpen(true);
    };

    const handleCloseDetailsModal = () => {
        setIsDetailsModalOpen(false);
        setSelectedOrder(null);
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
                (order.orderNumber && order.orderNumber.toLowerCase().includes(searchTerm.toLowerCase())) ||
                order.customerName.toLowerCase().includes(searchTerm.toLowerCase());

            const matchesStatus = statusFilter === 'All' || order.status === statusFilter;

            const matchesDate = !interval || isWithinInterval(parseISO(order.date), interval);

            return matchesSearch && matchesStatus && matchesDate;
        });
    }, [searchTerm, statusFilter, timeRange, orders]);

    return (
        <>
        <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-lg">
            <div className="p-6 border-b border-gray-200 dark:border-white/10">
                 <div className="flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">{t('orders.title')}</h2>
                        <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">{t('orders.description')}</p>
                    </div>
                    <button className="flex items-center gap-2 bg-secondary-light dark:bg-secondary-dark text-on-surface-light dark:text-on-surface-dark font-semibold py-2 px-4 rounded-lg border border-gray-300 dark:border-white/20 hover:bg-gray-100 dark:hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">
                        <DownloadIcon className="h-5 w-5" />
                        <span>{t('orders.export')}</span>
                    </button>
                </div>
                <div className="mt-6 flex flex-col gap-4">
                    <div className="flex flex-col sm:flex-row gap-4">
                        <input
                            type="text"
                            placeholder={t('orders.searchPlaceholder')}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="flex-1 bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary text-on-surface-light dark:text-on-surface-dark"
                        />
                        <select
                            aria-label={t('orders.filterByStatus')}
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value as OrderStatus | 'All')}
                            className="sm:w-48 bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-200 dark:border-white/10 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary appearance-none text-on-surface-light dark:text-on-surface-dark"
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
                    <div className="flex justify-center sm:justify-start">
                        <TimeRangeFilter selected={timeRange} onSelect={setTimeRange} />
                    </div>
                </div>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-left">
                    <thead className="bg-gray-100 dark:bg-white/5">
                        <tr className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                            <th className="py-3 px-6 font-semibold">{t('orders.headers.orderNumber')}</th>
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
                                <td colSpan={7} className="text-center py-12 text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                    {t('common.loading')}...
                                </td>
                            </tr>
                        ) : filteredOrders.length > 0 ? (
                            filteredOrders.map((order) => (
                                <tr 
                                    key={order.id} 
                                    className="border-b border-gray-200 dark:border-white/10 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors cursor-pointer"
                                    onDoubleClick={() => handleOrderDoubleClick(order)}
                                    title="Doble click para ver detalles"
                                >
                                    <td className="py-4 px-6 font-medium text-primary">{order.orderNumber || order.id}</td>
                                    <td className="py-4 px-6">{order.customerName}</td>
                                    <td className="py-4 px-6 text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">{format(parseISO(order.date), 'MMM d, yyyy, h:mm a', { locale: dateLocale })}</td>
                                    <td className="py-4 px-6 text-center">{order.items}</td>
                                    <td className="py-4 px-6">
                                        {editingOrderId === order.id ? (
                                            <select
                                                value={order.status}
                                                onChange={(e) => handleUpdateOrderStatus(order.id, e.target.value as OrderStatus)}
                                                onBlur={() => setEditingOrderId(null)}
                                                autoFocus
                                                className="bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-200 dark:border-white/10 rounded-lg py-1 px-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary appearance-none text-on-surface-light dark:text-on-surface-dark"
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
                                <td colSpan={7} className="text-center py-12 text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                    {t('orders.noOrders')}
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
             <div className="p-4 border-t border-gray-200 dark:border-white/10 text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark text-center">
                {t('orders.showingCount', { count: filteredOrders.length, total: orders.length })}
            </div>
        </div>
        
        <OrderDetailsModal
            isOpen={isDetailsModalOpen}
            onClose={handleCloseDetailsModal}
            order={selectedOrder}
        />
        </>
    );
};

export default Orders;