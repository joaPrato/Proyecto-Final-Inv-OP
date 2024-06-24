from sqlalchemy import func,desc
from . import db
from flask_sqlalchemy import SQLAlchemy 
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
    precio_articulo = db.Column(db.Float, nullable=False)
    tiempo_demora = db.Column(db.Integer, nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.id'))

    #Relaciones
    ordenes_compra=db.relationship('OrdenCompra',lazy='dynamic',backref='detalle_proveedor')    

    def calcular_lote_a_comprar(detalle_proveedor):
        #caluclo para obtener lote optimo
        return

    


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
    ordenes_compra = db.relationship ('OrdenCompra',backref='articulo',lazy='dynamic')

    def calcular_stock_de_seguridad(self):
        coeficiente_seguridad = float(self.coeficiente_seguridad)
        demora_proveedor = int(self.detalle_proveedor_predeterminado.tiempo_demora)
        desviacion_estandar = 1

        stock_de_seguridad = coeficiente_seguridad * desviacion_estandar * math.sqrt(demora_proveedor)

        return stock_de_seguridad
    
    def calcular_demanda_diaria(self):
        # Obtener la última demanda
        demanda = Demanda.query.filter_by(articulo_id=self.id).order_by(desc(Demanda.año), desc(Demanda.mes)).first()
        # Obtener la última demanda predecida
        demanda_predecida = DemandaPredecida.query.filter_by(articulo_id=self.id).order_by(desc(DemandaPredecida.año), desc(DemandaPredecida.mes)).first()

        cantidad_demandada = 0

        # Verificar si se encontró alguna demanda o demanda predecida
        if demanda and demanda_predecida:
            # Comparar las fechas para determinar cuál usar
            if (demanda.año > demanda_predecida.año) or (demanda.año == demanda_predecida.año and demanda.mes > demanda_predecida.mes):
                cantidad_demandada = demanda.cantidad
            else:
                cantidad_demandada = demanda_predecida.cantidad
        elif demanda:
            cantidad_demandada = demanda.cantidad
        elif demanda_predecida:
            cantidad_demandada = demanda_predecida.cantidad
        
        demanda_diaria = cantidad_demandada / 30

        return demanda_diaria
    
    def calcular_punto_de_pedido(self):
        # Solo para artículos con modelo inventario lote fijo

        demora_proveedor = int(self.detalle_proveedor_predeterminado.tiempo_demora)
        demanda_diaria = self.calcular_demanda_diaria()
        stock_seguridad = self.calcular_stock_de_seguridad()

        punto_de_pedido = demanda_diaria * demora_proveedor + stock_seguridad

        return punto_de_pedido
    
    def calcular_lote_a_comprar(self):
        if self.modelo_inventario.nombre == 'Lote fijo' and self.detalle_proveedor_predeterminado:
            demanda=self.calcular_demanda_diaria()*30
            costo_almacenamiento= self.costo_almacenamiento
            costo_pedido= self.costo_de_pedido + self.detalle_proveedor_predeterminado.costo_pedido_proveedor
            lote= math.sqrt(2*demanda*costo_pedido/costo_almacenamiento)
            return int(lote)
            #Stock seguridad
        elif self.modelo_inventario.nombre == 'Intervalo fijo' and self.detalle_proveedor_predeterminado:
            tiempo_pedido = self.tiempo_de_pedido 
            tiempo_demora_proveedor = self.detalle_proveedor_predeterminado.tiempo_demora
            demanda_diaria = self.calcular_demanda_diaria()
            stock=self.stock
            stock_seguridad= self.calcular_stock_de_seguridad()

            lote=(tiempo_pedido+tiempo_demora_proveedor)*demanda_diaria - (stock-stock_seguridad)
            return int(lote)
        
        elif not self.detalle_proveedor_predeterminado:
            lote=0
            return int(lote)
        else:
            raise ValueError("El articulo no tiene un modelo de inventario asignado o no tiene un proveedor predeterminado")
        
    
    
class OrdenCompra(db.Model):
    __tablename__ = 'orden_compra'
    lote = db.Column(db.Integer, nullable=False)
    nro_orden_compra = db.Column(db.Integer, primary_key=True)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado_orden_compra.id'), nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.id'), nullable=False)
    detalle_proveedor_id= db.Column(db.Integer, db.ForeignKey('detalle_proveedor.id'), nullable=False)


class Venta(db.Model):
    __tablename__ = 'venta'
    nro_venta = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, default=func.now())
    cantidad = db.Column(db.Integer, nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.codigo_articulo'), nullable=False)
    articulo = db.relationship('Articulo', backref='ventas') # agregue este para traer el articulo de la venta

    def calcular_demanda_mes(articulo, mes, año):
        demanda_mes = db.session.query(func.sum(Venta.cantidad)).\
            filter_by(articulo_id=articulo.id).\
            filter(func.strftime('%m', Venta.fecha) == mes).\
            filter(func.strftime('%Y', Venta.fecha) == año).scalar()

        return demanda_mes or 0
    

class Demanda(db.Model):
    __tablename__ = 'demanda'
    id = db.Column(db.Integer, primary_key=True)
    año = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.id'), nullable=False)

  
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


