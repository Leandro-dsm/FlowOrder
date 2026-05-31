from flask import Flask
from flasgger import Swagger
from clientes_blueprint import clientes_bp
from pedidos_blueprint import pedidos_bp

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'FlowOrder API',
    'version': '1.0.0',
    'description': 'API de gestão de clientes e pedidos'
}
swagger = Swagger(app)

app.register_blueprint(clientes_bp, url_prefix='/api')
app.register_blueprint(pedidos_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=5000)