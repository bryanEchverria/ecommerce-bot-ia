import React from 'react';
import { format, parseISO } from 'date-fns';
import { es, enUS } from 'date-fns/locale';
import { Order } from '../types';
import { XIcon, UserIcon, CalendarIcon, HashtagIcon, PackageIcon } from './Icons';
import { OrderStatusBadge } from './OrderStatusBadge';
import { useTranslation } from 'react-i18next';
import { useCurrency, formatCurrency } from './CurrencyContext';

interface OrderDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  order: Order | null;
}

const OrderDetailsModal: React.FC<OrderDetailsModalProps> = ({ isOpen, onClose, order }) => {
  const { t, i18n } = useTranslation();
  const { currency } = useCurrency();
  const dateLocale = i18n.language.startsWith('es') ? es : enUS;

  if (!isOpen || !order) return null;

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex justify-center items-center p-4" aria-modal="true" role="dialog">
      <div className="bg-surface-light dark:bg-surface-dark rounded-xl shadow-2xl w-full max-w-2xl animate-fade-in-up max-h-[90vh] overflow-y-auto">
        
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-white/10 flex justify-between items-center">
          <div>
            <h3 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">
              Detalles del Pedido
            </h3>
            <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark mt-1">
              {order.orderNumber || order.id}
            </p>
          </div>
          <button 
            type="button" 
            onClick={onClose} 
            className="text-on-surface-secondary-light dark:text-on-surface-secondary-dark hover:text-on-surface-light dark:hover:text-on-surface-dark transition-colors p-2 rounded-full hover:bg-gray-100 dark:hover:bg-white/10"
          >
            <XIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          
          {/* Order Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Left Column */}
            <div className="space-y-4">
              
              {/* Order Number */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <HashtagIcon className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                    Número de Pedido
                  </p>
                  <p className="font-semibold text-on-surface-light dark:text-on-surface-dark">
                    {order.orderNumber || order.id}
                  </p>
                </div>
              </div>

              {/* Customer */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
                  <UserIcon className="h-5 w-5 text-blue-500" />
                </div>
                <div>
                  <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                    Cliente
                  </p>
                  <p className="font-semibold text-on-surface-light dark:text-on-surface-dark">
                    {order.customerName}
                  </p>
                </div>
              </div>

              {/* Date */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center">
                  <CalendarIcon className="h-5 w-5 text-green-500" />
                </div>
                <div>
                  <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                    Fecha del Pedido
                  </p>
                  <p className="font-semibold text-on-surface-light dark:text-on-surface-dark">
                    {format(parseISO(order.date), 'PPP, p', { locale: dateLocale })}
                  </p>
                </div>
              </div>

            </div>

            {/* Right Column */}
            <div className="space-y-4">
              
              {/* Status */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-orange-500/10 rounded-lg flex items-center justify-center">
                  <PackageIcon className="h-5 w-5 text-orange-500" />
                </div>
                <div>
                  <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                    Estado
                  </p>
                  <OrderStatusBadge status={order.status} />
                </div>
              </div>

              {/* Items Count */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center">
                  <span className="text-sm font-bold text-purple-500">#</span>
                </div>
                <div>
                  <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                    Cantidad de Artículos
                  </p>
                  <p className="font-semibold text-on-surface-light dark:text-on-surface-dark">
                    {order.items} {order.items === 1 ? 'artículo' : 'artículos'}
                  </p>
                </div>
              </div>

              {/* Total */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center">
                  <span className="text-sm font-bold text-green-500">$</span>
                </div>
                <div>
                  <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                    Total del Pedido
                  </p>
                  <p className="text-xl font-bold text-green-500">
                    {formatCurrency(order.total, currency, i18n.language)}
                  </p>
                </div>
              </div>

            </div>
          </div>

          {/* Order Timeline */}
          <div className="border-t border-gray-200 dark:border-white/10 pt-6">
            <h4 className="text-lg font-semibold text-on-surface-light dark:text-on-surface-dark mb-4">
              Información Adicional
            </h4>
            
            <div className="bg-gray-50 dark:bg-white/5 rounded-lg p-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                  ID del Pedido:
                </span>
                <span className="text-sm font-mono text-on-surface-light dark:text-on-surface-dark">
                  {order.id}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                  Creado:
                </span>
                <span className="text-sm text-on-surface-light dark:text-on-surface-dark">
                  {format(parseISO(order.date), 'PPP', { locale: dateLocale })}
                </span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                  Valor promedio por artículo:
                </span>
                <span className="text-sm font-semibold text-on-surface-light dark:text-on-surface-dark">
                  {formatCurrency(order.total / order.items, currency, i18n.language)}
                </span>
              </div>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="p-6 bg-secondary-light dark:bg-secondary-dark/50 rounded-b-xl border-t border-gray-200 dark:border-white/10">
          <div className="flex justify-end gap-4">
            <button 
              type="button" 
              onClick={onClose} 
              className="bg-surface-light dark:bg-surface-dark text-on-surface-light dark:text-on-surface-dark font-semibold py-2 px-4 rounded-lg border border-gray-300 dark:border-white/20 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
            >
              Cerrar
            </button>
            <button 
              type="button" 
              className="bg-primary text-white font-semibold py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors"
            >
              Editar Pedido
            </button>
          </div>
        </div>

      </div>
      
      {/* Animation Styles */}
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

export default OrderDetailsModal;