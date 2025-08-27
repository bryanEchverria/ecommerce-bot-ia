import React, { createContext, useState, useContext, ReactNode } from 'react';

// Define the currencies you want to support
export type Currency = 'CLP';

interface CurrencyContextType {
  currency: Currency;
  setCurrency: (currency: Currency) => void;
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

export const CurrencyProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currency, setCurrency] = useState<Currency>('CLP');

  const value = { currency, setCurrency };

  return (
    <CurrencyContext.Provider value={value}>
      {children}
    </CurrencyContext.Provider>
  );
};

export const useCurrency = (): CurrencyContextType => {
  const context = useContext(CurrencyContext);
  if (context === undefined) {
    throw new Error('useCurrency must be used within a CurrencyProvider');
  }
  return context;
};

/**
 * Formats a number as a currency string.
 * @param value The number to format.
 * @param currency The currency code (e.g., 'USD').
 * @param locale The locale string (e.g., 'en-US', 'es-ES').
 * @returns A formatted currency string.
 */
export const formatCurrency = (value: number, currency: Currency, locale: string) => {
  try {
    const options: Intl.NumberFormatOptions = {
      style: 'currency',
      currency: currency,
    };
    if (currency === 'CLP') {
      options.maximumFractionDigits = 0;
    }
    
    // For CLP, es-CL locale gives the best formatting ($1.234), otherwise it might show as CLP1,234
    const effectiveLocale = currency === 'CLP' ? 'es-CL' : locale;

    return new Intl.NumberFormat(effectiveLocale, options).format(value);
  } catch (error) {
    console.error("Error formatting currency:", error);
    // Fallback for unsupported locales/currencies
    if (currency === 'CLP') {
      return `CLP$ ${Math.round(value)}`;
    }
    return `${currency} ${value.toFixed(2)}`;
  }
};

/**
 * Gets the currency symbol for a given currency code.
 * @param currency The currency code.
 * @param locale The locale string.
 * @returns The currency symbol (e.g., '$').
 */
export const getCurrencySymbol = (currency: Currency, locale: string) => {
    try {
        // For CLP, es-CL locale gives the best formatting ($), otherwise it might show as CLP
        const effectiveLocale = currency === 'CLP' ? 'es-CL' : locale;
        const parts = new Intl.NumberFormat(effectiveLocale, { style: 'currency', currency: currency }).formatToParts(0);
        return parts.find(part => part.type === 'currency')?.value || '$';
    } catch (error) {
        console.error("Error getting currency symbol:", error);
        return '$';
    }
};
