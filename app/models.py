from . import db
from flask_sqlalchemy import SQLAlchemy # type: ignore
from sqlalchemy.sql import func # type: ignore
import math

class EstadoOrdenCompra(db.Model):
    __tablename__ = 'estado_orden_compra'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    
    #Relaciones
    ordenes_compra=db.relationship('OrdenCompra', lazy='dynamic',backref='estado_orden_compra')

  
class Proveedor(db.Model):
    __tablename__ = 'proveedor'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    #Relaciones
    detalles_proveedor=db.relationship('DetalleProveedor',lazy='dynamic',backref='proveedor')
 
class DetalleProveedor(db.Model):
    __tablename__ = 'detalle_proveedor'
    id = db.Column(db.Integer, primary_key=True)
    costo_pedido_proveedor = db.Column(db.Float, nullable=False)
    lote_optimo = db.Column(db.Float, nullable=False)
    precio_articulo = db.Column(db.Float, nullable=False)
    tiempo_demora = db.Column(db.Integer, nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.id'))

    


class Articulo(db.Model):
    __tablename__ = 'articulo'
    id = db.Column(db.Integer, primary_key=True)
    codigo_articulo = db.Column(db.Integer, unique=True, nullable=False)
    nombre_articulo = db.Column(db.String(100), nullable=False)
    coeficiente_seguridad = db.Column(db.Float, nullable=False)
    costo_almacenamiento = db.Column(db.Float, nullable=False)
    costo_de_pedido = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    tiempo_de_pedido = db.Column(db.Integer)
    modelo_inventario_id = db.Column(db.Integer, db.ForeignKey('modelo_inventario.id'), nullable=False)
    detalle_proveedor_predeterminado_id = db.Column(db.Integer, db.ForeignKey('detalle_proveedor.id'))

    #Relaciones
    detalle_proveedor_predeterminado = db.relationship('DetalleProveedor', foreign_keys=[detalle_proveedor_predeterminado_id], backref='articulo_predeterminado', uselist=False)
    detalles_proveedor = db.relationship('DetalleProveedor', backref='articulo', foreign_keys='DetalleProveedor.articulo_id')

    def calcular_stock_de_seguridad (articulo,detalle_proveedor,desviacion_estandar):
        coeficiente_seguridad=float(articulo.coeficiente_seguridad)
        demora_proveedor=int(detalle_proveedor.tiempo_demora)

        stock_de_seguridad=coeficiente_seguridad*desviacion_estandar*math.sqrt(demora_proveedor)

        return stock_de_seguridad
    
    def calcular_demanda_diaria(demanda):
        cantidad_demandada=int(demanda.cantidad)
    
        demanda_diaria=cantidad_demandada/30

        return demanda_diaria
    
    def calcular_punto_de_pedido (stock_seguridad,demanda_diaria,detalle_proveedor):
        demora_proveedor=int(detalle_proveedor.tiempo_demora)

        punto_de_pedido=demanda_diaria*demora_proveedor + stock_seguridad

        return punto_de_pedido
    
    def calcular_cantidad_pedir_interlavo_fijo():
        #codigo para calcular cantidad a pedir en el modelo de inventario intervalo fijo
        return
    
    
class OrdenCompra(db.Model):
    __tablename__ = 'orden_compra'
    lote = db.Column(db.Integer, nullable=False)
    nro_orden_compra = db.Column(db.Integer, primary_key=True)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado_orden_compra.id'), nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.id'), nullable=False)


class Venta(db.Model):
    __tablename__ = 'venta'
    nro_venta = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, default=func.now())
    cantidad = db.Column(db.Integer, nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.codigo_articulo'), nullable=False)
    articulo = db.relationship('Articulo', backref='ventas') # trae el nombre articulo de la venta

    def calcular_demanda_mes(articulo, fecha):
        mes = str(fecha.month).zfill(2)  # Formatea el mes con dos dígitos
        año = str(fecha.year)  # Año ya es una cadena
        demanda_mes = db.session.query(func.sum(Venta.cantidad)).\
            filter_by(articulo_id=articulo).\
            filter(func.strftime('%m', Venta.fecha) == mes).\
            filter(func.strftime('%Y', Venta.fecha) == año).scalar()

        return demanda_mes or 0
    

class Demanda(db.Model):
    __tablename__ = 'demanda'
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_d= db.Column(db.Date, nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.id'), nullable=False)
    articulo = db.relationship('Articulo', backref='demanda') # trae el nombre articulo de la Demanda
    
    @classmethod
    def existe_demanda(cls, articulo_id, fecha): #cls es self pero para el metodo
        mes = fecha.month
        año = fecha.year
        
        demanda_existente = cls.query.filter_by(articulo_id=articulo_id).\
            filter(func.strftime('%m', cls.fecha_d) == str(mes).zfill(2)).\
            filter(func.strftime('%Y', cls.fecha_d) == str(año)).first()
        return demanda_existente is not None
    
    
  
class DemandaPredecida(db.Model):
    __tablename__ = 'demanda_predecida'
    id = db.Column(db.Integer, primary_key=True)
    año = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.id'), nullable=False)
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

    #Relaciones
    demandas_predecida=db.relationship('DemandaPredecida', lazy='dynamic', backref='modelo_prediccion_demanda')

    
class ModeloCalculoError(db.Model):
    __tablename__ = 'modelo_calculo_error'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    #Relaciones
    parametros_generales_prediccion=db.relationship('ParametrosGeneralesPrediccion', lazy='dynamic',backref='modelo_calculo_error')
  

class ModeloInventario(db.Model):
    __tablename__ = 'modelo_inventario'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    #Relaciones
    articulos=db.relationship('Articulo', lazy='dynamic',backref='modelo_inventario')


