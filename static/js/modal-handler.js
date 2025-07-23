// static/js/modal-handler.js

// Exemplo de funções para abrir e fechar um modal genérico
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex'; // Usar flex para centralizar
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Adicionar listeners para botões de fechar modal (se houver)
    document.querySelectorAll('.close-button').forEach(button => {
        button.addEventListener('click', function() {
            // Assume que o botão de fechar está dentro do modal-content
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    });

    // Fechar modal clicando fora do conteúdo (se o modal tiver a classe 'modal')
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });

    // Fechar modal com a tecla ESC
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            document.querySelectorAll('.modal').forEach(modal => {
                if (modal.style.display === 'flex') { // Se o modal estiver visível
                    modal.style.display = 'none';
                }
            });
        }
    });
});