
# Dicionário de Tradução PT-BR

TRANSLATIONS = {
    # Tipos de Transação
    'EARN': 'GANHO',
    'SPEND': 'GASTO',
    'PENALTY': 'PENALIDADE',
    
    # Status
    'PENDING': 'PENDENTE',
    'APPROVED': 'APROVADO',
    'REJECTED': 'REJEITADO',
    'active': 'Ativo',
    'inactive': 'Inativo',
    'accepted': 'Aceita',
    'completed': 'Concluída',
    'expired': 'Expirada',
    'pending_validation': 'Em Análise',
    
    # Ações de Auditoria
    'REMOVE_AVATAR': 'REMOVER AVATAR',
    'RESET_PASSWORD': 'REDEFINIR SENHA',
    'COMPLETE_MISSION': 'COMPLETAR MISSÃO',
    'APPROVE_MISSION': 'APROVAR MISSÃO',
    'REJECT_MISSION': 'REJEITAR MISSÃO',
    'DELETE_USER': 'EXCLUIR USUÁRIO',
    'CREATE_ITEM': 'CRIAR ITEM',
    'UPDATE_ITEM': 'ATUALIZAR ITEM',
    'DELETE_ITEM': 'EXCLUIR ITEM',
    'UPDATE_POINTS': 'ATUALIZAR PONTOS',
    
    # Mensagens de Erro e Sucesso
    'user_not_found': 'Usuário não encontrado.',
    'no_custom_avatar': 'Nenhuma foto personalizada para remover.',
    'avatar_removed': 'Foto de perfil removida. Padrão restaurado.',
    'mission_already_accepted': 'Missão já aceita.',
    'mission_accepted': 'Missão aceita com sucesso!',
    'mission_not_found': 'Missão não encontrada.',
    'mission_completed': 'Missão concluída! +{} pts creditados.',
    'request_in_analysis': 'Solicitação já está em análise.',
    'mission_already_completed': 'Missão já concluída.',
    'mission_expired_validation': 'Missão expirada não pode ser validada.',
    'invalid_mission_data': 'Dados da missão inválidos.',
    'invalid_status_validation': 'Status inválido para validação.',
    'request_sent': 'Solicitação enviada para análise.',
    'request_not_found': 'Solicitação não encontrada ou já processada.',
    'mission_rejected': 'Missão rejeitada.',
    'invalid_action': 'Ação inválida.',
    'insufficient_funds': 'Saldo insuficiente para esta aquisição.',
    'item_not_found': 'Item não encontrado.',
    'purchase_request_sent': 'Solicitação de compra enviada!',
    'login_success': 'Login realizado com sucesso!',
    'login_failed': 'Credenciais inválidas.',
    'register_success': 'Conta criada com sucesso!',
    'register_failed': 'Erro ao criar conta. Email ou usuário já existem.',
    'password_mismatch': 'As senhas não coincidem.',
    'fill_all_fields': 'Por favor, preencha todos os campos.',
}

def get_text(key, *args):
    """Retorna o texto traduzido formatado com argumentos opcionais."""
    text = TRANSLATIONS.get(key, key)
    if args:
        try:
            return text.format(*args)
        except:
            return text
    return text
