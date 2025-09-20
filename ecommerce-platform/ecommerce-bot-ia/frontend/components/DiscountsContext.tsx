import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Discount, DiscountType } from '../types';
import { discountsApi } from '../services/tenant-api';

interface DiscountsContextType {
  discounts: Discount[];
  loading: boolean;
  refreshDiscounts: () => Promise<void>;
  updateDiscount: (discount: Discount) => void;
  removeDiscount: (discountId: string) => void;
  addDiscount: (discount: Discount) => void;
}

const DiscountsContext = createContext<DiscountsContextType | undefined>(undefined);

export const useDiscounts = () => {
  const context = useContext(DiscountsContext);
  if (!context) {
    throw new Error('useDiscounts must be used within a DiscountsProvider');
  }
  return context;
};

interface DiscountsProviderProps {
  children: ReactNode;
}

export const DiscountsProvider: React.FC<DiscountsProviderProps> = ({ children }) => {
  const [discounts, setDiscounts] = useState<Discount[]>([]);
  const [loading, setLoading] = useState(true);

  const refreshDiscounts = async () => {
    try {
      setLoading(true);
      const discountsData = await discountsApi.getAll();
      
      const transformedDiscounts = discountsData.map(d => ({
        id: d.id,
        name: d.name,
        type: d.type === 'Percentage' ? DiscountType.Percentage : DiscountType.FixedAmount,
        value: d.value,
        target: d.target,
        category: d.category,
        productId: d.product_id,
        isActive: d.is_active
      }));
      
      setDiscounts(transformedDiscounts);
    } catch (error) {
      console.error('Error loading discounts:', error);
      setDiscounts([]);
    } finally {
      setLoading(false);
    }
  };

  const updateDiscount = (updatedDiscount: Discount) => {
    setDiscounts(discounts.map(d => d.id === updatedDiscount.id ? updatedDiscount : d));
  };

  const removeDiscount = (discountId: string) => {
    setDiscounts(discounts.filter(d => d.id !== discountId));
  };

  const addDiscount = (newDiscount: Discount) => {
    setDiscounts([newDiscount, ...discounts]);
  };

  useEffect(() => {
    refreshDiscounts();
  }, []);

  const value: DiscountsContextType = {
    discounts,
    loading,
    refreshDiscounts,
    updateDiscount,
    removeDiscount,
    addDiscount,
  };

  return (
    <DiscountsContext.Provider value={value}>
      {children}
    </DiscountsContext.Provider>
  );
};