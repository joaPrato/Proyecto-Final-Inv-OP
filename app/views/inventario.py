from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app import db
from app.models import *

bp = Blueprint('inventario', __name__, url_prefix='/inventario')

@bp.route('/', methods=['GET', 'POST'])

def articulos_a_reponer():
    # Filtrar artículos que tienen stock <= punto_pedido
    articulos = Articulo.query.filter(Articulo.stock <= Articulo.punto_pedido).all()
    
    # Filtrar órdenes de compra que no están pendientes
    articulos_a_reponer = []
    for articulo in articulos:
        orden_pendiente = OrdenCompra.query.filter_by(articulo_id=articulo.id, estado_id='Pendiente').first()
        if not orden_pendiente:
            articulos_a_reponer.append(articulo)
    
    return render_template('articulos_a_reponer.html', articulos=articulos_a_reponer)
