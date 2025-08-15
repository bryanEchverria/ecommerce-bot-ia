
import React from 'react';
import { useLocation } from 'react-router-dom';
import { MenuIcon } from './Icons';
import { useTranslation } from 'react-i18next';
import { useCurrency, Currency } from './CurrencyContext';

const LanguageSwitcher: React.FC = () => {
    const { i18n } = useTranslation();

    const changeLanguage = (lng: 'en' | 'es') => {
        i18n.changeLanguage(lng);
    };

    return (
        <div className="flex items-center bg-background rounded-lg p-1">
            <button
                onClick={() => changeLanguage('en')}
                className={`px-3 py-1 text-sm font-semibold rounded-md transition-colors ${i18n.language.startsWith('en') ? 'bg-primary text-white' : 'text-on-surface-secondary hover:bg-surface'}`}
            >
                EN
            </button>
            <button
                onClick={() => changeLanguage('es')}
                className={`px-3 py-1 text-sm font-semibold rounded-md transition-colors ${i18n.language.startsWith('es') ? 'bg-primary text-white' : 'text-on-surface-secondary hover:bg-surface'}`}
            >
                ES
            </button>
        </div>
    );
};

const CurrencySwitcher: React.FC = () => {
    const { currency, setCurrency } = useCurrency();
    const currencies: Currency[] = ['USD', 'CLP'];

    return (
        <div className="flex items-center bg-background rounded-lg p-1">
            {currencies.map((c) => (
                <button
                    key={c}
                    onClick={() => setCurrency(c)}
                    className={`px-3 py-1 text-sm font-semibold rounded-md transition-colors ${currency === c ? 'bg-primary text-white' : 'text-on-surface-secondary hover:bg-surface'}`}
                >
                    {c}
                </button>
            ))}
        </div>
    );
};


const Header: React.FC = () => {
  const { t } = useTranslation();
  const location = useLocation();

  const getTitle = () => {
    const path = location.pathname;
    if (path === '/') return t('header.titles.dashboard');
    if (path.startsWith('/products')) return t('header.titles.products');
    if (path.startsWith('/orders')) return t('header.titles.orders');
    if (path.startsWith('/clients')) return t('header.titles.clients');
    if (path.startsWith('/campaigns')) return t('header.titles.campaigns');
    if (path.startsWith('/discounts')) return t('header.titles.discounts');
    return t('header.titles.default');
  };

  const title = getTitle();

  return (
    <header className="flex-shrink-0 bg-surface border-b border-white/10 px-6 md:px-8 py-4 flex items-center justify-between">
      <div className="flex items-center">
        <button className="md:hidden mr-4 text-on-surface-secondary">
          <MenuIcon className="h-6 w-6" />
        </button>
        <h2 className="text-xl font-semibold text-on-surface">{title}</h2>
      </div>
      <div className="flex items-center gap-4">
        <div className="relative">
          <input
            type="search"
            placeholder={t('common.search')}
            className="hidden lg:block bg-background border border-white/10 rounded-lg py-2 px-4 w-64 focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <LanguageSwitcher />
        <CurrencySwitcher />
        <img
          src="https://i.pravatar.cc/150?u=a042581f4e29026704d"
          alt="User avatar"
          className="h-10 w-10 rounded-full border-2 border-primary"
        />
      </div>
    </header>
  );
};

export default Header;