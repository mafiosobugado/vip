# VIP Monitoring System

Sistema de monitoramento VIP com gerenciamento de usuários e alertas.

## Estrutura do Projeto

```
vip/
├── app.py                 # Aplicação Flask principal
├── database.py           # Funções do banco de dados
├── site.db              # Banco de dados SQLite
├── static/              # Arquivos estáticos
│   ├── css/
│   │   └── style.css    # Estilos principais
│   ├── js/
│   │   ├── main.js
│   │   ├── navbar.js
│   │   ├── notifications.js
│   │   ├── charts.js
│   │   ├── modal-handler.js
│   │   └── settings.js
│   ├── uploads/         # Imagens enviadas
│   └── favicon.ico
├── templates/           # Templates HTML
│   ├── base.html        # Template base
│   ├── login.html       # Página de login
│   ├── register.html    # Página de registro
│   ├── dashboard.html   # Dashboard principal
│   ├── config.html      # Configurações de usuário
│   ├── alerts.html      # Gerenciamento de alertas
│   ├── executives.html  # Gerenciamento de executivos
│   ├── items.html       # Itens identificados
│   ├── audit.html       # Auditoria do sistema
│   ├── reports.html     # Relatórios
│   ├── error.html       # Página de erro
│   ├── add_edit_executive.html
│   ├── add_edit_item.html
│   ├── data_management.html
│   └── partials/        # Componentes parciais
├── venv/               # Ambiente virtual Python
└── docs/               # Documentação (arquivos .md)
```

## Funcionalidades

### Autenticação
- Login com tipos de usuário (Usuário/Administrador)
- Registro de novos usuários
- Gerenciamento de sessões

### Administração (apenas para administradores)
- Gerenciamento de usuários
- Alteração de tipos de usuário
- Ativação/desativação de contas
- Reset de senhas

### Sistema de Alertas
- Criação e gerenciamento de alertas
- Notificações em tempo real
- Marcação como lido/não lido

### Executivos
- Cadastro de executivos
- Gerenciamento de informações
- Níveis de risco

### Auditoria
- Log de ações do sistema
- Histórico de alterações

## Como Executar

1. Ative o ambiente virtual:
   ```bash
   venv\Scripts\activate
   ```

2. Execute a aplicação:
   ```bash
   python app.py
   ```

3. Acesse: http://127.0.0.1:5000

## Usuários Padrão

- **Admin:** mafiosobugado (tipo: admin)
- **Usuário:** testuser (tipo: user)

## Tecnologias

- **Backend:** Flask, SQLite
- **Frontend:** HTML5, CSS3, JavaScript
- **Autenticação:** Flask-Login
- **UI:** Font Awesome, CSS Grid/Flexbox
