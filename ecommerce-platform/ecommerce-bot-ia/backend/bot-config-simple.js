// Módulo de Configuración del Bot - Versión Simple y Robusta
(function() {
    'use strict';
    
    console.log('🤖 Iniciando módulo de Configuración del Bot...');
    
    // Función para esperar a que un elemento aparezca en el DOM
    function waitForElement(selector, callback, maxAttempts = 50) {
        let attempts = 0;
        const interval = setInterval(() => {
            const element = document.querySelector(selector);
            attempts++;
            
            if (element) {
                clearInterval(interval);
                callback(element);
            } else if (attempts >= maxAttempts) {
                clearInterval(interval);
                console.log('❌ No se encontró el elemento:', selector);
                // Intentar con selectores alternativos
                tryAlternativeSelectors(callback);
            }
        }, 200);
    }
    
    function tryAlternativeSelectors(callback) {
        // Intentar diferentes selectores comunes para menús laterales
        const selectors = [
            'nav[role="navigation"]',
            '.sidebar',
            '[class*="sidebar"]',
            '[class*="nav"]',
            'aside',
            'nav',
            '[class*="menu"]',
            '#root nav',
            '#root aside',
            'div[class*="flex"] nav'
        ];
        
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element) {
                console.log('✅ Encontrado menú con selector:', selector);
                callback(element);
                return;
            }
        }
        
        // Si no encontramos nada, crear el botón flotante
        createFloatingButton();
    }
    
    function createFloatingButton() {
        console.log('📌 Creando botón flotante para configuración del bot...');
        
        // Verificar si ya existe
        if (document.getElementById('floating-bot-config')) {
            return;
        }
        
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
                z-index: 1000;
                transition: transform 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            " onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
                🤖
            </button>
            <div class="floating-tooltip" style="
                position: fixed;
                bottom: 90px;
                right: 20px;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                white-space: nowrap;
                z-index: 1001;
                opacity: 0;
                transition: opacity 0.2s ease;
                pointer-events: none;
            ">
                Configuración del Bot
            </div>
        `;
        
        // Agregar eventos
        const button = floatingButton.querySelector('.floating-bot-btn');
        const tooltip = floatingButton.querySelector('.floating-tooltip');
        
        button.addEventListener('click', showBotConfigModal);
        button.addEventListener('mouseenter', () => {
            tooltip.style.opacity = '1';
        });
        button.addEventListener('mouseleave', () => {
            tooltip.style.opacity = '0';
        });
        
        document.body.appendChild(floatingButton);
        console.log('✅ Botón flotante creado');
    }
    
    function addBotConfigToMenu(menuElement) {
        console.log('➕ Agregando opción al menú encontrado:', menuElement);
        
        // Verificar si ya existe
        if (document.getElementById('bot-config-menu-item')) {
            console.log('ℹ️ El ítem del menú ya existe');
            return;
        }
        
        // Crear el elemento del menú
        const menuItem = document.createElement('div');
        menuItem.id = 'bot-config-menu-item';
        menuItem.style.cssText = `
            padding: 12px 16px;
            margin: 4px 8px;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.2s ease;
            display: flex;
            align-items: center;
            gap: 12px;
            color: #374151;
            text-decoration: none;
        `;
        
        menuItem.innerHTML = `
            <span style="font-size: 20px;">🤖</span>
            <span style="font-weight: 500;">Configuración del Bot</span>
        `;
        
        // Eventos de hover
        menuItem.addEventListener('mouseenter', () => {
            menuItem.style.backgroundColor = '#f3f4f6';
        });
        menuItem.addEventListener('mouseleave', () => {
            menuItem.style.backgroundColor = 'transparent';
        });
        menuItem.addEventListener('click', showBotConfigModal);
        
        // Intentar diferentes estrategias para insertar
        if (menuElement.tagName === 'UL' || menuElement.classList.contains('menu-list')) {
            const li = document.createElement('li');
            li.appendChild(menuItem);
            menuElement.appendChild(li);
        } else if (menuElement.children.length > 0) {
            // Insertar después del primer elemento
            menuElement.insertBefore(menuItem, menuElement.children[1] || null);
        } else {
            menuElement.appendChild(menuItem);
        }
        
        console.log('✅ Opción agregada al menú');
    }
    
    function showBotConfigModal() {
        console.log('🚀 Abriendo configuración del bot...');
        
        // Verificar si ya existe el modal
        let modal = document.getElementById('bot-config-modal');
        if (!modal) {
            createBotConfigModal();
            modal = document.getElementById('bot-config-modal');
        }
        
        modal.style.display = 'flex';
        loadCurrentBotConfig();
    }
    
    function createBotConfigModal() {
        const modal = document.createElement('div');
        modal.id = 'bot-config-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;
        
        modal.innerHTML = `
            <div class="modal-content" style="
                background: white;
                border-radius: 12px;
                padding: 24px;
                width: 90%;
                max-width: 800px;
                max-height: 80%;
                overflow-y: auto;
                box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
            ">
                <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2 style="font-size: 24px; font-weight: bold; color: #1f2937; margin: 0;">
                        🤖 Configuración del Bot
                    </h2>
                    <button id="close-modal" style="
                        background: none;
                        border: none;
                        font-size: 24px;
                        cursor: pointer;
                        color: #6b7280;
                        padding: 4px;
                    ">×</button>
                </div>
                
                <div id="bot-config-content">
                    <div class="config-section" style="margin-bottom: 24px;">
                        <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px; color: #374151;">
                            Prompt del Sistema
                        </h3>
                        <textarea id="system-prompt" rows="6" style="
                            width: 100%;
                            padding: 12px;
                            border: 2px solid #e5e7eb;
                            border-radius: 8px;
                            font-family: inherit;
                            font-size: 14px;
                            resize: vertical;
                        " placeholder="Ingresa el prompt del sistema para el bot..."></textarea>
                    </div>
                    
                    <div class="config-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px;">
                        <div class="config-column">
                            <h4 style="font-size: 16px; font-weight: 600; margin-bottom: 12px; color: #374151;">
                                Configuración de Estilo
                            </h4>
                            <div style="space-y: 12px;">
                                <div style="margin-bottom: 12px;">
                                    <label style="display: block; font-weight: 500; margin-bottom: 4px;">Tono</label>
                                    <select id="tono" style="
                                        width: 100%;
                                        padding: 8px 12px;
                                        border: 2px solid #e5e7eb;
                                        border-radius: 6px;
                                        background: white;
                                    ">
                                        <option value="amigable">Amigable</option>
                                        <option value="profesional">Profesional</option>
                                        <option value="profesional_amigable">Profesional y Amigable</option>
                                        <option value="formal">Formal</option>
                                    </select>
                                </div>
                                <div style="margin-bottom: 12px;">
                                    <label style="display: flex; align-items: center; gap: 8px;">
                                        <input type="checkbox" id="usar-emojis">
                                        <span>Usar emojis</span>
                                    </label>
                                </div>
                                <div style="margin-bottom: 12px;">
                                    <label style="display: block; font-weight: 500; margin-bottom: 4px;">Límite de caracteres</label>
                                    <input type="number" id="limite-caracteres" min="50" max="1000" value="300" style="
                                        width: 100%;
                                        padding: 8px 12px;
                                        border: 2px solid #e5e7eb;
                                        border-radius: 6px;
                                    ">
                                </div>
                            </div>
                        </div>
                        
                        <div class="config-column">
                            <h4 style="font-size: 16px; font-weight: 600; margin-bottom: 12px; color: #374151;">
                                Parámetros de IA
                            </h4>
                            <div style="space-y: 12px;">
                                <div style="margin-bottom: 12px;">
                                    <label style="display: block; font-weight: 500; margin-bottom: 4px;">Modelo</label>
                                    <select id="modelo" style="
                                        width: 100%;
                                        padding: 8px 12px;
                                        border: 2px solid #e5e7eb;
                                        border-radius: 6px;
                                        background: white;
                                    ">
                                        <option value="gpt-4o-mini">GPT-4o Mini</option>
                                        <option value="gpt-4o">GPT-4o</option>
                                        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                    </select>
                                </div>
                                <div style="margin-bottom: 12px;">
                                    <label style="display: block; font-weight: 500; margin-bottom: 4px;">
                                        Temperature NLU: <span id="temp-nlu-value">0.3</span>
                                    </label>
                                    <input type="range" id="temp-nlu" min="0" max="1" step="0.1" value="0.3" style="width: 100%;">
                                </div>
                                <div style="margin-bottom: 12px;">
                                    <label style="display: block; font-weight: 500; margin-bottom: 4px;">
                                        Temperature NLG: <span id="temp-nlg-value">0.7</span>
                                    </label>
                                    <input type="range" id="temp-nlg" min="0" max="1" step="0.1" value="0.7" style="width: 100%;">
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="current-config" style="
                        background: #f9fafb;
                        border: 1px solid #e5e7eb;
                        border-radius: 8px;
                        padding: 16px;
                        margin-bottom: 24px;
                    ">
                        <h4 style="font-size: 14px; font-weight: 600; margin-bottom: 8px; color: #374151;">
                            Configuración Actual
                        </h4>
                        <div id="current-config-info" style="font-size: 12px; color: #6b7280;">
                            Cargando...
                        </div>
                    </div>
                    
                    <div class="modal-actions" style="display: flex; gap: 12px; justify-content: flex-end;">
                        <button id="cancel-config" style="
                            padding: 10px 20px;
                            border: 2px solid #e5e7eb;
                            border-radius: 6px;
                            background: white;
                            color: #374151;
                            cursor: pointer;
                            font-weight: 500;
                        ">Cancelar</button>
                        <button id="save-config" style="
                            padding: 10px 20px;
                            border: none;
                            border-radius: 6px;
                            background: #3b82f6;
                            color: white;
                            cursor: pointer;
                            font-weight: 500;
                        ">Guardar Configuración</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Event listeners
        document.getElementById('close-modal').addEventListener('click', closeBotConfigModal);
        document.getElementById('cancel-config').addEventListener('click', closeBotConfigModal);
        document.getElementById('save-config').addEventListener('click', saveBotConfiguration);
        
        // Sliders
        document.getElementById('temp-nlu').addEventListener('input', (e) => {
            document.getElementById('temp-nlu-value').textContent = e.target.value;
        });
        document.getElementById('temp-nlg').addEventListener('input', (e) => {
            document.getElementById('temp-nlg-value').textContent = e.target.value;
        });
        
        // Cerrar al hacer click fuera del modal
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeBotConfigModal();
            }
        });
        
        console.log('✅ Modal de configuración creado');
    }
    
    function closeBotConfigModal() {
        const modal = document.getElementById('bot-config-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    async function loadCurrentBotConfig() {
        const infoDiv = document.getElementById('current-config-info');
        
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
                infoDiv.innerHTML = \`
                    <strong>Versión:</strong> \${config.version} | 
                    <strong>Actualizado:</strong> \${new Date(config.updated_at).toLocaleDateString()} |
                    <strong>Estado:</strong> \${config.is_active ? 'Activo' : 'Inactivo'}
                \`;
            } else if (response.status === 404) {
                infoDiv.innerHTML = '<span style="color: #f59e0b;">⚠️ No hay configuración. Se creará una nueva al guardar.</span>';
                setDefaultValues();
            } else {
                throw new Error('Error cargando configuración');
            }
        } catch (error) {
            console.error('Error:', error);
            infoDiv.innerHTML = '<span style="color: #ef4444;">❌ Error cargando configuración</span>';
            setDefaultValues();
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
    
    function setDefaultValues() {
        document.getElementById('system-prompt').value = 'Eres un asistente de ventas especializado para ACME Cannabis Store. Ayuda a los clientes con información sobre productos, recomendaciones personalizadas y orientación profesional.';
        document.getElementById('tono').value = 'profesional_amigable';
        document.getElementById('usar-emojis').checked = true;
        document.getElementById('limite-caracteres').value = 300;
        document.getElementById('modelo').value = 'gpt-4o-mini';
        document.getElementById('temp-nlu').value = 0.3;
        document.getElementById('temp-nlg').value = 0.7;
        document.getElementById('temp-nlu-value').textContent = '0.3';
        document.getElementById('temp-nlg-value').textContent = '0.7';
    }
    
    async function saveBotConfiguration() {
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
            
            // Intentar PUT primero, luego POST si no existe
            let response = await fetch('/api/tenants/acme-cannabis-2024/prompt', {
                method: 'PUT',
                headers: {
                    'Authorization': \`Bearer \${token}\`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
            
            if (response.status === 404) {
                // No existe, crear con POST
                response = await fetch('/api/tenants/acme-cannabis-2024/prompt', {
                    method: 'POST',
                    headers: {
                        'Authorization': \`Bearer \${token}\`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(config)
                });
            }
            
            if (response.ok) {
                alert('✅ Configuración guardada exitosamente!');
                loadCurrentBotConfig(); // Recargar info
            } else {
                const error = await response.text();
                throw new Error(\`Error \${response.status}: \${error}\`);
            }
        } catch (error) {
            console.error('Error guardando:', error);
            alert(\`❌ Error guardando configuración: \${error.message}\`);
        }
        
        button.textContent = originalText;
        button.disabled = false;
    }
    
    // Inicializar el módulo
    function init() {
        console.log('🔧 Inicializando detección de menú...');
        
        // Esperar a que la página esté completamente cargada
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(init, 1000);
            });
            return;
        }
        
        // Intentar encontrar el menú lateral
        waitForElement('nav, .sidebar, aside, [role="navigation"]', addBotConfigToMenu);
        
        // También crear el botón flotante como respaldo
        setTimeout(createFloatingButton, 3000);
    }
    
    // Iniciar cuando la página esté lista
    init();
    
    console.log('🤖 Módulo de Configuración del Bot iniciado');
})();