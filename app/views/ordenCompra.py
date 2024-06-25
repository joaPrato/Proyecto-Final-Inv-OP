
from datetime import timedelta
from app.forms import OrdenCompraForm
from flask import Blueprint, render_template,flash, request, redirect, url_for,flash, jsonify # type: ignore
from app import db
from app.models import *

bp = Blueprint('ordenCompra', __name__, url_prefix='/ordenCompra')

@bp.route('/', methods=['GET', 'POST'])
def get_ordenes_compra():
    estado_orden_compra=EstadoOrdenCompra.query.filter_by(nombre='En curso').first()
    form = OrdenCompraForm()
    form.articulo_id.choices = [(a.id, a.nombre_articulo) for a in Articulo.query.all()]
    form.estado_id.choices = [(estado_orden_compra.id, estado_orden_compra.nombre)]
    proveedores_unicos = {d.proveedor for d in DetalleProveedor.query.all()}
    form.detalle_proveedor_id.choices = [(proveedor.id, proveedor.nombre) for proveedor in proveedores_unicos]
  

    if form.validate_on_submit():
        
        orden_compra= OrdenCompra.query.filter_by(articulo_id=form.articulo_id.data,estado_id=EstadoOrdenCompra.query.filter_by(nombre='En curso').first().id).first()
        detalle_proveedor = DetalleProveedor.query.filter_by(proveedor_id=form.detalle_proveedor_id.data, articulo_id=form.articulo_id.data).first()
        if not detalle_proveedor:
            flash('El proveedor no vende este artículo', 'danger')
        elif orden_compra :
            flash('El articulo ya tiene una orden de compra en curso', 'danger')
        else:
            nueva_orden = OrdenCompra(
                lote=form.lote.data,
                articulo_id=form.articulo_id.data,
                estado_id=form.estado_id.data,
                detalle_proveedor_id=detalle_proveedor.id
            )
            try:
                db.session.add(nueva_orden)
                db.session.commit()
                flash('Orden de compra creada con éxito', 'success')
                return redirect(url_for('ordenCompra.get_ordenes_compra'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al crear la orden de compra: {str(e)}', 'danger')

    if form.errors:
        flash(f'Errores en el formulario: {form.errors}', 'danger')
        print("Errores del formulario:", form.errors)

    ordenes_compra = OrdenCompra.query.all()
    articulos= Articulo.query.all()

    return render_template('ordenes_compra/lista_ordenes_compra.html', ordenes_compra=ordenes_compra, form=form,articulos=articulos)

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def edit_orden_compra(id):
    orden = OrdenCompra.query.get_or_404(id)
    form = OrdenCompraForm(obj=orden)
    form.articulo_id.choices = [(a.id, a.nombre_articulo) for a in Articulo.query.all()]
    form.detalle_proveedor_id.choices= [(orden.detalle_proveedor.id,orden.detalle_proveedor.proveedor.nombre)]
    form.estado_id.choices = [(e.id, e.nombre) for e in EstadoOrdenCompra.query.all()]

    if form.validate_on_submit():

        orden.lote = form.lote.data
        orden.articulo_id = form.articulo_id.data
        orden.estado_id = form.estado_id.data

        try:
            db.session.commit()
            flash('Orden de compra actualizada con éxito', 'success')
            return redirect(url_for('ordenCompra.get_ordenes_compra'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la orden de compra: {str(e)}', 'danger')

    return render_template('ordenes_compra/editar_orden_compra.html', form=form, orden=orden)

@bp.route('/eliminar/<int:id>')
def eliminar_orden_compra(id):
    orden = OrdenCompra.query.get_or_404(id)
    db.session.delete(orden)
    db.session.commit()
    flash('Orden de compra eliminada con éxito', 'success')
    return redirect(url_for('ordenCompra.get_ordenes_compra'))


@bp.route('/crear/<int:id>', methods=['GET', 'POST'])
def crear_orden_compra_articulo (id):
    articulo = Articulo.query.get_or_404(id)
    estado_orden_compra=EstadoOrdenCompra.query.filter_by(nombre='En curso').first()

    form = OrdenCompraForm()
    form.articulo_id.choices = [(articulo.id, articulo.nombre_articulo)]
    form.estado_id.choices = [(estado_orden_compra.id, estado_orden_compra.nombre)]
    form.detalle_proveedor_id.choices = [(dp.id, dp.proveedor.nombre) for dp in articulo.detalles_proveedor]

    lote=articulo.calcular_lote_a_comprar()

    if form.validate_on_submit():
        orden_compra= OrdenCompra.query.filter_by(articulo_id=form.articulo_id.data,estado_id=EstadoOrdenCompra.query.filter_by(nombre='En curso').first().id).first()
        if orden_compra :
            flash('El articulo ya tiene una orden de compra en curso', 'danger')
        else :
            nueva_orden = OrdenCompra(
                lote=form.lote.data,
                estado_id=form.estado_id.data,
                articulo_id=articulo.id,
                detalle_proveedor_id=form.detalle_proveedor_id.data
            )
            try:
                db.session.add(nueva_orden)
                db.session.commit()
                flash('Orden de compra creada con éxito', 'success')
                return redirect(url_for('ordenCompra.get_ordenes_compra'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al crear la orden de compra: {str(e)}', 'danger')
    
    return render_template('ordenes_compra/crear_orden_compra_articulo.html', form=form, articulo=articulo,lote=lote)


@bp.route('/actualizar_orden_finalizada', methods=['GET', 'POST'])
def actualizar_orden_finalizada():
    ordenes = OrdenCompra.query.filter_by(estado_id=EstadoOrdenCompra.query.filter_by(nombre='En curso').first().id).all()
    for orden in ordenes :
        demora = timedelta(days=orden.detalle_proveedor.tiempo_demora)
        if date.today()>=(orden.fecha + demora) :
            estado_orden_compra=EstadoOrdenCompra.query.filter_by(nombre='Finalizado').first()
            orden.estado_id =estado_orden_compra.id
            orden.articulo.stock= orden.articulo.stock + orden.lote
    try:
        db.session.commit()
        flash('Orden de compra actualizadas con exito', 'success')
        return redirect(url_for('ordenCompra.get_ordenes_compra'))
    except Exception as e:
        db.session.rollback()
        return f'Error al actualizar el stock: {str(e)}', 500




