from datetime import date
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

        return int(stock_de_seguridad)
    




    def calcular_demanda_diaria(self):
        # Obtener la última demanda
        demanda = Demanda.query.filter_by(articulo_id=self.id).order_by(desc(Demanda.fecha_d)).first()
        # Obtener la última demanda predecida
        demanda_predecida = DemandaPredecida.query.filter_by(articulo_id=self.id).order_by(desc(DemandaPredecida.año), desc(DemandaPredecida.mes)).first()

        cantidad_demandada = 0

        # Verificar si se encontró alguna demanda o demanda predecida
        if demanda and demanda_predecida:
            # Comparar las fechas para determinar cuál usar
            fecha_predecida = date(demanda_predecida.año, demanda_predecida.mes, 1)
            if demanda.fecha_d > fecha_predecida:
                cantidad_demandada = demanda.cantidad
            else:
                cantidad_demandada = demanda_predecida.cantidad
        elif demanda:
            cantidad_demandada = demanda.cantidad
        elif demanda_predecida:
            cantidad_demandada = demanda_predecida.cantidad

        demanda_diaria = cantidad_demandada / 30

        return int(demanda_diaria)


    
    def calcular_punto_de_pedido(self):
        # Solo para artículos con modelo inventario lote fijo

        demora_proveedor = int(self.detalle_proveedor_predeterminado.tiempo_demora)
        demanda_diaria = self.calcular_demanda_diaria()
        stock_seguridad = self.calcular_stock_de_seguridad()

        punto_de_pedido = demanda_diaria * demora_proveedor + stock_seguridad

        return int(punto_de_pedido)
    
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
    fecha= db.Column(db.Date, nullable=False,default=func.current_date())
    estado_id = db.Column(db.Integer, db.ForeignKey('estado_orden_compra.id'), nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.id'), nullable=False)
    detalle_proveedor_id= db.Column(db.Integer, db.ForeignKey('detalle_proveedor.id'), nullable=False)


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
        mes_año = fecha.strftime('%Y-%m')
        
        demanda_existente = cls.query.filter_by(articulo_id=articulo_id).\
            filter(func.strftime('%Y-%m', cls.fecha_d) == mes_año).first()
        
        return demanda_existente is not None
    
    
class DemandaPredecida(db.Model):
    __tablename__ = 'demanda_predecida'
    id = db.Column(db.Integer, primary_key=True)
    año = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.id'), nullable=False)
    modelo_prediccion_id = db.Column(db.Integer, db.ForeignKey('modelo_prediccion_demanda.id'), nullable=False)
    error_calculado = db.Column(db.Float, nullable=True)
    
    @staticmethod
    def predecir_promedio_movil(articulo_id, periodos):
        # Obtener los últimos n valores de demanda real
        demandas = Demanda.query.filter_by(articulo_id=articulo_id).order_by(Demanda.fecha_d.desc()).limit(periodos).all()
        if len(demandas) < periodos:
            raise ValueError("No hay suficientes datos históricos para el número de periodos solicitado")

        # Calcular el promedio
        promedio = sum(demanda.cantidad for demanda in demandas) / periodos
        return promedio

    @staticmethod
    def predecir_promedio_movil_ponderado(articulo_id, periodos, factores_ponderacion):
        # Obtener los últimos n valores de demanda
        demandas = Demanda.query.filter_by(articulo_id=articulo_id).order_by(Demanda.fecha_d.desc()).limit(periodos).all()
        if periodos != len(factores_ponderacion):
            raise ValueError("La cantidad de periodos y factores debe ser igual")
        if len(demandas) < periodos:
            raise ValueError("No hay suficientes datos históricos para el número de periodos solicitado")

        # Calcular el promedio ponderado
        suma_ponderada = sum(demanda.cantidad * factor for demanda, factor in zip(demandas, factores_ponderacion))
        promedio_ponderado = suma_ponderada / sum(factores_ponderacion)
        return promedio_ponderado

    @staticmethod
    def predecir_promedio_movil_suavizado(articulo_id, alfa, prediccion_raiz=None):
        # Obtener el último valor de demanda
        ultima_demanda = DemandaPredecida.query.filter_by(articulo_id=articulo_id).order_by(DemandaPredecida.año.desc(), DemandaPredecida.mes.desc()).first()
        if not ultima_demanda:
            raise ValueError("No hay datos históricos para el artículo solicitado")

        if prediccion_raiz is None:
            # Si no se proporciona una predicción raíz, usar la demanda del último periodo como predicción inicial
            prediccion_raiz = ultima_demanda.cantidad

        # Calcular la predicción usando suavización exponencial
        prediccion = prediccion_raiz + alfa * (ultima_demanda.cantidad - prediccion_raiz)
        return prediccion

    @staticmethod
    def predecir_regresion_lineal(articulo_id):
        demandas = Demanda.query.filter_by(articulo_id=articulo_id).order_by(Demanda.fecha_d.asc()).all()
        if len(demandas) < 2:
            raise ValueError("No hay suficientes datos históricos para realizar la predicción")

        n = len(demandas)
        suma_tiempo = sum(range(1, n + 1))
        suma_demanda = sum(demanda.cantidad for demanda in demandas)
        promedio_tiempo = suma_tiempo / n
        promedio_demanda = suma_demanda / n

        suma_tiempo_demanda = sum((i - promedio_tiempo) * (demandas[i - 1].cantidad - promedio_demanda) for i in range(1, n + 1))
        suma_tiempo_cuadrado = sum((i - promedio_tiempo) ** 2 for i in range(1, n + 1))

        m = suma_tiempo_demanda / suma_tiempo_cuadrado
        b = promedio_demanda - m * promedio_tiempo

        prediccion = m * (n + 1) + b
        return prediccion

    @staticmethod
    def calcular_coeficiente_correlacion(articulo_id, predicciones):
        demandas = Demanda.query.filter_by(articulo_id=articulo_id).order_by(Demanda.fecha_d.asc()).all()
        if len(demandas) != len(predicciones):
            raise ValueError("El número de predicciones no coincide con el número de demandas reales")

        promedio_real = sum(demanda.cantidad for demanda in demandas) / len(demandas)
        promedio_prediccion = sum(predicciones) / len(predicciones)

        suma_real_prediccion = sum((demanda.cantidad - promedio_real) * (prediccion - promedio_prediccion) for demanda, prediccion in zip(demandas, predicciones))
        suma_real_cuadrado = sum((demanda.cantidad - promedio_real) ** 2 for demanda in demandas)
        suma_prediccion_cuadrado = sum((prediccion - promedio_prediccion) ** 2 for prediccion in predicciones)

        r_cuadrado = suma_real_prediccion ** 2 / (suma_real_cuadrado * suma_prediccion_cuadrado)
        return math.sqrt(r_cuadrado)

    @staticmethod
    def predecir_ajuste_estacional(articulo_id, indices_estacionales):
        demandas = Demanda.query.filter_by(articulo_id=articulo_id).order_by(Demanda.fecha_d.asc()).all()
        if len(demandas) < 12 * 3:
            raise ValueError("No hay suficientes datos históricos para realizar la predicción")

        demanda_promedio = sum(demanda.cantidad for demanda in demandas) / len(demandas)
        demanda_estacional_ajustada = [demanda.cantidad / indices_estacionales[i % 12] for i, demanda in enumerate(demandas)]
        demanda_promedio_estacional = sum(demanda_estacional_ajustada) / len(demanda_estacional_ajustada)

        predicciones = [demanda_promedio_estacional * indices_estacionales[i % 12] for i in range(12)]
        return predicciones

    @staticmethod
    def calcular_intervalo_confianza(articulo_id, predicciones, nivel_confianza=0.95):
        demandas = Demanda.query.filter_by(articulo_id=articulo_id).order_by(Demanda.fecha_d.asc()).all()
        if len(demandas) != len(predicciones):
            raise ValueError("El número de predicciones no coincide con el número de demandas reales")

        n = len(demandas)
        suma_error_cuadrado = sum((demanda.cantidad - prediccion) ** 2 for demanda, prediccion in zip(demandas, predicciones))
        varianza = suma_error_cuadrado / (n - 2)
        desviacion_estandar = math.sqrt(varianza)

        z = 1.96  # valor Z para un nivel de confianza del 95%
        if nivel_confianza == 0.99:
            z = 2.576
        elif nivel_confianza == 0.68:
            z = 1.0

        intervalos_confianza = [(prediccion - z * desviacion_estandar, prediccion + z * desviacion_estandar) for prediccion in predicciones]
        return intervalos_confianza

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


