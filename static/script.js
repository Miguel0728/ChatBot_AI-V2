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
function createMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const avatarSVG = isUser 
        ? `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
             <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
           </svg>`
        : `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
             <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
             <path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
           </svg>`;
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            ${avatarSVG}
        </div>
        <div class="message-content">
            <div class="message-bubble">
                <p class="message-text">${escapeHtml(text)}</p>
            </div>
            <span class="message-time">${formatTime()}</span>
        </div>
    `;
    
    return messageDiv;
}

// Función para agregar mensaje al chat
function addMessage(text, isUser = false) {
    const messageElement = createMessage(text, isUser);
    chatMessages.appendChild(messageElement);
    
    // Scroll suave al final
    requestAnimationFrame(() => {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    });
    
    return messageElement;
}

// Función para enviar mensaje
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isLoading) return;
    
    // Agregar mensaje del usuario
    addMessage(message, true);
    
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
            // Pequeño delay para mejor UX
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Agregar respuesta de la IA
            addMessage(data.response, false);
        } else {
            addMessage(`❌ Error: ${data.error}`, false);
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('❌ Error de conexión. Por favor, intenta de nuevo.', false);
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
            addMessage('¡Hola! 👋 Soy tu asistente AI. ¿En qué puedo ayudarte hoy?', false);
        }
    } catch (error) {
        console.error('Error al limpiar conversación:', error);
        addMessage('❌ Error al limpiar la conversación.', false);
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

// Auto-resize del textarea
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 150) + 'px';
});

// Funciones de utilidad
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Función para formatear texto con markdown básico
function formatMessage(text) {
    return escapeHtml(text)
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    messageInput.focus();
    
    // Establecer el tiempo inicial en el mensaje de bienvenida
    const welcomeTime = document.querySelector('.message-time');
    if (welcomeTime) {
        welcomeTime.textContent = formatTime();
    }
    
    // Efecto de escritura para el mensaje de bienvenida (opcional)
    const firstMessage = document.querySelector('.message-text');
    if (firstMessage) {
        const text = firstMessage.textContent;
        firstMessage.textContent = '';
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                firstMessage.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 30);
            }
        };
        setTimeout(typeWriter, 500);
    }
});

// Manejar desconexión/reconexión
window.addEventListener('online', () => {
    console.log('Conexión restaurada');
});

window.addEventListener('offline', () => {
    console.log('Conexión perdida');
    addMessage('⚠️ Conexión perdida. Algunos mensajes pueden no enviarse.', false);
});

// Añadir indicador visual cuando el usuario está escribiendo
let typingTimeout;
messageInput.addEventListener('input', () => {
    clearTimeout(typingTimeout);
    
    // Aquí podrías añadir lógica para mostrar "escribiendo..."
    typingTimeout = setTimeout(() => {
        // Usuario dejó de escribir
    }, 1000);
});