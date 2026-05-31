from flask import Blueprint, request, jsonify
from models import PedidoCreate
from storage import pedidos, clientes, contador_pedido

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/pedidos', methods=['GET'])
def listar_pedidos():
    """
    Lista todos os pedidos com o nome do cliente associado
    ---
    tags:
      - Pedidos
    responses:
      200:
        description: Lista de pedidos enriquecida
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              id_cliente: {type: integer}
              nome_cliente: {type: string}
              produto: {type: string}
              valor: {type: number}
    """
    enriquecidos = []
    for p in pedidos:
        cliente = next((c for c in clientes if c['id'] == p['id_cliente']), None)
        enriquecidos.append({
            'id': p['id'],
            'id_cliente': p['id_cliente'],
            'nome_cliente': cliente['nome'] if cliente else 'Desconhecido',
            'produto': p['produto'],
            'valor': p['valor']
        })
    return jsonify(enriquecidos)

@pedidos_bp.route('/pedidos', methods=['POST'])
def criar_pedido():
    """
    Cria um novo pedido associado a um cliente existente
    ---
    tags:
      - Pedidos
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - id_cliente
            - produto
            - valor
          properties:
            id_cliente: {type: integer, example: 1}
            produto: {type: string, example: "Notebook Dell"}
            valor: {type: number, example: 3500.50}
    responses:
      201:
        description: Pedido criado com sucesso
        schema:
          type: object
          properties:
            id: {type: integer}
            id_cliente: {type: integer}
            produto: {type: string}
            valor: {type: number}
      400:
        description: Dados inválidos ou cliente não encontrado
    """
    global contador_pedido
    dados = request.get_json()
    try:
        validado = PedidoCreate(**dados)
    except Exception as e:
        return jsonify({'erro': str(e)}), 400
    cliente_existe = any(c['id'] == validado.id_cliente for c in clientes)
    if not cliente_existe:
        return jsonify({'erro': 'Cliente não encontrado'}), 400
    novo = {
        'id': contador_pedido,
        'id_cliente': validado.id_cliente,
        'produto': validado.produto,
        'valor': validado.valor
    }
    pedidos.append(novo)
    contador_pedido += 1
    return jsonify(novo), 201

@pedidos_bp.route('/pedidos/<int:id_pedido>', methods=['PUT'])
def atualizar_pedido(id_pedido):
    """
    Atualiza um pedido existente
    ---
    tags:
      - Pedidos
    parameters:
      - name: id_pedido
        in: path
        required: true
        type: integer
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - id_cliente
            - produto
            - valor
          properties:
            id_cliente: {type: integer}
            produto: {type: string}
            valor: {type: number}
    responses:
      200:
        description: Pedido atualizado
      400:
        description: Erro de validação ou cliente não encontrado
      404:
        description: Pedido não encontrado
    """
    dados = request.get_json()
    for pedido in pedidos:
        if pedido['id'] == id_pedido:
            try:
                validado = PedidoCreate(**dados)
            except Exception as e:
                return jsonify({'erro': str(e)}), 400
            cliente_existe = any(c['id'] == validado.id_cliente for c in clientes)
            if not cliente_existe:
                return jsonify({'erro': 'Cliente não encontrado'}), 400
            pedido['id_cliente'] = validado.id_cliente
            pedido['produto'] = validado.produto
            pedido['valor'] = validado.valor
            return jsonify(pedido), 200
    return jsonify({'erro': 'Pedido não encontrado'}), 404

@pedidos_bp.route('/pedidos/<int:id_pedido>', methods=['DELETE'])
def deletar_pedido(id_pedido):
    """
    Remove um pedido
    ---
    tags:
      - Pedidos
    parameters:
      - name: id_pedido
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Pedido removido
      404:
        description: Pedido não encontrado
    """
    for i, pedido in enumerate(pedidos):
        if pedido['id'] == id_pedido:
            del pedidos[i]
            return jsonify({'mensagem': 'Pedido removido'}), 200
    return jsonify({'erro': 'Pedido não encontrado'}), 404