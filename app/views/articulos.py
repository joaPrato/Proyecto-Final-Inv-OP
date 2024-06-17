from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app import db
from app.models import *

bp = Blueprint('articulos', __name__, url_prefix='/articulos')

@bp.route('/')
def get_articulos():
    
    modelos_inventario = ModeloInventario.query.all()
    articulos = Articulo.query.all()
    return render_template('articulos/index.html', articulos=articulos,modelos_inventario=modelos_inventario)

@bp.route('/', methods=['POST'])
def create():
    data=request.form
    nuevo_articulo = Articulo(
        codigo_articulo=data['codigo_articulo'],
        nombre_articulo=data['nombre_articulo'],
        coeficiente_seguridad= data['coeficiente_seguridad'],
        costo_almacenamiento= data['costo_almacenamiento'],
        costo_de_pedido= data['costo_de_pedido'],
        stock=int(data['stock']) if data['stock'].strip() else 0,
        tiempo_de_pedido=int(data.get('tiempo_de_pedido')) if data['tiempo_de_pedido'].strip() else None,
        detalle_proveedor_predeterminado_id=None,
        modelo_inventario_id= data['modelo_inventario_id']
    )
    db.session.add(nuevo_articulo)
    db.session.commit()
    return redirect(url_for('articulos.get_articulos')),print(jsonify(nuevo_articulo.serialize()), 201)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    articulos = Articulo.query.get_or_404(id)
    if request.method == 'POST':
        # Código para editar un artículo
        pass
    return render_template('articulos/edit.html', articulos=articulos)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    articulos = Articulo.query.get_or_404(id)
    # Código para eliminar un artículo
    pass
