import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

export interface ToastProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
  onClose: (id: string) => void;
}

export const Toast: React.FC<ToastProps> = ({ id, type, message, duration = 5000, onClose }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isLeaving, setIsLeaving] = useState(false);
  const [progress, setProgress] = useState(100);

  useEffect(() => {
    // Trigger enter animation
    const enterTimer = setTimeout(() => setIsVisible(true), 50);
    
    // Progress bar animation
    const progressTimer = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev - (100 / (duration / 100));
        return newProgress <= 0 ? 0 : newProgress;
      });
    }, 100);

    // Auto close timer
    const closeTimer = setTimeout(() => {
      setIsLeaving(true);
      setTimeout(() => onClose(id), 400);
    }, duration);

    return () => {
      clearTimeout(enterTimer);
      clearTimeout(closeTimer);
      clearInterval(progressTimer);
    };
  }, [id, duration, onClose]);

  const getIcon = () => {
    switch (type) {
      case 'success':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
          </svg>
        );
      case 'error':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      case 'warning':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        );
      case 'info':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const getColors = () => {
    switch (type) {
      case 'success':
        return {
          bg: 'bg-white dark:bg-gray-800',
          border: 'border-l-4 border-green-500',
          iconBg: 'bg-green-100 dark:bg-green-900',
          iconColor: 'text-green-600 dark:text-green-400',
          progressColor: 'bg-green-500',
          shadow: 'shadow-lg shadow-green-500/20'
        };
      case 'error':
        return {
          bg: 'bg-white dark:bg-gray-800',
          border: 'border-l-4 border-red-500',
          iconBg: 'bg-red-100 dark:bg-red-900',
          iconColor: 'text-red-600 dark:text-red-400',
          progressColor: 'bg-red-500',
          shadow: 'shadow-lg shadow-red-500/20'
        };
      case 'warning':
        return {
          bg: 'bg-white dark:bg-gray-800',
          border: 'border-l-4 border-amber-500',
          iconBg: 'bg-amber-100 dark:bg-amber-900',
          iconColor: 'text-amber-600 dark:text-amber-400',
          progressColor: 'bg-amber-500',
          shadow: 'shadow-lg shadow-amber-500/20'
        };
      case 'info':
        return {
          bg: 'bg-white dark:bg-gray-800',
          border: 'border-l-4 border-blue-500',
          iconBg: 'bg-blue-100 dark:bg-blue-900',
          iconColor: 'text-blue-600 dark:text-blue-400',
          progressColor: 'bg-blue-500',
          shadow: 'shadow-lg shadow-blue-500/20'
        };
    }
  };

  const colors = getColors();

  const handleClose = () => {
    setIsLeaving(true);
    setTimeout(() => onClose(id), 400);
  };

  return (
    <div
      className={`
        relative w-full max-w-sm p-4 ${colors.bg} ${colors.border} ${colors.shadow}
        rounded-lg backdrop-blur-sm border border-gray-200 dark:border-gray-700
        transform transition-all duration-400 ease-in-out
        ${isVisible && !isLeaving ? 'translate-x-0 opacity-100 scale-100' : 'translate-x-full opacity-0 scale-95'}
      `}
      role="alert"
    >
      {/* Progress bar */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gray-200 dark:bg-gray-700 rounded-t-lg overflow-hidden">
        <div
          className={`h-full ${colors.progressColor} transition-all duration-100 ease-linear`}
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="flex items-start">
        {/* Icon */}
        <div className={`flex-shrink-0 w-10 h-10 ${colors.iconBg} ${colors.iconColor} rounded-full flex items-center justify-center mr-3`}>
          {getIcon()}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 dark:text-gray-100 leading-5">
            {message}
          </p>
        </div>

        {/* Close button */}
        <button
          type="button"
          onClick={handleClose}
          className="flex-shrink-0 ml-3 inline-flex text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-300 dark:focus:ring-gray-600 rounded-lg p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
        >
          <span className="sr-only">Cerrar</span>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export interface ToastContextType {
  showToast: (message: string, type: ToastProps['type'], duration?: number) => void;
}

const ToastContext = React.createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastProps[]>([]);

  const showToast = (message: string, type: ToastProps['type'], duration?: number) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast: ToastProps = {
      id,
      message,
      type,
      duration,
      onClose: removeToast,
    };
    
    // Limit to max 5 toasts
    setToasts(prev => {
      const newToasts = [...prev, newToast];
      return newToasts.length > 5 ? newToasts.slice(-5) : newToasts;
    });
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      
      {/* Toast Container */}
      <div className="fixed top-4 right-4 z-[9999] pointer-events-none">
        <div className="flex flex-col gap-3 w-full max-w-sm">
          {toasts.map((toast, index) => (
            <div 
              key={toast.id} 
              className="pointer-events-auto"
              style={{
                zIndex: 9999 - index, // Stack toasts properly
              }}
            >
              <Toast {...toast} />
            </div>
          ))}
        </div>
      </div>
    </ToastContext.Provider>
  );
};