from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify # type: ignore
from app import db
from app.models import *
from app.forms import ArticuloFormCrear,ArticuloFormEditar

bp = Blueprint('articulos', __name__, url_prefix='/articulos')
@bp.route('/', methods=['GET', 'POST'])
def get_articulos():
    form_articulo_crear = ArticuloFormCrear()
    form_articulos_editar= ArticuloFormEditar()
    
    form_articulo_crear.modelo_inventario_id.choices = [(m.id, m.nombre) for m in ModeloInventario.query.all()]
    #form_articulos_editar.modelo_inventario_id.choices =   [(m.id, m.nombre) for m in ModeloInventario.query.all()]
    #form_articulos_editar.detalle_proveedor_predeterminado_id.choices = [(d.id, d.proveedor.nombre) for d in DetalleProveedor.query.all()]


    if form_articulo_crear.validate_on_submit():
        stock = form_articulo_crear.stock.data if form_articulo_crear.stock.data is not None else 0
        tiempo_de_pedido = form_articulo_crear.tiempo_de_pedido.data if form_articulo_crear.tiempo_de_pedido.data is not None else 0


        nuevo_articulo = Articulo( #Argregar lo del proveedor predeterminado
            codigo_articulo=form_articulo_crear.codigo_articulo.data,
            nombre_articulo=form_articulo_crear.nombre_articulo.data,
            coeficiente_seguridad=form_articulo_crear.coeficiente_seguridad.data,
            costo_almacenamiento=form_articulo_crear.costo_almacenamiento.data,
            costo_de_pedido=form_articulo_crear.costo_de_pedido.data,
            stock=stock,
            tiempo_de_pedido=tiempo_de_pedido,
            detalle_proveedor_predeterminado_id=None,
            modelo_inventario_id=form_articulo_crear.modelo_inventario_id.data
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
    return render_template('articulos/index.html', articulos=articulos, form_articulo_crear=form_articulo_crear,form_articulos_editar=form_articulos_editar)

@bp.route('/editar/<int:id>', methods=['GET','POST'])
def edit(id):
    articulo = Articulo.query.get_or_404(id)
    form = ArticuloFormEditar(obj=articulo)

    # Configuración de choices para el formulario de edición
    form.modelo_inventario_id.choices = [(m.id, m.nombre) for m in ModeloInventario.query.all()]
    form.detalle_proveedor_predeterminado_id.choices = [(d.id, d.proveedor.nombre) for d in DetalleProveedor.query.filter_by(articulo_id=articulo.id).all()]
    

    if form.validate_on_submit():
        articulo.codigo_articulo = form.codigo_articulo.data
        articulo.nombre_articulo = form.nombre_articulo.data
        articulo.coeficiente_seguridad = form.coeficiente_seguridad.data
        articulo.costo_almacenamiento = form.costo_almacenamiento.data
        articulo.costo_de_pedido = form.costo_de_pedido.data
        articulo.stock = form.stock.data
        articulo.tiempo_de_pedido = form.tiempo_de_pedido.data
        articulo.modelo_inventario_id = form.modelo_inventario_id.data
        articulo.detalle_proveedor_predeterminado_id = form.detalle_proveedor_predeterminado_id.data

        try:
            db.session.commit()
            flash('Artículo actualizado con éxito', 'success')
            return redirect(url_for('articulos.get_articulos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el artículo: {str(e)}', 'danger')

    # Si el formulario no es valido
    return render_template('articulos/editar_articulo.html', form=form, articulo=articulo)

    

@bp.route('/eliminar/<int:id>')
def eliminar(id):
    articulo = Articulo.query.get_or_404(id)
    db.session.delete(articulo)
    db.session.commit()
    flash('Artículo eliminado con éxito', 'success')
    return redirect(url_for('articulos.get_articulos'))
