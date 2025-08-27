
import React from 'react';
import { useTranslation } from 'react-i18next';
import { OrderStatus } from '../types';

interface OrderStatusBadgeProps {
  status: OrderStatus;
}

export const OrderStatusBadge: React.FC<OrderStatusBadgeProps> = ({ status }) => {
  const { t } = useTranslation();
  const baseClasses = 'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold capitalize';

  const statusStyles: Record<OrderStatus, string> = {
    [OrderStatus.Pending]: 'bg-yellow-500/20 text-yellow-400',
    [OrderStatus.Received]: 'bg-blue-500/20 text-blue-400',
    [OrderStatus.Shipping]: 'bg-purple-500/20 text-purple-400',
    [OrderStatus.Delivered]: 'bg-green-500/20 text-green-400',
    [OrderStatus.Cancelled]: 'bg-red-500/20 text-red-400',
  };

  const statusDotStyles: Record<OrderStatus, string> = {
    [OrderStatus.Pending]: 'bg-yellow-400',
    [OrderStatus.Received]: 'bg-blue-400',
    [OrderStatus.Shipping]: 'bg-purple-400',
    [OrderStatus.Delivered]: 'bg-green-400',
    [OrderStatus.Cancelled]: 'bg-red-400',
  };

  return (
    <span className={`${baseClasses} ${statusStyles[status]}`}>
        <span className={`w-2 h-2 mr-2 rounded-full ${statusDotStyles[status]}`}></span>
        {t(`orderStatus.${status}`)}
    </span>
  );
};