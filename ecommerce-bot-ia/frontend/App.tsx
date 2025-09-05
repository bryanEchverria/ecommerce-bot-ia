import React from 'react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Products from './components/Products';
import Orders from './components/Orders';
import Header from './components/Header';
import Campaigns from './components/Campaigns';
import Discounts from './components/Discounts';
import Clients from './components/Clients';
import WhatsAppSettings from './components/WhatsAppSettings';
import { CurrencyProvider } from './components/CurrencyContext';
import { ThemeProvider } from './components/ThemeContext';
import { ToastProvider } from './components/Toast';
import { DiscountsProvider } from './components/DiscountsContext';
import { AuthProvider } from './auth/AuthContext';

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <CurrencyProvider>
          <ToastProvider>
            <DiscountsProvider>
              <MemoryRouter>
                <div className="flex h-screen bg-background-light dark:bg-background-dark text-on-surface-light dark:text-on-surface-dark">
                <Sidebar />
                <main className="flex-1 flex flex-col overflow-hidden">
                  <Header />
                  <div className="flex-1 p-6 md:p-8 overflow-y-auto">
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/products" element={<Products />} />
                      <Route path="/orders" element={<Orders />} />
                      <Route path="/clients" element={<Clients />} />
                      <Route path="/campaigns" element={<Campaigns />} />
                      <Route path="/discounts" element={<Discounts />} />
                      <Route path="/whatsapp-settings" element={<WhatsAppSettings />} />
                    </Routes>
                  </div>
                </main>
              </div>
            </MemoryRouter>
          </DiscountsProvider>
        </ToastProvider>
      </CurrencyProvider>
    </AuthProvider>
    </ThemeProvider>
  );
};

export default App;