
import React from 'react';
import { CampaignStatus } from '../types';
import { useTranslation } from 'react-i18next';

interface CampaignStatusBadgeProps {
  status: CampaignStatus;
}

export const CampaignStatusBadge: React.FC<CampaignStatusBadgeProps> = ({ status }) => {
  const { t } = useTranslation();
  const baseClasses = 'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold capitalize';

  const statusStyles: Record<CampaignStatus, string> = {
    [CampaignStatus.Active]: 'bg-green-500/20 text-green-400',
    [CampaignStatus.Paused]: 'bg-yellow-500/20 text-yellow-400',
    [CampaignStatus.Completed]: 'bg-gray-500/20 text-gray-400',
  };

  const statusDotStyles: Record<CampaignStatus, string> = {
    [CampaignStatus.Active]: 'bg-green-400',
    [CampaignStatus.Paused]: 'bg-yellow-400',
    [CampaignStatus.Completed]: 'bg-gray-400',
  };

  return (
    <span className={`${baseClasses} ${statusStyles[status]}`}>
        <span className={`w-2 h-2 mr-2 rounded-full ${statusDotStyles[status]}`}></span>
        {t(`campaignStatus.${status}`)}
    </span>
  );
};