from flask import Blueprint, request, jsonify
from models import ClienteCreate
from storage import clientes, contador_cliente

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/clientes', methods=['GET'])
def listar_clientes():
    """
    Lista todos os clientes cadastrados
    ---
    tags:
      - Clientes
    responses:
      200:
        description: Lista de clientes
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              nome: {type: string}
              email: {type: string}
              telefone: {type: string}
    """
    return jsonify(clientes)

@clientes_bp.route('/clientes', methods=['POST'])
def criar_cliente():
    """
    Cria um novo cliente com validação Pydantic
    ---
    tags:
      - Clientes
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nome
            - email
            - telefone
          properties:
            nome: {type: string, example: "João Silva"}
            email: {type: string, example: "joao@email.com"}
            telefone: {type: string, example: "(11) 99999-9999"}
    responses:
      201:
        description: Cliente criado com sucesso
      400:
        description: Erro de validação (Pydantic)
    """
    global contador_cliente
    dados = request.get_json()
    try:
        validado = ClienteCreate(**dados)
    except Exception as e:
        return jsonify({'erro': str(e)}), 400
    novo = {
        'id': contador_cliente,
        'nome': validado.nome,
        'email': validado.email,
        'telefone': validado.telefone
    }
    clientes.append(novo)
    contador_cliente += 1
    return jsonify(novo), 201

@clientes_bp.route('/clientes/<int:id_cliente>', methods=['PUT'])
def atualizar_cliente(id_cliente):
    """
    Atualiza um cliente existente
    ---
    tags:
      - Clientes
    parameters:
      - name: id_cliente
        in: path
        required: true
        type: integer
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nome
            - email
            - telefone
          properties:
            nome: {type: string}
            email: {type: string}
            telefone: {type: string}
    responses:
      200:
        description: Cliente atualizado
      400:
        description: Erro de validação
      404:
        description: Cliente não encontrado
    """
    dados = request.get_json()
    for cliente in clientes:
        if cliente['id'] == id_cliente:
            try:
                validado = ClienteCreate(**dados)
            except Exception as e:
                return jsonify({'erro': str(e)}), 400
            cliente['nome'] = validado.nome
            cliente['email'] = validado.email
            cliente['telefone'] = validado.telefone
            return jsonify(cliente), 200
    return jsonify({'erro': 'Cliente não encontrado'}), 404

@clientes_bp.route('/clientes/<int:id_cliente>', methods=['DELETE'])
def deletar_cliente(id_cliente):
    """
    Remove um cliente
    ---
    tags:
      - Clientes
    parameters:
      - name: id_cliente
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Cliente removido
      404:
        description: Cliente não encontrado
    """
    for i, cliente in enumerate(clientes):
        if cliente['id'] == id_cliente:
            del clientes[i]
            return jsonify({'mensagem': 'Cliente removido'}), 200
    return jsonify({'erro': 'Cliente não encontrado'}), 404