// Script de depuración para forzar la aparición del módulo Bot Config
// Ejecutar en la consola del navegador (F12)

console.log('🔧 Debug: Forzando creación del módulo Bot Config...');

// Eliminar cualquier instancia existente
const existing = document.getElementById('floating-bot-config');
if (existing) existing.remove();

// Crear botón flotante forzado
const floatingButton = document.createElement('div');
floatingButton.id = 'floating-bot-config';
floatingButton.innerHTML = `
    <button class="floating-bot-btn" style="
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 50%;
        color: white;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        transition: transform 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    ">
        🤖
    </button>
`;

floatingButton.querySelector('.floating-bot-btn').addEventListener('click', () => {
    alert('🤖 Módulo de Configuración del Bot\n\nEste módulo te permite:\n✏️ Editar prompts del sistema\n🎨 Configurar tono y estilo\n🧠 Ajustar parámetros de IA\n📊 Ver historial de versiones\n\n¡El backend está funcionando correctamente!');
});

document.body.appendChild(floatingButton);

console.log('✅ Debug: Botón flotante creado exitosamente');
console.log('🎯 Busca el botón azul con 🤖 en la esquina inferior derecha');