from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect 
from config import Config


db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect() 

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app) 

    with app.app_context():
        from . import models  # Importar modelos
        db.create_all()

    from .views import articulos, inventario, ordenCompra, demanda, ventas,proveedores
    app.register_blueprint(articulos.bp)
    app.register_blueprint(inventario.bp)
    app.register_blueprint(ordenCompra.bp)
    app.register_blueprint(demanda.bp)
    app.register_blueprint(ventas.bp)
    app.register_blueprint(proveedores.bp)

    @app.route('/')
    def index():
        return render_template('base.html')

    return app

