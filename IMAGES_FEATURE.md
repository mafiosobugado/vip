# Funcionalidade de Múltiplas Imagens

## Visão Geral
O sistema agora suporta múltiplas imagens para cada item identificado, além da imagem principal existente.

## Funcionalidades Implementadas

### 1. Imagem Principal (Compatibilidade)
- Mantém a funcionalidade original de uma imagem principal por item
- Upload através do campo "Imagem Principal (Opcional)"
- Visualização e edição através do modal existente

### 2. Galeria de Imagens
- **Adicionar Imagens**: Botão "+ Adicionar Nova Imagem" na seção de edição
- **Visualizar Imagens**: Clique em qualquer imagem da galeria para visualizar em tamanho completo
- **Editar Descrição**: Cada imagem pode ter uma descrição personalizada
- **Excluir Imagens**: Botão "×" no canto superior direito de cada imagem

### 3. Modais Implementados
- **Modal Principal**: Para imagem principal (funcionalidade existente)
- **Modal de Adição**: Para adicionar novas imagens à galeria
- **Modal de Visualização**: Para ver imagens da galeria em tamanho completo

## Estrutura do Banco de Dados

### Nova Tabela: `item_images`
```sql
CREATE TABLE item_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    description TEXT,
    upload_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);
```

## Novas Rotas da API

### POST `/add_item_image/<int:item_id>`
- Adiciona uma nova imagem a um item específico
- Parâmetros: `image` (arquivo), `description` (texto opcional)
- Retorna: JSON com status de sucesso/erro

### DELETE `/delete_item_image/<int:image_id>`
- Remove uma imagem específica
- Remove tanto o registro do banco quanto o arquivo físico
- Retorna: JSON com status de sucesso/erro

### PUT `/update_image_description/<int:image_id>`
- Atualiza a descrição de uma imagem
- Parâmetros: JSON com `description`
- Retorna: JSON com status de sucesso/erro

## Funcionalidades JavaScript

### Principais Funções
- `openAddImageModal()`: Abre modal para adicionar nova imagem
- `addNewImage()`: Processa upload de nova imagem
- `deleteImage(imageId)`: Remove imagem com confirmação
- `openGalleryModalWithData(element)`: Abre modal de visualização
- `updateImageDescription()`: Salva descrição editada

### Validações
- Tamanho máximo: 5MB por imagem
- Formatos suportados: JPG, JPEG, PNG
- Validação tanto no frontend quanto backend

## Como Usar

### Para Adicionar Imagens (Apenas na Edição)
1. Acesse a edição de um item existente
2. Role até a seção "Galeria de Imagens"
3. Clique em "+ Adicionar Nova Imagem"
4. Selecione o arquivo e adicione uma descrição (opcional)
5. Clique em "Adicionar"

### Para Visualizar/Editar
1. Clique em qualquer imagem da galeria
2. A imagem abrirá em um modal em tamanho completo
3. Edite a descrição se necessário
4. Clique em "Salvar Descrição" para confirmar mudanças

### Para Excluir
1. Clique no "×" no canto superior direito da imagem
2. Confirme a exclusão no prompt

## Notas Técnicas
- As imagens são armazenadas em `/static/uploads/`
- Nomes de arquivo são gerados com UUID para evitar conflitos
- Exclusão em cascata: remover um item remove todas suas imagens
- Compatibilidade total com funcionalidade existente
