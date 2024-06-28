from datetime import date, timedelta
import datetime
from sqlalchemy import extract, func,desc
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
    def error_predecir_promedio_movil(articulo_id, cantidad_de_periodos):
        #Buscamos la cantidad de periodos que vamos a predecir para generar el error
        parametro_general= ParametrosGeneralesPrediccion.query.first()
        periodos_a_predecir= parametro_general.cantidad_periodos_a_predecir
        modelo_calculo_error= parametro_general.modelo_calculo_error

        #Buscamos la cantidad de demandas reales necesarias para calcular el error
        demandas_reales = Demanda.query.filter_by(articulo_id=articulo_id).order_by(Demanda.fecha_d.desc()).limit(cantidad_de_periodos+periodos_a_predecir).all()
        #Verificamos que haya suficientes demanda para calcular el error
        if len(demandas_reales) < cantidad_de_periodos+periodos_a_predecir:
                raise ValueError("No hay suficientes datos históricos para el calcular el error")
        demandas_predecida = []
        #Calculo del predicciones
        for i in range(periodos_a_predecir):
            #Toma las demandas anteriores a la del mes que vamos a predecir
            subconjunto_demandas = demandas_reales[i+1: i+1+ cantidad_de_periodos]
            # Calcular el promedio
            prediccion = sum(demanda.cantidad for demanda in subconjunto_demandas) / cantidad_de_periodos
            demandas_predecida.append(prediccion)
        
        #Calculamo el error
        error=modelo_calculo_error.calcular_error(demandas_reales[0:periodos_a_predecir ],demandas_predecida)
        return error
    
    @staticmethod
    def predecir_promedio_movil(articulo_id, cantidad_de_periodos,mes, año):
         # Obtener la fecha de referencia (mes y año)
        fecha_referencia = datetime(year=año, month=mes, day=1)

        # Obtener los últimos n valores de demanda real que incluyan la fecha de referencia y los n periodos anteriores
        demandas = Demanda.query.filter(
            Demanda.articulo_id == articulo_id,
            Demanda.fecha_d <= fecha_referencia,  
            Demanda.fecha_d >= fecha_referencia - timedelta(days=31*cantidad_de_periodos), 
        ).order_by(Demanda.fecha_d.desc()).all()

        if len(demandas) < cantidad_de_periodos:
            raise ValueError("No hay suficientes datos históricos para el número de periodos solicitado")

        # Calcular el promedio
        subconjunto_demandas = demandas[1: cantidad_de_periodos] #Sub conjunto con las demandas realeas, anteriores al mes que estoy prediciendo
        promedio = sum(demanda.cantidad for demanda in subconjunto_demandas) / cantidad_de_periodos
        return int(promedio)

    @staticmethod
    def error_predecir_promedio_movil_ponderado(articulo_id, cantidad_de_periodos, factores_ponderacion):
        #Buscamos la cantidad de periodos que vamos a predecir para generar el error
        parametro_general= ParametrosGeneralesPrediccion.query.first()
        periodos_a_predecir= parametro_general.cantidad_periodos_a_predecir
        modelo_calculo_error= parametro_general.modelo_calculo_error

        #Buscamos la cantidad de demandas reales necesarias para calcular el error
        demandas_reales = Demanda.query.filter_by(articulo_id=articulo_id).order_by(Demanda.fecha_d.desc()).limit(cantidad_de_periodos+periodos_a_predecir).all()
        #Verificamos que haya suficientes demanda para calcular el error
        if len(demandas_reales) < cantidad_de_periodos+periodos_a_predecir:
                raise ValueError("No hay suficientes datos históricos para el calcular el error")
        demandas_predecida = []
        #Calculo del predicciones
        for i in range(periodos_a_predecir):
            #Toma las demandas anteriores a la del mes que vamos a predecir
            subconjunto_demandas = demandas_reales[i+1: i+1+ cantidad_de_periodos]
            # Calcular el promedio
            prediccion = sum(demanda.cantidad * factor for demanda,factor in zip(subconjunto_demandas,factores_ponderacion)) / cantidad_de_periodos
            demandas_predecida.append(prediccion)
        
        #Calculamo el error
        error=modelo_calculo_error.calcular_error(demandas_reales[0:periodos_a_predecir ],demandas_predecida)
        return error
    
    @staticmethod
    def predecir_promedio_movil_ponderado(articulo_id, cantidad_de_periodos, factores_ponderacion,mes,año):
        # Obtener la fecha de referencia (mes y año)
        fecha_referencia = datetime(year=año, month=mes, day=1)

        # Obtener los últimos n valores de demanda real que incluyan la fecha de referencia y los n periodos anteriores
        demandas = Demanda.query.filter(
            Demanda.articulo_id == articulo_id,
            Demanda.fecha_d <= fecha_referencia,  
            Demanda.fecha_d >= fecha_referencia - timedelta(days=31*cantidad_de_periodos), 
        ).order_by(Demanda.fecha_d.desc()).all()

        if len(demandas) < cantidad_de_periodos:
            raise ValueError("No hay suficientes datos históricos para el número de periodos solicitado")

        # Calcular el promedio
        subconjunto_demandas = demandas[1: cantidad_de_periodos] #Sub conjunto con las demandas realeas, anteriores al mes que estoy prediciendo
        promedio = sum(demanda.cantidad * factor  for demanda , factor in zip(subconjunto_demandas,factores_ponderacion)) / cantidad_de_periodos
        return int(promedio)

    @staticmethod
    def error_predecir_promedio_movil_suavizado(articulo_id, alfa, prediccion_raiz):
        #Buscamos la cantidad de periodos que vamos a predecir para generar el error
        parametro_general= ParametrosGeneralesPrediccion.query.first()
        periodos_a_predecir= parametro_general.cantidad_periodos_a_predecir
        modelo_calculo_error= parametro_general.modelo_calculo_error

        # Obtener demandas reales desde la mas reciente a la mas antigua
        demandas_reales = Demanda.query.filter_by(articulo_id=articulo_id).order_by(DemandaPredecida.año.desc(), DemandaPredecida.mes.desc()).limit(periodos_a_predecir+1).all()
        #Las ordenamos desde la mas antigua a la mas nueva
        demandas_reales.reverse()

        if len(demandas_reales) < periodos_a_predecir+1:
                raise ValueError("No hay suficientes datos históricos para el calcular el error")

        if prediccion_raiz is None:
            # Si no se proporciona una predicción raíz, usar la demanda del último periodo como predicción inicial
            prediccion_raiz = demandas_reales[0].cantidad

        # Calculo de predicciones 
        demandas_predecida = []
        for i in range(periodos_a_predecir):
            if i == 0 :
                demanda_predecida= prediccion_raiz + alfa*(demandas_reales[i]-prediccion_raiz)
                demandas_predecida.append(demanda_predecida)
            else:
                demanda_predecida= demandas_predecida[i-1] + alfa*(demandas_reales[i]-demandas_predecida[i-1])
                demandas_predecida.append(demanda_predecida)
        

        error=modelo_calculo_error.calcular_error(demandas_reales[1:periodos_a_predecir+1 ],demandas_predecida)
        return error
    
    def predecir_promedio_movil_suavizado(articulo_id, alfa, prediccion_raiz):
        # Obtener el último valor de demanda
        ultima_demanda = DemandaPredecida.query.filter_by(articulo_id=articulo_id).order_by(DemandaPredecida.año.desc(), DemandaPredecida.mes.desc()).first()
        if not ultima_demanda:
            raise ValueError("No hay datos históricos para el artículo solicitado")

        if prediccion_raiz is None:
            # Si no se proporciona una predicción raíz, usar la demanda del último periodo como predicción inicial
            prediccion_raiz = ultima_demanda.cantidad

        # Calcular la predicción usando suavización exponencial
        prediccion = prediccion_raiz + alfa * (ultima_demanda.cantidad - prediccion_raiz)
        return int(prediccion)

    @staticmethod
    def error_predecir_regresion_lineal(articulo_id):
        #Buscamos la cantidad de periodos que vamos a predecir para generar el error
        parametro_general= ParametrosGeneralesPrediccion.query.first()
        periodos_a_predecir= parametro_general.cantidad_periodos_a_predecir
        modelo_calculo_error= parametro_general.modelo_calculo_error

        #Trae la ultimas 50 demandas ordenadas desde la mas antigua a la mas nueva
        demandas = Demanda.query.filter_by(articulo_id=articulo_id).order_by(Demanda.fecha_d.asc()).limit(50).all()
        # Dividir la lista de demandas
        demandas_para_calculo = demandas[:len(demandas)-periodos_a_predecir]
        demandas_reales = demandas[-periodos_a_predecir:]
        if len(demandas) < 2:
            raise ValueError("No hay suficientes datos históricos para realizar la predicción")

        n = len(demandas_para_calculo)
        suma_tiempo = sum(range(1, n + 1))
        suma_demanda = sum(demanda.cantidad for demanda in demandas_para_calculo)
        promedio_tiempo = suma_tiempo / n
        promedio_demanda = suma_demanda / n

        suma_tiempo_demanda = sum((i - promedio_tiempo) * (demandas_para_calculo[i - 1].cantidad - promedio_demanda) for i in range(1, n + 1))
        suma_tiempo_cuadrado = sum((i - promedio_tiempo) ** 2 for i in range(1, n + 1))

        m = suma_tiempo_demanda / suma_tiempo_cuadrado
        b = promedio_demanda - m * promedio_tiempo

        #Calculo predicciones 
        demandas_predecida = []
        for i in range(n,n+periodos_a_predecir):
            demanda_predecida=m * (i + 1) + b
            demandas_predecida.append(demanda_predecida)

        #Calulo de error
        error=modelo_calculo_error.calcular_error(demandas_reales,demandas_predecida)
        return error

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

    @staticmethod #Creo que no lo pide esto
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
    def calcular_indice_estacionalidad(articulo_id, mes,año):
        # Consulta para obtener las demandas de los últimos tres años
        años = [año - i for i in range(1, 4)]  
        demandas= Demanda.query.filter(
            Demanda.articulo_id == articulo_id,
            extract('year', Demanda.fecha_d).in_(años)
        ).all()
        
        if len(demandas) < 12 * 3:
            raise ValueError("No hay suficientes datos históricos para realizar la predicción")

        demanda_promedio_historica = sum(demanda.cantidad for demanda in demandas) / len(demandas)
        demanda_promedio_mes= 0
        for demanda in demandas:
            if demanda.fecha_d.month == mes:
                demanda_promedio_mes = demanda_promedio_mes + demanda.cantidad
        #Este indice se multiplica por la prediccion obtenida por algun metodo. Eso ajusta la estacionalidad
        indice_de_estacionalidad_mensual=demanda_promedio_mes/demanda_promedio_historica

        return indice_de_estacionalidad_mensual

    @staticmethod #No entiendo bien que es lo que hace 
    def predecir_ajuste_estacional(articulo_id, indices_estacionales):
        demandas = Demanda.query.filter_by(articulo_id=articulo_id).order_by(Demanda.fecha_d.asc()).all()
        if len(demandas) < 12 * 3:
            raise ValueError("No hay suficientes datos históricos para realizar la predicción")

        demanda_promedio = sum(demanda.cantidad for demanda in demandas) / len(demandas)
        demanda_estacional_ajustada = [demanda.cantidad / indices_estacionales[i % 12] for i, demanda in enumerate(demandas)]
        demanda_promedio_estacional = sum(demanda_estacional_ajustada) / len(demanda_estacional_ajustada)

        predicciones = [demanda_promedio_estacional * indices_estacionales[i % 12] for i in range(12)]
        return predicciones

    @staticmethod #Creo que no lo pide esto
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
  
    def calcular_error(self,demandas_reales,demandas_predecidas):
        n=len(demandas_reales)
        error_total=0
        if len(demandas_predecidas) != len(demandas_reales):
            raise ValueError("Al calcular el error, las listas demanda real y demanda predecida no son del mismo tamaño")
        if self.nombre == 'MAD':
             error_total = (sum(abs(demanda_real.cantidad - demanda_predecida) for demanda_real, demanda_predecida in zip(demandas_reales, demandas_predecidas)))/n
        if self.nombre == 'MSE':
             error_total = (sum(math.sqrt(demanda_real.cantidad - demanda_predecida) for demanda_real, demanda_predecida in zip(demandas_reales, demandas_predecidas)))/n     
        if self.nombre == 'MAPE':
             error_total = (sum(100*abs(demanda_real.cantidad - demanda_predecida)/demanda_real.cantidad for demanda_real, demanda_predecida in zip(demandas_reales, demandas_predecidas)))/n  
        return error_total

class ModeloInventario(db.Model):
    __tablename__ = 'modelo_inventario'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    #Relaciones
    articulos=db.relationship('Articulo', lazy='dynamic',backref='modelo_inventario')


