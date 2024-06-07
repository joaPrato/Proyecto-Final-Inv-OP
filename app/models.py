from . import db

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class EstadoOrdenCompra(db.Model):
    __tablename__ = 'estado_orden_compra'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    ordenes_compra = db.relationship('OrdenCompra', backref='estado', lazy=True)

class Proveedor(db.Model):
    __tablename__ = 'proveedor'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    detalles_proveedor = db.relationship('DetalleProveedor', backref='proveedor', lazy=True)

class Articulo(db.Model):
    __tablename__ = 'articulo'
    codigo_articulo = db.Column(db.Integer, primary_key=True)
    coeficiente_seguridad = db.Column(db.Integer, nullable=False)
    costo_articulo = db.Column(db.Float, nullable=False)
    punto_pedido = db.Column(db.Integer)
    stock = db.Column(db.Integer, nullable=False)
    stock_maximo = db.Column(db.Integer)
    stock_seguridad = db.Column(db.Integer)
    tiempo_de_pedido = db.Column(db.Integer)
    detalle_proveedor_predeterminado_id = db.Column(db.Integer, db.ForeignKey('detalle_proveedor.id'))
    modelo_inventario_id = db.Column(db.Integer, db.ForeignKey('modelo_inventario.id'), nullable=False)
    detalle_proveedor = db.relationship('DetalleProveedor', backref='articulo', lazy=True)
    detalle_venta = db.relationship('DetalleVenta', backref='articulo', lazy=True)
    demanda = db.relationship('Demanda', backref='articulo', lazy=True)
    demanda_predecida = db.relationship('DemandaPredecida', backref='articulo', lazy=True)
    ordenes_compra = db.relationship('OrdenCompra', backref='articulo', lazy=True)

class OrdenCompra(db.Model):
    __tablename__ = 'orden_compra'
    lote = db.Column(db.Integer, nullable=False)
    nro_orden_compra = db.Column(db.Integer, primary_key=True)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado_orden_compra.id'), nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.codigo_articulo'), nullable=False)

class DetalleProveedor(db.Model):
    __tablename__ = 'detalle_proveedor'
    id = db.Column(db.Integer, primary_key=True)
    costo_almacenamiento = db.Column(db.Float, nullable=False)
    costo_pedido = db.Column(db.Float, nullable=False)
    lote_optimo = db.Column(db.Float, nullable=False)
    precio_articulo = db.Column(db.Float, nullable=False)
    tiempo_demora = db.Column(db.Integer, nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.codigo_articulo'), nullable=False)
    articulo_predeterminado = db.relationship('Articulo', backref='detalle_proveedor_predeterminado', lazy=True, foreign_keys=[Articulo.detalle_proveedor_predeterminado_id])

class Venta(db.Model):
    __tablename__ = 'venta'
    nro_venta = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    detalle_venta = db.relationship('DetalleVenta', backref='venta', lazy=True)

class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.nro_venta'), nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.codigo_articulo'), nullable=False)

class Demanda(db.Model):
    __tablename__ = 'demanda'
    id = db.Column(db.Integer, primary_key=True)
    año = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.codigo_articulo'), nullable=False)

class DemandaPredecida(db.Model):
    __tablename__ = 'demanda_predecida'
    id = db.Column(db.Integer, primary_key=True)
    año = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.codigo_articulo'), nullable=False)
    modelo_prediccion_id = db.Column(db.Integer, db.ForeignKey('modelo_prediccion_demanda.id'), nullable=False)

class ParametrosGeneralesPrediccion(db.Model):
    __tablename__ = 'parametros_generales_prediccion'
    id = db.Column(db.Integer, primary_key=True)
    cantidad_periodos_a_predecir = db.Column(db.Integer, nullable=False)
    error_aceptable = db.Column(db.Integer, nullable=False)
    modelo_calculo_error_id = db.Column(db.Integer, db.ForeignKey('modelo_calculo_error.id'), nullable=False)

class ModeloPrediccionDemanda(db.Model):
    __tablename__ = 'modelo_prediccion_demanda'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    demandas_predecidas = db.relationship('DemandaPredecida', backref='modelo_prediccion', lazy=True)

class ModeloCalculoError(db.Model):
    __tablename__ = 'modelo_calculo_error'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    parametros_generales_prediccion = db.relationship('ParametrosGeneralesPrediccion', backref='modelo_calculo_error', lazy=True)

class ModeloInventario(db.Model):
    __tablename__ = 'modelo_inventario'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    articulos = db.relationship('Articulo', backref='modelo_inventario', lazy=True)

