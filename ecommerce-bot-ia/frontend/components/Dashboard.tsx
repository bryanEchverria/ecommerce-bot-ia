
import React, { useState, useMemo, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Order } from '../types';
import { format, subDays, startOfDay, endOfDay, isWithinInterval, eachDayOfInterval, parseISO, startOfYesterday, endOfYesterday, compareAsc, eachMonthOfInterval, startOfMonth, endOfMonth } from 'date-fns';
import { es, enUS } from 'date-fns/locale';
import { useTranslation } from 'react-i18next';
import { DollarSignIcon, ShoppingCartIcon, PackageIcon, UsersIcon } from './Icons';
import { OrderStatusBadge } from './OrderStatusBadge';
import { useCurrency, formatCurrency } from './CurrencyContext';

interface StatCardProps {
    title: string;
    value: string;
    icon: React.ReactNode;
    change?: string;
    changeColor: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, change, changeColor }) => (
    <div className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl shadow-lg flex items-start justify-between">
        <div>
            <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark font-medium">{title}</p>
            <p className="text-3xl font-bold text-on-surface-light dark:text-on-surface-dark mt-1">{value}</p>
            {change && <p className={`text-xs ${changeColor} mt-2 font-semibold`}>{change}</p>}
        </div>
        <div className="bg-primary/20 p-3 rounded-lg">
            {icon}
        </div>
    </div>
);


