from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    from .views import articulos, inventario, ordenCompra, demanda, ventas
    app.register_blueprint(articulos.bp)
    app.register_blueprint(inventario.bp)
    app.register_blueprint(ordenCompra.bp)
    app.register_blueprint(demanda.bp)
    app.register_blueprint(ventas.bp)

    return app

