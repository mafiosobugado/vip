// Funções para gerenciar a navbar moderna

// Toggle da sidebar
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('collapsed');
    
    // Salvar preferência no localStorage
    localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
}

// Toggle do menu do usuário na sidebar
function toggleUserMenu() {
    const dropdown = document.getElementById('userMenuDropdown');
    const toggle = document.querySelector('.user-menu-toggle i');
    
    if (dropdown.style.display === 'block') {
        dropdown.style.display = 'none';
        toggle.className = 'fas fa-chevron-up';
    } else {
        dropdown.style.display = 'block';
        toggle.className = 'fas fa-chevron-down';
    }
}

// Toggle do menu do usuário na navbar
function toggleNavUserMenu() {
    const dropdown = document.getElementById('userNavDropdown');
    const chevron = document.getElementById('navUserChevron');
    const userInfo = document.querySelector('.user-info-navbar');
    
    if (dropdown.style.display === 'block') {
        dropdown.style.display = 'none';
        chevron.className = 'fas fa-chevron-down';
        userInfo.classList.remove('active');
    } else {
        dropdown.style.display = 'block';
        chevron.className = 'fas fa-chevron-up';
        userInfo.classList.add('active');
    }
}

// Toggle das notificações
function toggleNotifications() {
    const dropdown = document.getElementById('notificationsDropdown');
    
    if (dropdown.style.display === 'block') {
        dropdown.style.display = 'none';
    } else {
        dropdown.style.display = 'block';
    }
}

// Atualizar contador de notificações
function updateNotificationBadge() {
    const badge = document.querySelector('.notification-badge');
    const unreadCount = document.querySelectorAll('.notification-item.unread').length;
    
    if (unreadCount > 0) {
        badge.textContent = unreadCount;
        badge.style.display = 'block';
    } else {
        badge.style.display = 'none';
    }
}

// Toggle modo escuro (placeholder)
function toggleDarkMode() {
    const body = document.body;
    body.classList.toggle('light-theme');
    
    const icon = document.querySelector('[onclick="toggleDarkMode()"] i');
    if (body.classList.contains('light-theme')) {
        icon.className = 'fas fa-sun';
    } else {
        icon.className = 'fas fa-moon';
    }
}

// Toggle tela cheia
function toggleFullscreen() {
    const icon = document.querySelector('[onclick="toggleFullscreen()"] i');
    
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().then(() => {
            icon.className = 'fas fa-compress';
        });
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen().then(() => {
                icon.className = 'fas fa-expand';
            });
        }
    }
}

// Fechar dropdowns quando clicar fora
function setupClickOutside() {
    document.addEventListener('click', function(event) {
        // Fechar menu do usuário na sidebar
        const userMenu = document.getElementById('userMenuDropdown');
        
        if (userMenu && !event.target.closest('.user-menu') && userMenu.style.display === 'block') {
            userMenu.style.display = 'none';
            const chevron = document.querySelector('.user-menu-toggle i');
            if (chevron) chevron.className = 'fas fa-chevron-up';
        }
        
        // Fechar menu do usuário na navbar
        const navUserMenu = document.getElementById('userNavDropdown');
        const userInfoNavbar = document.querySelector('.user-info-navbar');
        
        if (navUserMenu && !event.target.closest('.user-info-navbar') && navUserMenu.style.display === 'block') {
            navUserMenu.style.display = 'none';
            const navChevron = document.getElementById('navUserChevron');
            if (navChevron) navChevron.className = 'fas fa-chevron-down';
            if (userInfoNavbar) userInfoNavbar.classList.remove('active');
        }
        
        // Fechar notificações
        const notifications = document.getElementById('notificationsDropdown');
        
        if (notifications && !event.target.closest('.notifications-dropdown') && 
            !event.target.closest('[onclick="toggleNotifications()"]') && 
            notifications.style.display === 'block') {
            notifications.style.display = 'none';
        }
    });
}

// Marcar todas as notificações como lidas
function markAllNotificationsRead() {
    const unreadItems = document.querySelectorAll('.notification-item.unread');
    unreadItems.forEach(item => {
        item.classList.remove('unread');
    });
    updateNotificationBadge();
}

// Restaurar estado da sidebar
function restoreSidebarState() {
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    const sidebar = document.querySelector('.sidebar');
    
    if (isCollapsed && sidebar && !sidebar.classList.contains('collapsed')) {
        sidebar.classList.add('collapsed');
    }
}

// Responsividade da sidebar em mobile
function setupMobileResponsive() {
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (!sidebarToggle || !sidebar) return;
    
    if (window.innerWidth <= 768) {
        const handleToggle = function(e) {
            e.stopPropagation();
            sidebar.classList.toggle('show');
        };
        
        sidebarToggle.removeEventListener('click', handleToggle);
        sidebarToggle.addEventListener('click', handleToggle);
        
        // Fechar sidebar ao clicar fora em mobile
        document.addEventListener('click', function(event) {
            if (window.innerWidth <= 768 && 
                !event.target.closest('.sidebar') && 
                !event.target.closest('.sidebar-toggle') &&
                sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
            }
        });
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    restoreSidebarState();
    setupClickOutside();
    setupMobileResponsive();
    updateNotificationBadge();
    
    // Adicionar listener para o botão de marcar todas como lidas
    const markAllBtn = document.querySelector('.mark-all-read');
    if (markAllBtn) {
        markAllBtn.addEventListener('click', markAllNotificationsRead);
    }
    
    // Responsividade em tempo real
    window.addEventListener('resize', function() {
        setupMobileResponsive();
    });
});
    setupMobileResponsive();
    updateNotificationBadge();
    
    // Adicionar listener para o botão de marcar todas como lidas
    const markAllBtn = document.querySelector('.mark-all-read');
    if (markAllBtn) {
        markAllBtn.addEventListener('click', markAllNotificationsRead);
    }
    
    // Responsividade em tempo real
    window.addEventListener('resize', function() {
        setupMobileResponsive();
    });
});
