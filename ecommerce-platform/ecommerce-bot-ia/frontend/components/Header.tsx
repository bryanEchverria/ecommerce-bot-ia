
import React from 'react';
import { useLocation } from 'react-router-dom';
import { MenuIcon } from './Icons';
import { useTranslation } from 'react-i18next';
import { useTheme } from './ThemeContext';
import { useAuth } from '../auth/AuthContext';

const LanguageSwitcher: React.FC = () => {
    const { i18n } = useTranslation();

    const changeLanguage = (lng: 'en' | 'es') => {
        i18n.changeLanguage(lng);
    };

    return (
        <div className="flex items-center bg-background-light dark:bg-background-dark rounded-lg p-1">
            <button
                onClick={() => changeLanguage('en')}
                className={`px-3 py-1 text-sm font-semibold rounded-md transition-colors ${i18n.language.startsWith('en') ? 'bg-primary text-white' : 'text-on-surface-secondary-light dark:text-on-surface-secondary-dark hover:bg-surface-light dark:hover:bg-surface-dark'}`}
            >
                EN
            </button>
            <button
                onClick={() => changeLanguage('es')}
                className={`px-3 py-1 text-sm font-semibold rounded-md transition-colors ${i18n.language.startsWith('es') ? 'bg-primary text-white' : 'text-on-surface-secondary-light dark:text-on-surface-secondary-dark hover:bg-surface-light dark:hover:bg-surface-dark'}`}
            >
                ES
            </button>
        </div>
    );
};

const ThemeToggle: React.FC = () => {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            onClick={toggleTheme}
            className="flex items-center justify-center p-2 rounded-lg bg-background-light dark:bg-background-dark border border-gray-300 dark:border-gray-600 hover:bg-surface-light dark:hover:bg-surface-dark transition-colors"
            title={theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
        >
            {theme === 'dark' ? (
                // Sol (modo claro)
                <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                </svg>
            ) : (
                // Luna (modo oscuro)
                <svg className="w-5 h-5 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
            )}
        </button>
    );
};

const UserMenu: React.FC = () => {
  const { user, client, logout } = useAuth();
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <div className="relative">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="h-10 w-10 rounded-full border-2 border-primary bg-primary text-white hover:bg-primary/90 transition-colors flex items-center justify-center"
      >
        <span className="text-sm font-medium">
          {user?.email?.charAt(0).toUpperCase()}
        </span>
      </button>
      
      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-64 bg-surface-light dark:bg-surface-dark rounded-lg shadow-lg border border-gray-200 dark:border-white/10 z-20">
            <div className="p-4 border-b border-gray-200 dark:border-white/10">
              <p className="text-sm font-medium text-on-surface-light dark:text-on-surface-dark">
                {user?.email}
              </p>
              <p className="text-xs text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
                {client?.name} ({user?.role})
              </p>
            </div>
            <div className="p-2">
              <button
                onClick={() => {
                  logout();
                  setIsOpen(false);
                }}
                className="w-full text-left px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
              >
                Cerrar Sesión
              </button>
            </div>
          </div>
        </>
      )}
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
    <header className="flex-shrink-0 bg-surface-light dark:bg-surface-dark border-b border-gray-200 dark:border-white/10 px-6 md:px-8 py-4 flex items-center justify-between">
      <div className="flex items-center">
        <button className="md:hidden mr-4 text-on-surface-secondary-light dark:text-on-surface-secondary-dark">
          <MenuIcon className="h-6 w-6" />
        </button>
        <h2 className="text-xl font-semibold text-on-surface-light dark:text-on-surface-dark">{title}</h2>
      </div>
      <div className="flex items-center gap-4">
        <div className="relative">
          <input
            type="search"
            placeholder={t('common.search')}
            className="hidden lg:block bg-background-light dark:bg-background-dark border border-gray-300 dark:border-white/10 rounded-lg py-2 px-4 w-64 focus:outline-none focus:ring-2 focus:ring-primary text-on-surface-light dark:text-on-surface-dark"
          />
        </div>
        <LanguageSwitcher />
        <ThemeToggle />
        <UserMenu />
      </div>
    </header>
  );
};

export default Header;