
import React from 'react';
import { ProductStatus } from '../types';
import { useTranslation } from 'react-i18next';

interface ProductStatusBadgeProps {
  status: ProductStatus;
}

export const ProductStatusBadge: React.FC<ProductStatusBadgeProps> = ({ status }) => {
  const { t } = useTranslation();
  const baseClasses = 'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold capitalize';

  const statusStyles: Record<ProductStatus, string> = {
    [ProductStatus.Active]: 'bg-green-500/20 text-green-400',
    [ProductStatus.Archived]: 'bg-gray-500/20 text-gray-400',
    [ProductStatus.OutOfStock]: 'bg-yellow-500/20 text-yellow-400',
  };

  const statusDotStyles: Record<ProductStatus, string> = {
    [ProductStatus.Active]: 'bg-green-400',
    [ProductStatus.Archived]: 'bg-gray-400',
    [ProductStatus.OutOfStock]: 'bg-yellow-400',
  };

  return (
    <span className={`${baseClasses} ${statusStyles[status]}`}>
        <span className={`w-2 h-2 mr-2 rounded-full ${statusDotStyles[status]}`}></span>
        {t(`productStatus.${status}`)}
    </span>
  );
};