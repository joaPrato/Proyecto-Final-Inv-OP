from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, jsonify # type: ignore
from app import db
from app.models import *
from app.models import Articulo, OrdenCompra

bp = Blueprint('inventario', __name__, url_prefix='/inventario')

@bp.route('/', methods=['GET', 'POST'])

def articulos_a_reponer_bajo_stock():
    # Obtener todos los artículos
    articulos = Articulo.query.all()
    articulos_a_reponer = []

    # Filtrar artículos con modelo lote fijo que tienen stock <= calcular_punto_de_pedido
    articulos_bajo_stock_modelo_lote_fijo = [articulo for articulo in articulos if articulo.stock <= articulo.calcular_punto_de_pedido() and articulo.modelo_inventario.nombre == 'Lote fijo']

    # Filtrar artículos con modelo Intervalo fijo que hayan pasado el tiempo de pedido desde la fecha de la última orden de compra
    # Fecha actual
    fecha_actual = datetime.now().date()
    for articulo in articulos:
        if articulo.modelo_inventario.nombre == 'Intervalo fijo':
            ultima_orden = OrdenCompra.query.filter_by(articulo_id=articulo.id).order_by(OrdenCompra.fecha.desc()).first()
            if ultima_orden:
                dias_desde_ultima_orden = (fecha_actual - ultima_orden.fecha).days
                if articulo.tiempo_de_pedido <= dias_desde_ultima_orden:
                    articulos_a_reponer.append(articulo)
            else:
                articulos_a_reponer.append(articulo)

    
    articulos_bajo_stock_modelo_lote_fijo = [articulo for articulo in articulos if articulo.stock <= articulo.calcular_punto_de_pedido() and articulo.modelo_inventario.nombre == 'Lote fijo']

    # Filtrar artículos con modelo lote fijo sin órdenes de compra pendientes
    for articulo in articulos_bajo_stock_modelo_lote_fijo:
        orden_en_curso = OrdenCompra.query.filter_by(articulo_id=articulo.id, estado_id='En curso').first()
        if not orden_en_curso:
            articulos_a_reponer.append(articulo)


    # Filtrar artículos bajo el stock de seguridad
    articulos_bajo_stock_seguridad = [articulo for articulo in articulos if articulo.stock <= articulo.calcular_stock_de_seguridad()]

    return render_template('inventario/articulos_a_reponer_bajo_stock.html', articulos_a_reponer=articulos_a_reponer,
                                                                  articulos_bajo_stock_seguridad=articulos_bajo_stock_seguridad)

