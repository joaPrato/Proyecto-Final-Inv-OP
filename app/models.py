from . import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

class EstadoOrdenCompra(db.Model):
    __tablename__ = 'estado_orden_compra'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

    def __init__(self, nombre):
        self.nombre = nombre

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre
        }

class Proveedor(db.Model):
    __tablename__ = 'proveedor'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)


    def __init__(self, nombre):
        self.nombre = nombre

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre
        }

class Articulo(db.Model):
    __tablename__ = 'articulo'
    id=db.Column(db.Integer,primary_key=True)
    codigo_articulo = db.Column(db.Integer, unique=True,nullable=False)
    nombre_articulo = db.Column(db.String(100),nullable=False)
    coeficiente_seguridad = db.Column(db.Float, nullable=False)
    costo_almacenamiento = db.Column(db.Float, nullable=False)
    costo_de_pedido = db.Column(db.Float,nullable=False)
    #punto_pedido = db.Column(db.Integer) Calcular en un metodo
    stock = db.Column(db.Integer, nullable=False)
    #demandaDiaria = db.Column(db.Integer) Calcular en un metodo
    #stock_seguridad = db.Column(db.Integer) Calcular en un metodo
    tiempo_de_pedido = db.Column(db.Integer)
    detalle_proveedor_predeterminado_id = db.Column(db.Integer, db.ForeignKey('detalle_proveedor.id', use_alter=True, name='fk_detalle_proveedor_id'))
    modelo_inventario_id = db.Column(db.Integer, db.ForeignKey('modelo_inventario.id'), nullable=False)
    

    detalles_proveedor = db.relationship('DetalleProveedor', lazy=True,foreign_keys='DetalleProveedor.articulo_id')
    demandas = db.relationship('Demanda', lazy=True,foreign_keys='Demanda.articulo_id')
    demandas_predecidas = db.relationship('DemandaPredecida', lazy=True,foreign_keys='DemandaPredecida.articulo_id')
    modelo_inventario = db.relationship('ModeloInventario',lazy='joined',foreign_keys=[modelo_inventario_id])
    detalle_proveedor_predeterminado= db.relationship('DetalleProveedor', lazy='joined',foreign_keys=[detalle_proveedor_predeterminado_id])

    def __init__(self, codigo_articulo,nombre_articulo, coeficiente_seguridad, costo_almacenamiento, costo_de_pedido, stock, tiempo_de_pedido, detalle_proveedor_predeterminado_id, modelo_inventario_id):
        self.codigo_articulo = codigo_articulo
        self.nombre_articulo=nombre_articulo
        self.coeficiente_seguridad = coeficiente_seguridad
        self.costo_almacenamiento = costo_almacenamiento
        self.costo_de_pedido = costo_de_pedido
        self.stock = stock
        self.tiempo_de_pedido = tiempo_de_pedido
        self.detalle_proveedor_predeterminado_id = detalle_proveedor_predeterminado_id
        self.modelo_inventario_id = modelo_inventario_id

    def serialize(self):
        return {
            'id': self.id,
            'codigo_articulo': self.codigo_articulo,
            'nombre_articulo': self.nombre_articulo,
            'coeficiente_seguridad': self.coeficiente_seguridad,
            'costo_almacenamiento': self.costo_almacenamiento,
            'costo_de_pedido': self.costo_de_pedido,
            'stock': self.stock,
            'tiempo_de_pedido': self.tiempo_de_pedido,
            'detalle_proveedor_predeterminado': self.detalle_proveedor_predeterminado.serialize() if self.detalle_proveedor_predeterminado else None,
            'modelo_inventario': self.modelo_inventario.serialize() if self.modelo_inventario else None,
            'detalles_proveedor': [detalle.serialize() for detalle in self.detalles_proveedor]  if self.detalles_proveedor else [],
            'demandas': [demanda.serialize() for demanda in self.demandas] if self.demandas else [],
            'demandas_predecidas': [demanda_predecida.serialize() for demanda_predecida in self.demandas_predecidas] if self.demandas_predecidas else []
        }

class OrdenCompra(db.Model):
    __tablename__ = 'orden_compra'
    lote = db.Column(db.Integer, nullable=False)
    nro_orden_compra = db.Column(db.Integer, primary_key=True)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado_orden_compra.id'), nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.codigo_articulo'), nullable=False)

    articulo= db.relationship('Articulo', lazy='joined')
    estadoOrdenCompra= db.relationship('EstadoOrdenCompra', lazy='joined')

    def __init__(self, lote, estado, articulo):
        self.lote = lote
        self.estado = estado
        self.articulo = articulo

    def serialize(self):
        return {
            'lote': self.lote,
            'nro_orden_compra': self.nro_orden_compra,
            'estado': self.estado.serialize(),
            'articulo': self.articulo.serialize()
        }


