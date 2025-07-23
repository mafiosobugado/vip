// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Fechar mensagens de flash
    const closeAlertButtons = document.querySelectorAll('.close-alert');
    closeAlertButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });

    // Lógica para o submenu do usuário na sidebar
    const userInfoToggle = document.querySelector('.user-info-toggle');
    if (userInfoToggle) {
        userInfoToggle.addEventListener('click', function(event) {
            event.preventDefault(); // Evita que o link navegue
            const submenu = this.nextElementSibling; // O submenu é o próximo irmão da <a>
            if (submenu && submenu.classList.contains('user-submenu')) {
                submenu.classList.toggle('show');
            }
        });

        // Fechar submenu se clicar fora
        document.addEventListener('click', function(event) {
            if (userInfoToggle && !userInfoToggle.contains(event.target) && !event.target.closest('.user-submenu')) {
                const submenu = userInfoToggle.nextElementSibling;
                if (submenu && submenu.classList.contains('show')) {
                    submenu.classList.remove('show');
                }
            }
        });
    }

    // Função de confirmação de exclusão genérica (pode ser usada em vários lugares)
    // Usada por onsubmit="return confirmDelete();"
    window.confirmDelete = function() {
        return confirm('Tem certeza que deseja excluir este item?');
    };

    // Garantir que botões de delete tenham a classe correta
    const deleteButtons = document.querySelectorAll('button[title*="Excluir"], button.btn-delete');
    deleteButtons.forEach(button => {
        if (!button.classList.contains('btn-delete')) {
            button.classList.add('btn-delete');
        }
    });

    // Garantir que outros botões de ação tenham as classes corretas
    const treatButtons = document.querySelectorAll('button[title*="Tratado"], button.btn-mark-treated');
    treatButtons.forEach(button => {
        if (!button.classList.contains('btn-mark-treated')) {
            button.classList.add('btn-mark-treated');
        }
    });

    const ignoreButtons = document.querySelectorAll('button[title*="Ignorado"], button.btn-mark-ignored');
    ignoreButtons.forEach(button => {
        if (!button.classList.contains('btn-mark-ignored')) {
            button.classList.add('btn-mark-ignored');
        }
    });
});