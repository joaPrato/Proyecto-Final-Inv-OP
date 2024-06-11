from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from .views import articulos, inventario, ordenCompra, demanda, ventas
    app.register_blueprint(articulos.bp)
    app.register_blueprint(inventario.bp)
    app.register_blueprint(ordenCompra.bp)
    app.register_blueprint(demanda.bp)
    app.register_blueprint(ventas.bp)

    return app