class DetalleProveedor(db.Model):
    __tablename__ = 'detalle_proveedor'
    id = db.Column(db.Integer, primary_key=True)
    costo_pedido_proveedor = db.Column(db.Float, nullable=False)
    lote_optimo = db.Column(db.Float, nullable=False)
    precio_articulo = db.Column(db.Float, nullable=False)
    tiempo_demora = db.Column(db.Integer, nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.codigo_articulo'))

    proveedor= db.relationship('Proveedor',lazy='joined')

    def __init__(self, costo_pedido_proveedor, lote_optimo, precio_articulo, tiempo_demora, proveedor):
        self.costo_pedido_proveedor = costo_pedido_proveedor
        self.lote_optimo = lote_optimo
        self.precio_articulo = precio_articulo
        self.tiempo_demora = tiempo_demora
        self.proveedor = proveedor
        

    def serialize(self):
        return {
            'id': self.id,
            'costo_pedido_proveedor': self.costo_pedido_proveedor,
            'lote_optimo': self.lote_optimo,
            'precio_articulo': self.precio_articulo,
            'tiempo_demora': self.tiempo_demora,
            'proveedor': self.proveedor.serialize(),
        }
    

class Venta(db.Model):
    __tablename__ = 'venta'
    nro_venta = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, default=func.now())

    detalles_venta = db.relationship('DetalleVenta', lazy='joined')

    def __init__(self, fecha):
        self.fecha = fecha

    def serialize(self):
        return {
            'nro_venta': self.nro_venta,
            'fecha': self.fecha,
            'detalles_venta': [detalle.serialize() for detalle in self.detalles_venta]  if self.detalles_venta else []

        }

class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.nro_venta'), nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.codigo_articulo'), nullable=False)

    articulo=db.relationship('Articulo',lazy='joined')

    def __init__(self, cantidad, venta_id, articulo):
        self.cantidad = cantidad
        self.venta_id = venta_id
        self.articulo= articulo

    def serialize(self):
        return {
            'id': self.id,
            'cantidad': self.cantidad,
            'venta_id': self.venta_id,
            'articulos': self.articulo.serialize()
        }

class Demanda(db.Model):
    __tablename__ = 'demanda'
    id = db.Column(db.Integer, primary_key=True)
    año = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.codigo_articulo'), nullable=False)

    def __init__(self, año, mes, cantidad):
        self.año = año
        self.mes = mes
        self.cantidad = cantidad

    def serialize(self):
        return {
            'id': self.id,
            'año': self.año,
            'mes': self.mes,
            'cantidad': self.cantidad
        }

class DemandaPredecida(db.Model):
    __tablename__ = 'demanda_predecida'
    id = db.Column(db.Integer, primary_key=True)
    año = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.codigo_articulo'), nullable=False)
    modelo_prediccion_id = db.Column(db.Integer, db.ForeignKey('modelo_prediccion_demanda.id'), nullable=False)
    
    modelo_prediccion=db.relationship('ModeloPrediccionDemanda',lazy='joined')

    def __init__(self, año, mes, cantidad, modelo_prediccion):
        self.año = año
        self.mes = mes
        self.cantidad = cantidad
        self.modelo_prediccion=modelo_prediccion

    def serialize(self):
        return {
            'id': self.id,
            'año': self.año,
            'mes': self.mes,
            'cantidad': self.cantidad,
            'modelo_prediccion': self.modelo_prediccion.serialize()
        }


class ParametrosGeneralesPrediccion(db.Model):
    __tablename__ = 'parametros_generales_prediccion'
    id = db.Column(db.Integer, primary_key=True)
    cantidad_periodos_a_predecir = db.Column(db.Integer, nullable=False)
    error_aceptable = db.Column(db.Integer, nullable=False)
    modelo_calculo_error_id = db.Column(db.Integer, db.ForeignKey('modelo_calculo_error.id'), nullable=False)

    modelo_calculo_error=db.relationship('ModeloCalculoError', lazy='joined')

    def __init__(self, cantidad_periodos_a_predecir, error_aceptable, modelo_calculo_error):
        self.cantidad_periodos_a_predecir = cantidad_periodos_a_predecir
        self.error_aceptable = error_aceptable
        self.modelo_calculo_error = modelo_calculo_error

    def serialize(self):
        return {
            'id': self.id,
            'cantidad_periodos_a_predecir': self.cantidad_periodos_a_predecir,
            'error_aceptable': self.error_aceptable,
            'modelo_calculo_error': self.modelo_calculo_error.serialize()
        }

class ModeloPrediccionDemanda(db.Model):
    __tablename__ = 'modelo_prediccion_demanda'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    def __init__(self, nombre):
        self.nombre = nombre

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre
        }

class ModeloCalculoError(db.Model):
    __tablename__ = 'modelo_calculo_error'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    def __init__(self, nombre):
        self.nombre = nombre

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre
        }

class ModeloInventario(db.Model):
    __tablename__ = 'modelo_inventario'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    def __init__(self, nombre):
        self.nombre = nombre

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre
        }