
import React from 'react';
import { useTranslation } from 'react-i18next';

interface DiscountStatusBadgeProps {
  isActive: boolean;
}

export const DiscountStatusBadge: React.FC<DiscountStatusBadgeProps> = ({ isActive }) => {
  const { t } = useTranslation();
  const baseClasses = 'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold capitalize';
  
  const statusText = isActive ? t('discountStatus.active') : t('discountStatus.inactive');
  const statusColor = isActive ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400';
  const dotColor = isActive ? 'bg-green-400' : 'bg-gray-400';

  return (
    <span className={`${baseClasses} ${statusColor}`}>
        <span className={`w-2 h-2 mr-2 rounded-full ${dotColor}`}></span>
        {statusText}
    </span>
  );
};