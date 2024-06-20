from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify
from app import db
from app.models import *
from app.forms import ArticuloFormCrearEditar

bp = Blueprint('articulos', __name__, url_prefix='/articulos')

@bp.route('/', methods=['GET', 'POST'])
def get_articulos():
    form = ArticuloFormCrearEditar()
    form.modelo_inventario_id.choices = [(m.id, m.nombre) for m in ModeloInventario.query.all()]

    if form.validate_on_submit():
        stock = form.stock.data if form.stock.data is not None else 0
        tiempo_de_pedido = form.tiempo_de_pedido.data if form.tiempo_de_pedido.data is not None else 0


        nuevo_articulo = Articulo(
            codigo_articulo=form.codigo_articulo.data,
            nombre_articulo=form.nombre_articulo.data,
            coeficiente_seguridad=form.coeficiente_seguridad.data,
            costo_almacenamiento=form.costo_almacenamiento.data,
            costo_de_pedido=form.costo_de_pedido.data,
            stock=stock,
            tiempo_de_pedido=tiempo_de_pedido,
            detalle_proveedor_predeterminado_id=None,
            modelo_inventario_id=form.modelo_inventario_id.data
        )
        try:
            db.session.add(nuevo_articulo)
            db.session.commit()
            flash('Artículo creado con éxito', 'success')
            return redirect(url_for('articulos.get_articulos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el artículo: {str(e)}', 'danger')

    articulos = Articulo.query.all()
    return render_template('articulos/index.html', articulos=articulos, form=form)

@bp.route('/editar/<int:id>', methods=['POST'])
def edit(id):
    articulo = Articulo.query.get_or_404(id)
    form = ArticuloFormCrearEditar(obj=articulo)
    form.modelo_inventario_id.choices = [(m.id, m.nombre) for m in ModeloInventario.query.all()]

    if form.validate_on_submit():
        articulo.codigo_articulo = form.codigo_articulo.data
        articulo.nombre_articulo = form.nombre_articulo.data
        articulo.coeficiente_seguridad = form.coeficiente_seguridad.data
        articulo.costo_almacenamiento = form.costo_almacenamiento.data
        articulo.costo_de_pedido = form.costo_de_pedido.data
        articulo.stock = form.stock.data
        articulo.tiempo_de_pedido = form.tiempo_de_pedido.data
        articulo.modelo_inventario_id = form.modelo_inventario_id.data

        try:
            db.session.commit()
            flash('Artículo actualizado con éxito', 'success')
            return redirect(url_for('articulos.get_articulos'))
        except Exception as e:
            print(f"Error al actualizar artículo: {str(e)}")
            db.session.rollback()
            flash('Error al actualizar artículo', 'danger')

    # Si el formulario no es valido
    return redirect(url_for('articulos.get_articulos', form=form, articulo_id=articulo.id))

    

@bp.route('/eliminar/<int:id>')
def eliminar(id):
    articulo = Articulo.query.get_or_404(id)
    db.session.delete(articulo)
    db.session.commit()
    flash('Artículo eliminado con éxito', 'success')
    return redirect(url_for('articulos.get_articulos'))
