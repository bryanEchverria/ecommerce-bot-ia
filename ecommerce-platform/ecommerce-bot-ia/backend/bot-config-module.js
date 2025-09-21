// Módulo de Configuración del Bot - Inyección al Frontend
(function() {
    'use strict';
    
    // Esperar a que la página esté cargada
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initBotConfigModule);
    } else {
        initBotConfigModule();
    }
    
    function initBotConfigModule() {
        console.log('🤖 Inicializando módulo de Configuración del Bot...');
        
        // Esperar a que el menú lateral esté disponible
        setTimeout(() => {
            addBotConfigToMenu();
            createBotConfigPage();
        }, 2000);
    }
    
    function addBotConfigToMenu() {
        // Buscar el menú lateral
        const sidebar = document.querySelector('nav, .sidebar, [role="navigation"]') || 
                       document.querySelector('div[class*="sidebar"]') ||
                       document.querySelector('div[class*="nav"]');
        
        if (!sidebar) {
            console.log('❌ No se encontró menú lateral, intentando de nuevo...');
            setTimeout(addBotConfigToMenu, 1000);
            return;
        }
        
        // Verificar si ya existe el enlace
        if (document.getElementById('bot-config-menu-item')) {
            return;
        }
        
        // Crear enlace del menú
        const menuItem = document.createElement('div');
        menuItem.id = 'bot-config-menu-item';
        menuItem.className = 'menu-item bot-config-menu';
        menuItem.innerHTML = `
            <a href="#/bot-config" class="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700 transition-colors">
                <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                <span>Configuración del Bot</span>
            </a>
        `;
        
        // Agregar event listener
        menuItem.addEventListener('click', (e) => {
            e.preventDefault();
            showBotConfigPage();
        });
        
        // Insertar en el menú
        const menuList = sidebar.querySelector('ul, .menu-list') || sidebar;
        if (menuList.children.length > 0) {
            // Insertar después del primer elemento del menú
            menuList.children[1].insertAdjacentElement('afterend', menuItem);
        } else {
            menuList.appendChild(menuItem);
        }
        
        console.log('✅ Módulo "Configuración del Bot" agregado al menú');
    }
    
    function createBotConfigPage() {
        // Verificar si ya existe la página
        if (document.getElementById('bot-config-page')) {
            return;
        }
        
        // Crear página de configuración del bot
        const page = document.createElement('div');
        page.id = 'bot-config-page';
        page.className = 'hidden fixed inset-0 bg-white dark:bg-gray-900 z-50 overflow-y-auto';
        page.innerHTML = `
            <div class="min-h-screen p-6">
                <div class="max-w-4xl mx-auto">
                    <!-- Header -->
                    <div class="flex items-center justify-between mb-6">
                        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
                            🤖 Configuración del Bot
                        </h1>
                        <button id="close-bot-config" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    
                    <!-- Estado de carga -->
                    <div id="bot-config-loading" class="text-center py-8">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                        <p class="mt-2 text-gray-600 dark:text-gray-400">Cargando configuración...</p>
                    </div>
                    
                    <!-- Contenido -->
                    <div id="bot-config-content" class="hidden">
                        <!-- Tabs -->
                        <div class="border-b border-gray-200 dark:border-gray-700 mb-6">
                            <nav class="-mb-px flex space-x-8">
                                <button class="bot-config-tab active border-b-2 border-blue-500 py-2 px-1 text-sm font-medium text-blue-600" data-tab="config">
                                    Configuración
                                </button>
                                <button class="bot-config-tab border-b-2 border-transparent py-2 px-1 text-sm font-medium text-gray-500 hover:text-gray-700" data-tab="versions">
                                    Historial
                                </button>
                                <button class="bot-config-tab border-b-2 border-transparent py-2 px-1 text-sm font-medium text-gray-500 hover:text-gray-700" data-tab="preview">
                                    Preview
                                </button>
                            </nav>
                        </div>
                        
                        <!-- Tab: Configuración -->
                        <div id="tab-config" class="bot-config-tab-content">
                            <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                                <h3 class="text-lg font-medium mb-4">Prompt del Sistema</h3>
                                <textarea id="system-prompt" rows="8" class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white" placeholder="Ingresa el prompt del sistema para el bot..."></textarea>
                                
                                <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <h4 class="text-md font-medium mb-2">Configuración de Estilo</h4>
                                        <div class="space-y-3">
                                            <div>
                                                <label class="block text-sm font-medium mb-1">Tono</label>
                                                <select id="tono" class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white">
                                                    <option value="amigable">Amigable</option>
                                                    <option value="profesional">Profesional</option>
                                                    <option value="profesional_amigable">Profesional y Amigable</option>
                                                    <option value="formal">Formal</option>
                                                </select>
                                            </div>
                                            <div class="flex items-center">
                                                <input type="checkbox" id="usar-emojis" class="mr-2">
                                                <label for="usar-emojis" class="text-sm">Usar emojis</label>
                                            </div>
                                            <div>
                                                <label class="block text-sm font-medium mb-1">Límite de caracteres</label>
                                                <input type="number" id="limite-caracteres" min="50" max="1000" value="300" class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white">
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div>
                                        <h4 class="text-md font-medium mb-2">Parámetros IA</h4>
                                        <div class="space-y-3">
                                            <div>
                                                <label class="block text-sm font-medium mb-1">Modelo</label>
                                                <select id="modelo" class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white">
                                                    <option value="gpt-4o-mini">GPT-4o Mini</option>
                                                    <option value="gpt-4o">GPT-4o</option>
                                                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label class="block text-sm font-medium mb-1">Temperature NLU</label>
                                                <input type="range" id="temp-nlu" min="0" max="1" step="0.1" value="0.3" class="w-full">
                                                <span id="temp-nlu-value" class="text-sm text-gray-600">0.3</span>
                                            </div>
                                            <div>
                                                <label class="block text-sm font-medium mb-1">Temperature NLG</label>
                                                <input type="range" id="temp-nlg" min="0" max="1" step="0.1" value="0.7" class="w-full">
                                                <span id="temp-nlg-value" class="text-sm text-gray-600">0.7</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mt-6 flex space-x-4">
                                    <button id="save-config" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md">
                                        Guardar Configuración
                                    </button>
                                    <button id="reset-config" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md">
                                        Restablecer
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Tab: Historial -->
                        <div id="tab-versions" class="bot-config-tab-content hidden">
                            <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                                <h3 class="text-lg font-medium mb-4">Historial de Versiones</h3>
                                <div id="versions-list" class="space-y-4">
                                    <!-- Se llenará dinámicamente -->
                                </div>
                            </div>
                        </div>
                        
                        <!-- Tab: Preview -->
                        <div id="tab-preview" class="bot-config-tab-content hidden">
                            <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                                <h3 class="text-lg font-medium mb-4">Probar Configuración</h3>
                                <div class="space-y-4">
                                    <div>
                                        <label class="block text-sm font-medium mb-1">Mensaje de prueba</label>
                                        <input type="text" id="test-message" placeholder="Ej: Hola, ¿qué productos tienes?" class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white">
                                    </div>
                                    <button id="test-bot" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md">
                                        Probar Bot
                                    </button>
                                    <div id="bot-response" class="hidden mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-md">
                                        <!-- Respuesta del bot aparecerá aquí -->
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(page);
        
        // Agregar event listeners
        setupBotConfigEventListeners();
    }
    
    function setupBotConfigEventListeners() {
        // Cerrar página
        document.getElementById('close-bot-config').addEventListener('click', hideBotConfigPage);
        
        // Tabs
        document.querySelectorAll('.bot-config-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                switchBotConfigTab(tabName);
            });
        });
        
        // Sliders
        const tempNluSlider = document.getElementById('temp-nlu');
        const tempNlgSlider = document.getElementById('temp-nlg');
        
        tempNluSlider.addEventListener('input', (e) => {
            document.getElementById('temp-nlu-value').textContent = e.target.value;
        });
        
        tempNlgSlider.addEventListener('input', (e) => {
            document.getElementById('temp-nlg-value').textContent = e.target.value;
        });
        
        // Guardar configuración
        document.getElementById('save-config').addEventListener('click', saveBotConfig);
        
        // Probar bot
        document.getElementById('test-bot').addEventListener('click', testBotConfig);
    }
    
    function showBotConfigPage() {
        const page = document.getElementById('bot-config-page');
        if (page) {
            page.classList.remove('hidden');
            loadBotConfig();
        }
    }
    
    function hideBotConfigPage() {
        const page = document.getElementById('bot-config-page');
        if (page) {
            page.classList.add('hidden');
        }
    }
    
    function switchBotConfigTab(tabName) {
        // Actualizar tabs
        document.querySelectorAll('.bot-config-tab').forEach(tab => {
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active', 'border-blue-500', 'text-blue-600');
                tab.classList.remove('border-transparent', 'text-gray-500');
            } else {
                tab.classList.remove('active', 'border-blue-500', 'text-blue-600');
                tab.classList.add('border-transparent', 'text-gray-500');
            }
        });
        
        // Mostrar contenido
        document.querySelectorAll('.bot-config-tab-content').forEach(content => {
            content.classList.add('hidden');
        });
        document.getElementById(\`tab-\${tabName}\`).classList.remove('hidden');
        
        // Cargar datos específicos
        if (tabName === 'versions') {
            loadVersionHistory();
        }
    }
    
    async function loadBotConfig() {
        const loading = document.getElementById('bot-config-loading');
        const content = document.getElementById('bot-config-content');
        
        try {
            const token = localStorage.getItem('auth_token') || '';
            const response = await fetch('/api/tenants/acme-cannabis-2024/prompt', {
                headers: {
                    'Authorization': \`Bearer \${token}\`
                }
            });
            
            if (response.ok) {
                const config = await response.json();
                populateConfigForm(config);
                loading.classList.add('hidden');
                content.classList.remove('hidden');
            } else {
                throw new Error('No se pudo cargar la configuración');
            }
        } catch (error) {
            console.error('Error cargando configuración:', error);
            loading.innerHTML = '<p class="text-red-500">Error cargando configuración</p>';
        }
    }
    
    function populateConfigForm(config) {
        document.getElementById('system-prompt').value = config.system_prompt || '';
        document.getElementById('tono').value = config.style_overrides?.tono || 'amigable';
        document.getElementById('usar-emojis').checked = config.style_overrides?.usar_emojis || false;
        document.getElementById('limite-caracteres').value = config.style_overrides?.limite_respuesta_caracteres || 300;
        document.getElementById('modelo').value = config.nlu_params?.modelo || 'gpt-4o-mini';
        document.getElementById('temp-nlu').value = config.nlu_params?.temperature_nlu || 0.3;
        document.getElementById('temp-nlg').value = config.nlg_params?.temperature_nlg || 0.7;
        
        // Actualizar displays
        document.getElementById('temp-nlu-value').textContent = config.nlu_params?.temperature_nlu || 0.3;
        document.getElementById('temp-nlg-value').textContent = config.nlg_params?.temperature_nlg || 0.7;
    }
    
    async function saveBotConfig() {
        const button = document.getElementById('save-config');
        const originalText = button.textContent;
        button.textContent = 'Guardando...';
        button.disabled = true;
        
        try {
            const token = localStorage.getItem('auth_token') || '';
            const config = {
                system_prompt: document.getElementById('system-prompt').value,
                style_overrides: {
                    tono: document.getElementById('tono').value,
                    usar_emojis: document.getElementById('usar-emojis').checked,
                    limite_respuesta_caracteres: parseInt(document.getElementById('limite-caracteres').value),
                    incluir_contexto_empresa: true
                },
                nlu_params: {
                    modelo: document.getElementById('modelo').value,
                    temperature_nlu: parseFloat(document.getElementById('temp-nlu').value),
                    max_tokens_nlu: 150
                },
                nlg_params: {
                    modelo: document.getElementById('modelo').value,
                    temperature_nlg: parseFloat(document.getElementById('temp-nlg').value),
                    max_tokens_nlg: 300
                }
            };
            
            const response = await fetch('/api/tenants/acme-cannabis-2024/prompt', {
                method: 'PUT',
                headers: {
                    'Authorization': \`Bearer \${token}\`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
            
            if (response.ok) {
                alert('✅ Configuración guardada exitosamente');
            } else {
                throw new Error('Error guardando configuración');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('❌ Error guardando configuración');
        }
        
        button.textContent = originalText;
        button.disabled = false;
    }
    
    async function testBotConfig() {
        const message = document.getElementById('test-message').value;
        if (!message.trim()) {
            alert('Por favor ingresa un mensaje de prueba');
            return;
        }
        
        const responseDiv = document.getElementById('bot-response');
        responseDiv.classList.remove('hidden');
        responseDiv.innerHTML = '<p class="text-gray-600">Generando respuesta...</p>';
        
        // Simular respuesta del bot
        setTimeout(() => {
            responseDiv.innerHTML = \`
                <h4 class="font-medium mb-2">Respuesta del Bot:</h4>
                <p class="text-gray-800 dark:text-gray-200">¡Hola! Soy tu asistente de ventas especializado en cannabis medicinal para ACME Cannabis Store. 🌱</p>
                <p class="text-sm text-gray-500 mt-2">Para probar con IA real, implementar endpoint de preview.</p>
            \`;
        }, 1000);
    }
    
    async function loadVersionHistory() {
        const versionsList = document.getElementById('versions-list');
        versionsList.innerHTML = '<p class="text-gray-600">Cargando historial...</p>';
        
        try {
            const token = localStorage.getItem('auth_token') || '';
            const response = await fetch('/api/tenants/acme-cannabis-2024/prompt/versions', {
                headers: {
                    'Authorization': \`Bearer \${token}\`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                displayVersionHistory(data);
            } else {
                throw new Error('Error cargando historial');
            }
        } catch (error) {
            versionsList.innerHTML = '<p class="text-red-500">Error cargando historial</p>';
        }
    }
    
    function displayVersionHistory(data) {
        const versionsList = document.getElementById('versions-list');
        
        if (data.versions.length === 0) {
            versionsList.innerHTML = '<p class="text-gray-600">No hay versiones disponibles</p>';
            return;
        }
        
        versionsList.innerHTML = data.versions.map(version => \`
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4 \${version.is_active ? 'bg-blue-50 dark:bg-blue-900' : ''}">
                <div class="flex items-center justify-between mb-2">
                    <h4 class="font-medium">Versión \${version.version} \${version.is_active ? '(Actual)' : ''}</h4>
                    <span class="text-sm text-gray-500">\${new Date(version.created_at).toLocaleDateString()}</span>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">\${version.system_prompt.substring(0, 100)}...</p>
                <div class="flex space-x-2">
                    <span class="inline-block bg-gray-200 dark:bg-gray-700 text-xs px-2 py-1 rounded">Tono: \${version.style_overrides?.tono || 'N/A'}</span>
                    <span class="inline-block bg-gray-200 dark:bg-gray-700 text-xs px-2 py-1 rounded">Modelo: \${version.nlu_params?.modelo || 'N/A'}</span>
                </div>
            </div>
        \`).join('');
    }
    
    console.log('🤖 Módulo de Configuración del Bot cargado');
})();