const RecentOrdersTable: React.FC<{ orders: Order[] }> = ({ orders }) => {
    const { t, i18n } = useTranslation();
    const { currency } = useCurrency();
    const dateLocale = i18n.language.startsWith('es') ? es : enUS;

    return (
        <div className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl shadow-lg h-full">
            <h3 className="text-lg font-semibold text-on-surface-light dark:text-on-surface-dark mb-4">{t('dashboard.recentOrders.title')}</h3>
            <div className="overflow-x-auto">
                <table className="w-full text-left">
                    <thead>
                        <tr className="border-b border-gray-200 dark:border-white/10 text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                            <th className="py-3 px-4 font-semibold">{t('dashboard.recentOrders.headers.orderNumber')}</th>
                            <th className="py-3 px-4 font-semibold">{t('dashboard.recentOrders.headers.customer')}</th>
                            <th className="py-3 px-4 font-semibold">{t('dashboard.recentOrders.headers.date')}</th>
                            <th className="py-3 px-4 font-semibold">{t('dashboard.recentOrders.headers.status')}</th>
                            <th className="py-3 px-4 font-semibold text-right">{t('dashboard.recentOrders.headers.total')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {orders
                            .sort((a, b) => {
                                // Priorizar órdenes con orderNumber
                                if (a.orderNumber && !b.orderNumber) return -1;
                                if (!a.orderNumber && b.orderNumber) return 1;
                                // Si ambas tienen o no tienen orderNumber, ordenar por fecha (más reciente primero)
                                return new Date(b.date).getTime() - new Date(a.date).getTime();
                            })
                            .slice(0, 5).map(order => (
                            <tr key={order.id} className="border-b border-gray-200 dark:border-white/10 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">
                                <td className="py-3 px-4 text-sm font-medium text-primary">{order.orderNumber || order.id}</td>
                                <td className="py-3 px-4 text-sm">{order.customerName}</td>
                                <td className="py-3 px-4 text-sm">{format(parseISO(order.date), 'MMM d, yyyy', { locale: dateLocale })}</td>
                                <td className="py-3 px-4"><OrderStatusBadge status={order.status} /></td>
                                <td className="py-3 px-4 text-sm font-semibold text-right">{formatCurrency(order.total, currency, i18n.language)}</td>
                            </tr>
                        ))}
                         {orders.length === 0 && (
                            <tr>
                                <td colSpan={5} className="text-center py-12 text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                                    {t('dashboard.recentOrders.noOrders')}
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

type TimeRange = 'today' | '7d' | '30d' | '1y';

const TimeRangeFilter: React.FC<{ selected: TimeRange, onSelect: (range: TimeRange) => void }> = ({ selected, onSelect }) => {
    const { t } = useTranslation();
    const ranges: { key: TimeRange; label: string }[] = [
        { key: 'today', label: t('dashboard.timeFilters.today') },
        { key: '7d', label: t('dashboard.timeFilters.7d') },
        { key: '30d', label: t('dashboard.timeFilters.30d') },
        { key: '1y', label: t('dashboard.timeFilters.1y') },
    ];

    return (
        <div className="flex bg-surface-light dark:bg-surface-dark rounded-lg p-1 space-x-1">
            {ranges.map(({ key, label }) => (
                <button
                    key={key}
                    onClick={() => onSelect(key)}
                    className={`px-4 py-1.5 rounded-md text-sm font-semibold transition-colors focus:outline-none ${
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


const Dashboard: React.FC = () => {
    console.log('Dashboard component rendering...');
    const { t, i18n } = useTranslation();
    const { currency } = useCurrency();
    const [timeRange, setTimeRange] = useState<TimeRange>('30d');
    const dateLocale = i18n.language.startsWith('es') ? es : enUS;
    const [orders, setOrders] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    // Load data from API - copy exact working code from Orders component
    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                console.log('Dashboard: Making fetch call to flow-orders...');
                const response = await fetch('/api/flow-orders/');
                console.log('Dashboard: Response received:', response.status);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                const data = await response.json();
                console.log('Dashboard: Data received:', data);
                const ordersData = data.pedidos || [];
                
                // Transform data exactly like Orders component
                const transformedOrders = ordersData.map(o => ({
                    id: o.id,
                    orderNumber: o.code,
                    customerName: o.customer_name,
                    date: o.created_at || o.date,
                    items: o.items || 1,
                    status: o.status,
                    total: typeof o.total === 'string' ? parseFloat(o.total) : o.total
                }));
                
                setOrders(transformedOrders);
            } catch (error) {
                console.error('Error loading orders data:', error);
                setOrders([]);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    const dashboardData = useMemo(() => {
        console.log('Dashboard: useMemo triggered with orders:', orders);
        const now = new Date();
        let currentPeriodStart, currentPeriodEnd;
        let previousPeriodStart, previousPeriodEnd;

        switch (timeRange) {
            case 'today':
                currentPeriodStart = startOfDay(now);
                currentPeriodEnd = endOfDay(now);
                previousPeriodStart = startOfYesterday();
                previousPeriodEnd = endOfYesterday();
                break;
            case '7d':
                currentPeriodStart = startOfDay(subDays(now, 6));
                currentPeriodEnd = endOfDay(now);
                previousPeriodStart = startOfDay(subDays(now, 13));
                previousPeriodEnd = endOfDay(subDays(now, 7));
                break;
            case '1y':
                currentPeriodStart = startOfDay(subDays(now, 364));
                currentPeriodEnd = endOfDay(now);
                previousPeriodStart = startOfDay(subDays(now, 729));
                previousPeriodEnd = endOfDay(subDays(now, 365));
                break;
            case '30d':
            default:
                currentPeriodStart = startOfDay(subDays(now, 29));
                currentPeriodEnd = endOfDay(now);
                previousPeriodStart = startOfDay(subDays(now, 59));
                previousPeriodEnd = endOfDay(subDays(now, 30));
                break;
        }

        const currentInterval = { start: currentPeriodStart, end: currentPeriodEnd };
        const previousInterval = { start: previousPeriodStart, end: previousPeriodEnd };

        const currentOrders = orders.filter(o => {
            try {
                const orderDate = parseISO(o.date);
                return isWithinInterval(orderDate, currentInterval);
            } catch (e) {
                console.error('Error parsing date for order', o.id, ':', o.date, e);
                return false;
            }
        });
        const previousOrders = orders.filter(o => {
            try {
                const orderDate = parseISO(o.date);
                return isWithinInterval(orderDate, previousInterval);
            } catch (e) {
                console.error('Error parsing date for order', o.id, ':', o.date, e);
                return false;
            }
        });

        // In multi-tenant, we track customers from orders, not separate client data
        const currentCustomers = new Set(currentOrders.map(o => o.customerName)).size;
        const previousCustomers = new Set(previousOrders.map(o => o.customerName)).size;

        const totalRevenue = currentOrders.reduce((sum, order) => sum + (order.status !== 'Cancelled' ? order.total : 0), 0);
        const salesCount = currentOrders.filter(o => o.status !== 'Cancelled').length;
        const newCustomers = currentCustomers;
        const newOrders = currentOrders.length;

        const prevTotalRevenue = previousOrders.reduce((sum, order) => sum + (order.status !== 'Cancelled' ? order.total : 0), 0);
        const prevSalesCount = previousOrders.filter(o => o.status !== 'Cancelled').length;
        const prevNewCustomers = previousCustomers;
        const prevNewOrders = previousOrders.length;

        const getChange = (current: number, previous: number) => {
            if (previous === 0) return current > 0 ? Infinity : 0;
            if (current === previous) return 0;
            return ((current - previous) / previous) * 100;
        };

        const revenueChange = getChange(totalRevenue, prevTotalRevenue);
        const salesChange = getChange(salesCount, prevSalesCount);
        const customersChange = getChange(newCustomers, prevNewCustomers);
        const ordersChange = getChange(newOrders, prevNewOrders);

        let salesTrendData;
        if (timeRange === '1y') {
            const monthsInInterval = eachMonthOfInterval(currentInterval);
            salesTrendData = monthsInInterval.map(month => {
                const salesForMonth = currentOrders
                    .filter(order => {
                        const orderDate = parseISO(order.date);
                        return order.status !== 'Cancelled' &&
                               isWithinInterval(orderDate, { start: startOfMonth(month), end: endOfMonth(month) });
                    })
                    .reduce((sum, order) => sum + order.total, 0);
                return { name: format(month, 'MMM', { locale: dateLocale }), sales: salesForMonth };
            });
        } else if (timeRange === 'today') {
            const hours = Array.from({length: 24}, (_, i) => i); // 0-23
            salesTrendData = hours.map(hour => {
                const salesForHour = currentOrders
                    .filter(order => parseISO(order.date).getHours() === hour && order.status !== 'Cancelled')
                    .reduce((sum, order) => sum + order.total, 0);
                return { name: format(new Date(0,0,0,hour), 'ha').toLowerCase(), sales: salesForHour };
            });
        } else { // 7d and 30d
            const daysInInterval = eachDayOfInterval(currentInterval);
            salesTrendData = daysInInterval.map(day => {
                const salesForDay = currentOrders
                    .filter(order => format(parseISO(order.date), 'yyyy-MM-dd') === format(day, 'yyyy-MM-dd') && order.status !== 'Cancelled')
                    .reduce((sum, order) => sum + order.total, 0);
                return { name: format(day, 'MMM d', { locale: dateLocale }), sales: salesForDay };
            });
        }


        const sortedOrders = currentOrders.sort((a, b) => compareAsc(parseISO(b.date), parseISO(a.date)));

        return {
            totalRevenue,
            salesCount,
            newOrders,
            newCustomers,
            revenueChange,
            salesChange,
            ordersChange,
            customersChange,
            salesTrendData,
            recentOrders: sortedOrders,
        };
    }, [timeRange, i18n.language, orders]);

    const formatChange = (change: number) => {
        if (!isFinite(change)) return '+100.0%';
        const sign = change > 0 ? '+' : '';
        return `${sign}${change.toFixed(1)}%`;
    }
    
    const getChangeColor = (change: number) => {
        if (change > 0) return 'text-green-400';
        if (change < 0) return 'text-red-400';
        return 'text-on-surface-secondary-light dark:text-on-surface-secondary-dark';
    }

    const getChangePeriodLabel = () => {
        return t(`dashboard.changeLabels.${timeRange}`);
    }
    
    const yAxisTickFormatter = (value: number) => {
        const language = i18n.language;
        if (value === 0) return formatCurrency(0, currency, language);
        
        const absValue = Math.abs(value);
        const symbol = new Intl.NumberFormat(language, { style: 'currency', currency: currency, minimumFractionDigits: 0, maximumFractionDigits: 0 }).formatToParts(0).find(p => p.type === 'currency')?.value || '';
        
        if (timeRange === 'today') {
           return formatCurrency(value, currency, language).replace(/\.00$/, '');
        }
        
        if (absValue < 1000) return formatCurrency(value, currency, language).replace(/\.00$/, '');
        
        return `${symbol}${new Intl.NumberFormat(language).format(Math.round(value/1000))}k`;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-lg text-on-surface-secondary-light dark:text-on-surface-secondary-dark">Loading dashboard...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-start">
                <TimeRangeFilter selected={timeRange} onSelect={setTimeRange} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard 
                    title={t('dashboard.cards.totalRevenue')}
                    value={formatCurrency(dashboardData.totalRevenue, currency, i18n.language)} 
                    icon={<DollarSignIcon className="h-6 w-6 text-primary" />} 
                    change={`${formatChange(dashboardData.revenueChange)} ${getChangePeriodLabel()}`}
                    changeColor={getChangeColor(dashboardData.revenueChange)}
                />
                <StatCard 
                    title={t('dashboard.cards.sales')}
                    value={dashboardData.salesCount.toLocaleString(i18n.language)} 
                    icon={<ShoppingCartIcon className="h-6 w-6 text-primary" />} 
                    change={`${formatChange(dashboardData.salesChange)} ${getChangePeriodLabel()}`}
                    changeColor={getChangeColor(dashboardData.salesChange)}
                />
                <StatCard 
                    title={t('dashboard.cards.newOrders')}
                    value={dashboardData.newOrders.toLocaleString(i18n.language)} 
                    icon={<PackageIcon className="h-6 w-6 text-primary" />} 
                    change={`${formatChange(dashboardData.ordersChange)} ${getChangePeriodLabel()}`}
                    changeColor={getChangeColor(dashboardData.ordersChange)}
                />
                <StatCard 
                    title={t('dashboard.cards.newCustomers')} 
                    value={dashboardData.newCustomers.toLocaleString(i18n.language)} 
                    icon={<UsersIcon className="h-6 w-6 text-primary" />} 
                    change={`${formatChange(dashboardData.customersChange)} ${getChangePeriodLabel()}`}
                    changeColor={getChangeColor(dashboardData.customersChange)}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
                <div className="lg:col-span-3 bg-surface-light dark:bg-surface-dark p-6 rounded-xl shadow-lg">
                    <h3 className="text-lg font-semibold text-on-surface-light dark:text-on-surface-dark mb-4">{t('dashboard.salesTrend.title')}</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={dashboardData.salesTrendData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
                                <XAxis dataKey="name" tick={{ fill: '#9ca3af' }} fontSize={12} />
                                <YAxis tick={{ fill: '#9ca3af' }} fontSize={12} axisLine={{ stroke: '#4b5563' }} tickFormatter={yAxisTickFormatter} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1f2937',
                                        borderColor: '#374151',
                                        color: '#f9fafb',
                                    }}
                                    cursor={{ fill: 'rgba(79, 70, 229, 0.1)' }}
                                    formatter={(value: number) => [formatCurrency(value, currency, i18n.language), t('dashboard.cards.sales')]}
                                />
                                <Legend wrapperStyle={{ color: '#9ca3af' }} formatter={() => t('dashboard.cards.sales')} />
                                <Line type="monotone" dataKey="sales" stroke="#4f46e5" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 8 }} name={t('dashboard.cards.sales')} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
                <div className="lg:col-span-2">
                     <RecentOrdersTable orders={dashboardData.recentOrders} />
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
