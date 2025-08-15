import { Product, Order, OrderStatus, ProductStatus, Campaign, CampaignStatus, Discount, DiscountType, Client } from './types';

const today = new Date();
const subDays = (date: Date, days: number): Date => {
    const newDate = new Date(date);
    newDate.setDate(newDate.getDate() - days);
    return newDate;
};

export const mockProducts: Product[] = [
  { id: 'P001', name: 'QuantumGlow Laptop', category: 'Electronics', price: 1299.99, salePrice: 1199.99, stock: 75, imageUrl: 'https://picsum.photos/seed/P001/400/400', status: ProductStatus.Active },
  { id: 'P002', name: 'AetherSound Headphones', category: 'Audio', price: 199.99, salePrice: 179.99, stock: 250, imageUrl: 'https://picsum.photos/seed/P002/400/400', status: ProductStatus.Active },
  { id: 'P003', name: 'NovaSmart Watch', category: 'Wearables', price: 249.50, stock: 0, imageUrl: 'https://picsum.photos/seed/P003/400/400', status: ProductStatus.OutOfStock },
  { id: 'P004', name: 'ErgoFlow Mechanical Keyboard', category: 'Peripherals', price: 159.00, stock: 90, imageUrl: 'https://picsum.photos/seed/P004/400/400', status: ProductStatus.Active },
  { id: 'P005', name: 'FlexiGrip Gaming Mouse', category: 'Peripherals', price: 89.99, salePrice: 79.99, stock: 300, imageUrl: 'https://picsum.photos/seed/P005/400/400', status: ProductStatus.Active },
  { id: 'P006', name: '4K UltraView Monitor', category: 'Displays', price: 499.00, stock: 60, imageUrl: 'https://picsum.photos/seed/P006/400/400', status: ProductStatus.Archived },
  { id: 'P007', name: 'Portable PowerCore+', category: 'Accessories', price: 59.99, stock: 500, imageUrl: 'https://picsum.photos/seed/P007/400/400', status: ProductStatus.Active },
];

export const mockOrders: Order[] = [
  { id: 'ORD-24001', customerName: 'Alice Johnson', date: subDays(today, 1).toISOString(), total: 249.50, status: OrderStatus.Delivered, items: 1 },
  { id: 'ORD-24002', customerName: 'Bob Williams', date: subDays(today, 1).toISOString(), total: 1379.98, status: OrderStatus.Shipped, items: 2 },
  { id: 'ORD-24003', customerName: 'Charlie Brown', date: subDays(today, 2).toISOString(), total: 179.99, status: OrderStatus.Pending, items: 1 },
  { id: 'ORD-24004', customerName: 'Diana Prince', date: subDays(today, 6).toISOString(), total: 159.00, status: OrderStatus.Cancelled, items: 1 },
  { id: 'ORD-24005', customerName: 'Ethan Hunt', date: subDays(today, 8).toISOString(), total: 558.99, status: OrderStatus.Pending, items: 2 },
  { id: 'ORD-24006', customerName: 'Fiona Glenanne', date: subDays(today, 15).toISOString(), total: 79.99, status: OrderStatus.Delivered, items: 1 },
  { id: 'ORD-24007', customerName: 'George Costanza', date: subDays(today, 28).toISOString(), total: 1199.99, status: OrderStatus.Shipped, items: 1 },
  { id: 'ORD-24008', customerName: 'Hannah Abbott', date: subDays(today, 40).toISOString(), total: 499.00, status: OrderStatus.Pending, items: 1 },
  { id: 'ORD-24009', customerName: 'Alice Johnson', date: subDays(today, 65).toISOString(), total: 89.99, status: OrderStatus.Delivered, items: 1 },
  { id: 'ORD-24010', customerName: 'Diana Prince', date: subDays(today, 90).toISOString(), total: 320.00, status: OrderStatus.Delivered, items: 2 },
  { id: 'ORD-24011', customerName: 'Charlie Brown', date: subDays(today, 123).toISOString(), total: 450.50, status: OrderStatus.Shipped, items: 3 },
  { id: 'ORD-24012', customerName: 'Ethan Hunt', date: subDays(today, 150).toISOString(), total: 199.99, status: OrderStatus.Delivered, items: 1 },
  { id: 'ORD-24013', customerName: 'Bob Williams', date: subDays(today, 180).toISOString(), total: 1500.00, status: OrderStatus.Shipped, items: 1 },
  { id: 'ORD-24014', customerName: 'Fiona Glenanne', date: subDays(today, 210).toISOString(), total: 75.00, status: OrderStatus.Delivered, items: 1 },
  { id: 'ORD-24015', customerName: 'George Costanza', date: subDays(today, 250).toISOString(), total: 600.00, status: OrderStatus.Cancelled, items: 2 },
  { id: 'ORD-24016', customerName: 'Hannah Abbott', date: subDays(today, 300).toISOString(), total: 1299.99, status: OrderStatus.Shipped, items: 1 },
  { id: 'ORD-24017', customerName: 'Alice Johnson', date: subDays(today, 340).toISOString(), total: 250.00, status: OrderStatus.Delivered, items: 1 },
  { id: 'ORD-24018', customerName: 'Bob Williams', date: subDays(today, 360).toISOString(), total: 88.00, status: OrderStatus.Delivered, items: 2 },
];

