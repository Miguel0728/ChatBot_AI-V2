// Elementos del DOM
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const loadingIndicator = document.getElementById('loadingIndicator');

// Estado de la aplicación
let isLoading = false;

// Función para formatear el tiempo
function formatTime() {
    const now = new Date();
    return now.toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

// Función para crear un mensaje en el chat
function createMessage(sender, text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <span class="message-sender">${isUser ? '👤 Tú' : '🤖 AI'}</span>
            <span class="message-text">${text}</span>
            <span class="message-time">${formatTime()}</span>
        </div>
    `;
    
    return messageDiv;
}

// Función para agregar mensaje al chat
function addMessage(sender, text, isUser = false) {
    const messageElement = createMessage(sender, text, isUser);
    chatMessages.appendChild(messageElement);
    
    // Scroll al final
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageElement;
}

// Función para enviar mensaje
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isLoading) return;
    
    // Agregar mensaje del usuario
    addMessage('user', message, true);
    
    // Limpiar input
    messageInput.value = '';
    
    // Mostrar indicador de carga
    setLoading(true);
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Agregar respuesta de la IA
            addMessage('bot', data.response, false);
        } else {
            addMessage('bot', `❌ Error: ${data.error}`, false);
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('bot', '❌ Error de conexión. Por favor, intenta de nuevo.', false);
    } finally {
        setLoading(false);
    }
}

// Función para manejar el estado de carga
function setLoading(loading) {
    isLoading = loading;
    
    if (loading) {
        loadingIndicator.classList.add('show');
        sendBtn.disabled = true;
        messageInput.disabled = true;
    } else {
        loadingIndicator.classList.remove('show');
        sendBtn.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
    }
}

// Función para limpiar la conversación
async function clearConversation() {
    if (!confirm('¿Estás seguro de que quieres limpiar la conversación?')) {
        return;
    }
    
    try {
        const response = await fetch('/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            // Limpiar mensajes del DOM
            chatMessages.innerHTML = '';
            
            // Agregar mensaje de bienvenida
            addMessage('bot', '¡Hola! Soy tu asistente AI. ¿En qué puedo ayudarte hoy?', false);
        }
    } catch (error) {
        console.error('Error al limpiar conversación:', error);
        addMessage('bot', '❌ Error al limpiar la conversación.', false);
    }
}

// Event Listeners
sendBtn.addEventListener('click', sendMessage);
clearBtn.addEventListener('click', clearConversation);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-resize del textarea (si decidimos cambiarlo más tarde)
messageInput.addEventListener('input', function() {
    // Funcionalidad futura para auto-resize
});

// Cargar historial al inicio (opcional)
async function loadHistory() {
    try {
        const response = await fetch('/history');
        const data = await response.json();
        
        if (response.ok && data.history.length > 0) {
            // Limpiar chat actual
            chatMessages.innerHTML = '';
            
            // Agregar mensajes del historial
            data.history.forEach(msg => {
                addMessage(
                    msg.role, 
                    msg.content, 
                    msg.role === 'user'
                );
            });
        }
    } catch (error) {
        console.error('Error al cargar historial:', error);
    }
}

// Funciones de utilidad
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Función para formatear texto con markdown básico (opcional)
function formatMessage(text) {
    // Aquí puedes agregar formateo de markdown básico si lo deseas
    return escapeHtml(text)
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>');
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    messageInput.focus();
    
    // Establecer el tiempo inicial en el mensaje de bienvenida
    const welcomeTime = document.querySelector('.message-time');
    if (welcomeTime) {
        welcomeTime.textContent = formatTime();
    }
});

// Manejar desconexión/reconexión
window.addEventListener('online', () => {
    console.log('Conexión restaurada');
});

window.addEventListener('offline', () => {
    console.log('Conexión perdida');
    addMessage('bot', '⚠️ Conexión perdida. Algunos mensajes pueden no enviarse.', false);
});
