from curses import flash
from app.forms import OrdenCompraForm
from flask import Blueprint, render_template, request, redirect, url_for, jsonify # type: ignore
from app import db
from app.models import *

bp = Blueprint('ordenCompra', __name__, url_prefix='/ordenCompra')

@bp.route('/', methods=['GET', 'POST'])
def get_ordenes_compra():
    form = OrdenCompraForm()
    form.articulo_id.choices = [(a.id, a.nombreArticulo) for a in Articulo.query.all()]
    form.estado_orden_id.choices = [(e.id, e.nombre) for e in EstadoOrdenCompra.query.all()]

    if form.validate_on_submit():
        nueva_orden = OrdenCompra(
            lote=form.lote.data,
            articulo_id=form.articulo_id.data,
            estado_orden_id=form.estado_orden_id.data
        )
        try:
            db.session.add(nueva_orden)
            db.session.commit()
            flash('Orden de compra creada con éxito', 'success')
            return redirect(url_for('ordenCompra.get_ordenes_compra'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la orden de compra: {str(e)}', 'danger')

    ordenes_compra = OrdenCompra.query.all()
    return render_template('ordenes_compra/lista_ordenes_compra', ordenes_compra=ordenes_compra, form=form)

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def edit_orden_compra(id):
    orden = OrdenCompra.query.get_or_404(id)
    form = OrdenCompraForm(obj=orden)
    form.articulo_id.choices = [(a.id, a.nombreArticulo) for a in Articulo.query.all()]
    form.estado_orden_id.choices = [(e.id, e.nombre) for e in EstadoOrdenCompra.query.all()]

    if form.validate_on_submit():
        orden.lote = form.lote.data
        orden.articulo_id = form.articulo_id.data
        orden.estado_orden_id = form.estado_orden_id.data

        try:
            db.session.commit()
            flash('Orden de compra actualizada con éxito', 'success')
            return redirect(url_for('ordenCompra.get_ordenes_compra'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la orden de compra: {str(e)}', 'danger')

    return render_template('ordenes_compra/editar_orden_compra', form=form, orden=orden)

@bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_orden_compra(id):
    orden = OrdenCompra.query.get_or_404(id)
    try:
        db.session.delete(orden)
        db.session.commit()
        flash('Orden de compra eliminada con éxito', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la orden de compra: {str(e)}', 'danger')

    return redirect(url_for('ordenCompra.get_ordenes_compra'))