export const mockSalesData = []; // No longer used, will be calculated dynamically

export const mockCampaigns: Campaign[] = [
  { id: 'CAMP-01', name: 'Summer Sale 2024', startDate: '2024-06-01', endDate: '2024-08-31', status: CampaignStatus.Active, budget: 5000, clicks: 12500, conversions: 450, imageUrl: 'https://picsum.photos/seed/CAMP-01/400/400', productIds: ['P001', 'P002'] },
  { id: 'CAMP-02', name: 'Black Friday Deals', startDate: '2024-11-20', endDate: '2024-11-30', status: CampaignStatus.Paused, budget: 15000, clicks: 0, conversions: 0, imageUrl: 'https://picsum.photos/seed/CAMP-02/400/400', productIds: ['P001', 'P002', 'P005', 'P007'] },
  { id: 'CAMP-03', name: 'New Year Kick-off', startDate: '2024-01-01', endDate: '2024-01-31', status: CampaignStatus.Completed, budget: 3000, clicks: 8500, conversions: 210, imageUrl: 'https://picsum.photos/seed/CAMP-03/400/400', productIds: [] },
  { id: 'CAMP-04', name: 'Spring Refresh', startDate: '2024-03-15', endDate: '2024-04-15', status: CampaignStatus.Completed, budget: 2500, clicks: 6800, conversions: 180, imageUrl: 'https://picsum.photos/seed/CAMP-04/400/400', productIds: ['P005'] },
];

export const mockDiscounts: Discount[] = [
    { id: 'D001', name: '10% Off Electronics', type: DiscountType.Percentage, value: 10, target: 'Category', category: 'Electronics', isActive: true },
    { id: 'D002', name: 'Summer Audio Sale', type: DiscountType.FixedAmount, value: 20, target: 'Category', category: 'Audio', isActive: true },
    { id: 'D003', name: '5% Off Everything', type: DiscountType.Percentage, value: 5, target: 'All', isActive: true },
    { id: 'D004', name: 'Laptop Special', type: DiscountType.FixedAmount, value: 150, target: 'Product', productId: 'P001', isActive: true },
    { id: 'D005', name: 'Archive Sale', type: DiscountType.Percentage, value: 50, target: 'All', isActive: false },
];

export const mockClients: Client[] = [
  { id: 'C001', name: 'Alice Johnson', email: 'alice.j@example.com', phone: '123-456-7890', joinDate: subDays(today, 2).toISOString(), totalSpent: 2450.75, avatarUrl: 'https://i.pravatar.cc/150?u=C001' },
  { id: 'C002', name: 'Bob Williams', email: 'bob.w@example.com', phone: '234-567-8901', joinDate: subDays(today, 8).toISOString(), totalSpent: 1890.50, avatarUrl: 'https://i.pravatar.cc/150?u=C002' },
  { id: 'C003', name: 'Charlie Brown', email: 'charlie.b@example.com', phone: '345-678-9012', joinDate: subDays(today, 15).toISOString(), totalSpent: 3200.00, avatarUrl: 'https://i.pravatar.cc/150?u=C003' },
  { id: 'C004', name: 'Diana Prince', email: 'diana.p@example.com', phone: '456-789-0123', joinDate: subDays(today, 25).toISOString(), totalSpent: 850.20, avatarUrl: 'https://i.pravatar.cc/150?u=C004' },
  { id: 'C005', name: 'Ethan Hunt', email: 'ethan.h@example.com', phone: '567-890-1234', joinDate: subDays(today, 35).toISOString(), totalSpent: 5300.90, avatarUrl: 'https://i.pravatar.cc/150?u=C005' },
  { id: 'C006', name: 'Fiona Glenanne', email: 'fiona.g@example.com', phone: '678-901-2345', joinDate: subDays(today, 50).toISOString(), totalSpent: 750.00, avatarUrl: 'https://i.pravatar.cc/150?u=C006' },
  { id: 'C007', name: 'George Costanza', email: 'george.c@example.com', phone: '789-012-3456', joinDate: subDays(today, 100).toISOString(), totalSpent: 1250.00, avatarUrl: 'https://i.pravatar.cc/150?u=C007' },
  { id: 'C008', name: 'Hannah Abbott', email: 'hannah.a@example.com', phone: '890-123-4567', joinDate: subDays(today, 200).toISOString(), totalSpent: 980.00, avatarUrl: 'https://i.pravatar.cc/150?u=C008' },
];