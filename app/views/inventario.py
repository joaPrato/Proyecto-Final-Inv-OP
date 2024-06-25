from flask import Blueprint, render_template, request, redirect, url_for, jsonify # type: ignore
from app import db
from app.models import *
from app.models import Articulo, OrdenCompra

bp = Blueprint('inventario', __name__, url_prefix='/inventario')

@bp.route('/', methods=['GET', 'POST'])

def articulos_a_reponer_bajo_stock():
    # Obtener todos los artículos
    articulos = Articulo.query.all()
    
    # Filtrar artículos que tienen stock <= calcular_punto_de_pedido
    articulos_bajo_stock = [articulo for articulo in articulos if articulo.stock <= articulo.calcular_punto_de_pedido()]
    
    # Filtrar artículos sin órdenes de compra pendientes
    articulos_a_reponer = []
    for articulo in articulos_bajo_stock:
        orden_pendiente = OrdenCompra.query.filter_by(articulo_id=articulo.id, estado_id='Pendiente').first()
        if not orden_pendiente:
            articulos_a_reponer.append(articulo)
    
    # Filtrar artículos bajo el stock de seguridad
    articulos_bajo_stock_seguridad = [articulo for articulo in articulos if articulo.stock <= articulo.calcular_stock_de_seguridad]

    return render_template('inventario/articulos_a_reponer_bajo_stock.html', articulos_a_reponer=articulos_a_reponer,
                                                                  articulos_bajo_stock_seguridad=articulos_bajo_stock_seguridad)

