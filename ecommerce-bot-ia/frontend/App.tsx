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
import TwilioSettings from './components/TwilioSettings';
import PaymentMethods from './components/PaymentMethods';
import Login from './components/Login';
import ProtectedRoute from './components/ProtectedRoute';
import { CurrencyProvider } from './components/CurrencyContext';
import { ThemeProvider } from './components/ThemeContext';
import { ToastProvider } from './components/Toast';
import { DiscountsProvider } from './components/DiscountsContext';
import { AuthProvider, useAuth } from './auth/AuthContext';

const AppContent: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-background-light dark:bg-background-dark">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
          <p className="mt-4 text-on-surface-light dark:text-on-surface-dark">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <MemoryRouter>
      <div className="flex h-screen bg-background-light dark:bg-background-dark text-on-surface-light dark:text-on-surface-dark">
        <Sidebar />
        <main className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <div className="flex-1 p-6 md:p-8 overflow-y-auto">
            <Routes>
              <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/products" element={<ProtectedRoute><Products /></ProtectedRoute>} />
              <Route path="/orders" element={<ProtectedRoute><Orders /></ProtectedRoute>} />
              <Route path="/clients" element={<ProtectedRoute><Clients /></ProtectedRoute>} />
              <Route path="/campaigns" element={<ProtectedRoute><Campaigns /></ProtectedRoute>} />
              <Route path="/discounts" element={<ProtectedRoute><Discounts /></ProtectedRoute>} />
              <Route path="/whatsapp-settings" element={<ProtectedRoute><WhatsAppSettings /></ProtectedRoute>} />
              <Route path="/twilio-settings" element={<ProtectedRoute><TwilioSettings /></ProtectedRoute>} />
              <Route path="/payment-methods" element={<ProtectedRoute><PaymentMethods /></ProtectedRoute>} />
            </Routes>
          </div>
        </main>
      </div>
    </MemoryRouter>
  );
};

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <CurrencyProvider>
          <ToastProvider>
            <DiscountsProvider>
              <AppContent />
            </DiscountsProvider>
          </ToastProvider>
        </CurrencyProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;