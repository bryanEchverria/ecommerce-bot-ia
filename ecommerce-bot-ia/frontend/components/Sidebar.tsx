
import React from 'react';
import { useMatch, useNavigate } from 'react-router-dom';
import { HomeIcon, PackageIcon, ShoppingCartIcon, ZapIcon, MegaphoneIcon, PercentIcon, UsersIcon, WhatsAppIcon, PhoneIcon, CreditCardIcon } from './Icons';
import { useTranslation } from 'react-i18next';

const NavItem: React.FC<{ to: string; children: React.ReactNode; }> = ({ to, children }) => {
  const navigate = useNavigate();
  const match = useMatch({ path: to, end: true });
  const isActive = !!match;

  const activeClass = 'bg-primary/20 text-primary';
  const inactiveClass = 'text-on-surface-secondary-light dark:text-on-surface-secondary-dark hover:bg-surface-light dark:hover:bg-surface-dark hover:text-on-surface-light dark:hover:text-on-surface-dark';

  return (
    <button
      onClick={() => navigate(to)}
      className={`flex items-center w-full px-4 py-3 rounded-lg transition-colors duration-200 text-left ${isActive ? activeClass : inactiveClass}`}
      aria-current={isActive ? 'page' : undefined}
    >
      {children}
    </button>
  );
};

const Sidebar: React.FC = () => {
  const { t } = useTranslation();

  return (
    <aside className="w-64 flex-shrink-0 bg-secondary-light dark:bg-secondary-dark p-6 hidden md:flex flex-col justify-between">
      <div>
        <div className="flex items-center gap-3 mb-10 px-2">
          <div className="bg-primary p-2 rounded-lg">
            <ZapIcon className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-xl font-bold text-on-surface-light dark:text-on-surface-dark">{t('sidebar.title')}</h1>
        </div>
        <nav className="flex flex-col gap-3">
          <NavItem to="/">
            <HomeIcon className="h-5 w-5 mr-4" />
            <span>{t('sidebar.dashboard')}</span>
          </NavItem>
          <NavItem to="/products">
            <PackageIcon className="h-5 w-5 mr-4" />
            <span>{t('sidebar.products')}</span>
          </NavItem>
          <NavItem to="/orders">
            <ShoppingCartIcon className="h-5 w-5 mr-4" />
            <span>{t('sidebar.orders')}</span>
          </NavItem>
           <NavItem to="/clients">
            <UsersIcon className="h-5 w-5 mr-4" />
            <span>{t('sidebar.clients')}</span>
          </NavItem>
           <NavItem to="/campaigns">
            <MegaphoneIcon className="h-5 w-5 mr-4" />
            <span>{t('sidebar.campaigns')}</span>
          </NavItem>
          <NavItem to="/discounts">
            <PercentIcon className="h-5 w-5 mr-4" />
            <span>{t('sidebar.discounts')}</span>
          </NavItem>
          <NavItem to="/whatsapp-settings">
            <WhatsAppIcon className="h-5 w-5 mr-4" />
            <span>{t('sidebar.whatsappSettings')}</span>
          </NavItem>
          <NavItem to="/payment-methods">
            <CreditCardIcon className="h-5 w-5 mr-4" />
            <span>Métodos de Pago</span>
          </NavItem>
          <NavItem to="/twilio-settings">
            <PhoneIcon className="h-5 w-5 mr-4" />
            <span>Twilio</span>
          </NavItem>
        </nav>
      </div>
      <div className="px-4 py-3 rounded-lg bg-surface-light dark:bg-surface-dark text-center">
        <p className="text-sm text-on-surface-secondary-light dark:text-on-surface-secondary-dark">{t('sidebar.copyright')}</p>
        <p className="text-xs text-on-surface-secondary-light/70 dark:text-on-surface-secondary-dark/70">{t('sidebar.rightsReserved')}</p>
      </div>
    </aside>
  );
};

export default Sidebar;