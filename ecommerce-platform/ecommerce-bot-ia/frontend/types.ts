
export enum ProductStatus {
  Active = 'Active',
  Archived = 'Archived',
  OutOfStock = 'Out of Stock'
}

export interface Product {
  id: string;
  name: string;
  description?: string;
  category: string;
  price: number;
  salePrice?: number;
  stock: number;
  widthCm?: number;
  heightCm?: number;
  imageUrl: string;
  status: ProductStatus;
}

export enum OrderStatus {
  Pending = 'Pending',
  Received = 'Received',
  Shipping = 'Shipping',
  Delivered = 'Delivered',
  Cancelled = 'Cancelled'
}

export interface Order {
  id: string;
  orderNumber?: string;
  customerName: string;
  date: string;
  total: number;
  status: OrderStatus;
  items: number;
}

export interface SalesData {
  name: string;
  sales: number;
}

export enum CampaignStatus {
  Active = 'Active',
  Paused = 'Paused',
  Completed = 'Completed',
}

export interface Campaign {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  status: CampaignStatus;
  budget: number;
  clicks: number;
  conversions: number;
  imageUrl: string;
  productIds: string[];
}

export enum DiscountType {
  Percentage = 'Percentage',
  FixedAmount = 'Fixed Amount',
}

export interface Discount {
  id: string;
  name: string;
  type: DiscountType;
  value: number;
  target: 'All' | 'Category' | 'Product';
  category?: string;
  productId?: string;
  isActive: boolean;
}

export interface Client {
  id: string;
  name: string;
  email: string;
  phone: string;
  joinDate: string;
  totalSpent: number;
  avatarUrl: string;
}
