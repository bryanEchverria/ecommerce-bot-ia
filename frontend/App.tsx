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
import { CurrencyProvider } from './components/CurrencyContext';
import { ToastProvider } from './components/Toast';
import { DiscountsProvider } from './components/DiscountsContext';

const App: React.FC = () => {
  return (
    <CurrencyProvider>
      <ToastProvider>
        <DiscountsProvider>
          <MemoryRouter>
            <div className="flex h-screen bg-background text-on-surface">
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
                  </Routes>
                </div>
              </main>
            </div>
          </MemoryRouter>
        </DiscountsProvider>
      </ToastProvider>
    </CurrencyProvider>
  );
};

export default App;