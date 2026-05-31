# ==========================================
# FlowOrder - Armazenamento em memória
# ==========================================
# Simula um banco de dados para desenvolvimento.
# Em produção, substitua por SQLAlchemy + PostgreSQL.

# Lista de clientes (cada cliente é um dicionário com id, nome, email, telefone)
clientes = []

# Lista de pedidos (cada pedido tem id, id_cliente, produto, valor)
pedidos = []

# Contadores para IDs automáticos
contador_cliente = 1
contador_pedido = 1