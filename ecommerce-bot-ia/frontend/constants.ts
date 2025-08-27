import { Product, Order, Campaign, Discount, Client } from './types';

export const mockProducts: Product[] = [
  // No mock data - products will be loaded from API
];

export const mockOrders: Order[] = [
  // No mock data - orders will be loaded from tenant-aware API
];

export const mockSalesData = []; // No longer used, will be calculated dynamically

export const mockCampaigns: Campaign[] = [
  // No mock data - campaigns will be loaded from API
];

export const mockDiscounts: Discount[] = [
  // No mock data - discounts will be loaded from API
];

export const mockClients: Client[] = [
  // No mock data - in multi-tenant system, client data comes from auth context
];