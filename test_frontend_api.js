// Test script para verificar que el frontend pueda conectarse al backend
console.log("Testing frontend-backend connection...");

// Simular la llamada que hace el frontend
fetch('http://127.0.0.1:8002/api/orders', {
    method: 'GET',
    mode: 'cors',
    headers: {
        'Content-Type': 'application/json',
    }
})
.then(response => {
    console.log('Response status:', response.status);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
})
.then(orders => {
    console.log('✅ Connection successful!');
    console.log(`📦 Found ${orders.length} orders:`);
    
    orders.slice(0, 3).forEach((order, index) => {
        console.log(`${index + 1}. ${order.customer_name} - $${order.total} - ${order.status}`);
    });
    
    if (orders.length > 3) {
        console.log(`... and ${orders.length - 3} more orders`);
    }
})
.catch(error => {
    console.error('❌ Connection failed:', error.message);
});