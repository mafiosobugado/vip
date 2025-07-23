// Sistema de notificações funcional

// Dados simulados de notificações (em produção viriam do backend)
let notifications = [
    {
        id: 1,
        title: 'Novo item crítico identificado',
        message: 'João Silva - Investigação federal',
        time: '2 min atrás',
        type: 'danger',
        icon: 'fas fa-exclamation-triangle',
        read: false,
        critical: true
    },
    {
        id: 2,
        title: 'Novo executivo adicionado',
        message: 'Maria Santos foi adicionada ao sistema',
        time: '15 min atrás',
        type: 'warning',
        icon: 'fas fa-user-plus',
        read: false,
        critical: false
    },
    {
        id: 3,
        title: 'Item tratado com sucesso',
        message: 'Processo judicial - Status atualizado',
        time: '1 hora atrás',
        type: 'success',
        icon: 'fas fa-check-circle',
        read: false,
        critical: false
    },
    {
        id: 4,
        title: 'Score de risco atualizado',
        message: 'Pedro Costa - Novo score: 85',
        time: '2 horas atrás',
        type: 'warning',
        icon: 'fas fa-chart-line',
        read: true,
        critical: false
    },
    {
        id: 5,
        title: 'Backup realizado',
        message: 'Backup diário concluído com sucesso',
        time: '3 horas atrás',
        type: 'success',
        icon: 'fas fa-database',
        read: true,
        critical: false
    }
];

// Marcar uma notificação como lida
function markAsRead(notificationId) {
    const notification = notifications.find(n => n.id === notificationId);
    if (notification) {
        notification.read = true;
        updateNotificationDisplay();
        updateNotificationBadge();
        
        // Animação de sucesso
        const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
        if (notificationElement) {
            notificationElement.style.transform = 'scale(0.95)';
            setTimeout(() => {
                notificationElement.classList.remove('unread');
                notificationElement.style.transform = 'scale(1)';
            }, 150);
        }
        
        // Mostrar toast de sucesso
        showToast('Notificação marcada como lida', 'success');
    }
}

// Marcar todas as notificações como lidas
function markAllNotificationsRead() {
    notifications.forEach(notification => {
        notification.read = true;
    });
    
    updateNotificationDisplay();
    updateNotificationBadge();
    showToast('Todas as notificações foram marcadas como lidas', 'success');
}

// Atualizar o contador de notificações
function updateNotificationBadge() {
    const badge = document.getElementById('notificationCount');
    const unreadCount = notifications.filter(n => !n.read).length;
    
    if (unreadCount > 0) {
        badge.textContent = unreadCount;
        badge.style.display = 'block';
    } else {
        badge.style.display = 'none';
    }
}

// Atualizar a exibição das notificações no dropdown
function updateNotificationDisplay() {
    const notificationsList = document.getElementById('notificationsList');
    if (!notificationsList) return;
    
    notificationsList.innerHTML = '';
    
    // Mostrar apenas as 5 mais recentes no dropdown
    const recentNotifications = notifications.slice(0, 5);
    
    recentNotifications.forEach(notification => {
        const notificationElement = createNotificationElement(notification, false);
        notificationsList.appendChild(notificationElement);
    });
}

// Criar elemento de notificação
function createNotificationElement(notification, isModal = false) {
    const div = document.createElement('div');
    div.className = `notification-item${isModal ? ' notification-modal-item' : ''} ${!notification.read ? 'unread' : ''}`;
    div.setAttribute('data-notification-id', notification.id);
    
    div.innerHTML = `
        <div class="notification-icon ${notification.type}">
            <i class="${notification.icon}"></i>
        </div>
        <div class="notification-content">
            <h5>${notification.title}</h5>
            <p>${notification.message}</p>
            <span class="notification-time">${notification.time}</span>
        </div>
        ${!notification.read ? `
            <button class="notification-action" onclick="markAsRead(${notification.id})" title="Marcar como lida">
                <i class="fas fa-check"></i>
            </button>
        ` : ''}
    `;
    
    return div;
}

// Abrir modal de notificações
function openNotificationsModal() {
    loadNotificationsModal();
    openModal('notificationsModal');
    
    // Fechar dropdown
    document.getElementById('notificationsDropdown').style.display = 'none';
}

// Carregar notificações no modal
function loadNotificationsModal(filter = 'all') {
    const modalList = document.getElementById('notificationsModalList');
    if (!modalList) return;
    
    modalList.innerHTML = '';
    
    let filteredNotifications = notifications;
    
    switch (filter) {
        case 'unread':
            filteredNotifications = notifications.filter(n => !n.read);
            break;
        case 'critical':
            filteredNotifications = notifications.filter(n => n.critical);
            break;
        default:
            filteredNotifications = notifications;
    }
    
    if (filteredNotifications.length === 0) {
        modalList.innerHTML = '<p style="text-align: center; color: var(--text-color-light-2); padding: 20px;">Nenhuma notificação encontrada.</p>';
        return;
    }
    
    filteredNotifications.forEach(notification => {
        const notificationElement = createNotificationElement(notification, true);
        modalList.appendChild(notificationElement);
    });
}

// Filtrar notificações no modal
function filterNotifications(filter) {
    // Atualizar botões ativos
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Carregar notificações filtradas
    loadNotificationsModal(filter);
}

// Mostrar toast de sucesso/erro
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Adicionar estilos do toast se não existirem
    if (!document.querySelector('#toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            .toast {
                position: fixed;
                top: 100px;
                right: 20px;
                background: var(--dark-bg-3);
                color: var(--text-color-light);
                padding: 12px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                z-index: 10000;
                display: flex;
                align-items: center;
                gap: 8px;
                border-left: 4px solid var(--primary-color);
                animation: slideInRight 0.3s ease;
            }
            .toast-success { border-left-color: #28a745; }
            .toast-error { border-left-color: #dc3545; }
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(toast);
    
    // Remover após 3 segundos
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Inicializar sistema de notificações
document.addEventListener('DOMContentLoaded', function() {
    updateNotificationDisplay();
    updateNotificationBadge();
    
    // Simular novas notificações (remover em produção)
    setTimeout(() => {
        notifications.unshift({
            id: Date.now(),
            title: 'Nova simulação',
            message: 'Notificação de teste adicionada',
            time: 'Agora',
            type: 'warning',
            icon: 'fas fa-bell',
            read: false,
            critical: false
        });
        updateNotificationDisplay();
        updateNotificationBadge();
    }, 10000); // 10 segundos após carregar
});
