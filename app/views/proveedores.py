from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify # type: ignore
from app import db
from app.forms import ProveedorFrom,DetalleProveedorForm,DetalleProveedorFormEditar
from app.models import *

bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')

@bp.route('/', methods=['GET'])
def index():
    form_proveedor = ProveedorFrom()
    form_detalle_proveedor = DetalleProveedorForm()
    form_detalle_proveedor.proveedor_id.choices = [(p.id, p.nombre) for p in Proveedor.query.all()]
    form_detalle_proveedor.articulo_id.choices = [(a.id, a.nombre_articulo) for a in Articulo.query.all()]
    form_detalle_proveedor_editar = DetalleProveedorFormEditar()

    proveedores = Proveedor.query.all()
    articulos = Articulo.query.all()
    return render_template('proveedores/index.html', proveedores=proveedores, articulos=articulos,form_proveedor=form_proveedor,form_detalle_proveedor=form_detalle_proveedor,form_detalle_proveedor_editar=form_detalle_proveedor_editar)


@bp.route('/crear_proveedor', methods=['POST'])
def crear_proveedor():
    form = ProveedorFrom()

    if form.validate_on_submit():
        nuevo_proveedor=Proveedor(
            nombre=form.nombre.data
        )
        try:
            db.session.add(nuevo_proveedor)
            db.session.commit()
            flash('Proveedor creado exitosamente', 'success')
            return redirect(url_for('proveedores.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear proveedor: {e}', 'danger')
           
    
    return redirect(url_for('proveedores.index', form=form))


@bp.route('/crear_detalle_proveedor', methods=['POST'])
def crear_detalle_proveedor():
    form=DetalleProveedorForm()
     # Populate SelectField choices
    form.proveedor_id.choices = [(p.id, p.nombre) for p in Proveedor.query.all()]
    form.articulo_id.choices = [(a.id, a.nombre_articulo) for a in Articulo.query.all()]

    if form.validate_on_submit(): 
        
        nuevo_detalle_proveedor=DetalleProveedor(
            proveedor_id=form.proveedor_id.data,
            costo_pedido_proveedor=form.costo_pedido_proveedor.data,
            tiempo_demora=form.tiempo_demora.data,
            precio_articulo=form.precio_articulo.data,
            articulo_id=form.articulo_id.data
        )
        try:
            db.session.add(nuevo_detalle_proveedor)
            db.session.commit()
            flash('Detalle proveedor creado exitosamente', 'success')
            return redirect(url_for('proveedores.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear detalle provedor: {e}', 'danger')
    if form.errors:
        flash(f'Errores en el formulario: {form.errors}', 'danger')
        print("Errores del formulario:", form.errors) 
           
    
    return redirect(url_for('proveedores.index', form=form))


@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_detalle_proveedor(id):
    detalle_proveedor = DetalleProveedor.query.get_or_404(id)
    form = DetalleProveedorFormEditar(obj=detalle_proveedor)

    if form.validate_on_submit(): 
        detalle_proveedor.costo_pedido_proveedor = form.costo_pedido_proveedor.data
        detalle_proveedor.tiempo_demora = form.tiempo_demora.data
        detalle_proveedor.precio_articulo = form.precio_articulo.data

        try:
            db.session.commit()
            flash('Detalle proveedor editado exitosamente', 'success')
            return redirect(url_for('proveedores.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al editar detalle proveedor: {e}', 'danger')

    if form.errors:
        flash(f'Errores en el formulario: {form.errors}', 'danger')
        print("Errores del formulario:", form.errors)        

    return redirect(url_for('proveedores.index', form=form, detalle_proveedor=detalle_proveedor))


@bp.route('/eliminar/<int:id>')
def eliminar_detalle_proveedor(id):
    articulo = Articulo.query.filter_by(detalle_proveedor_predeterminado_id=id).first()
    detalle_proveedor = DetalleProveedor.query.get_or_404(id)

    
    if articulo:  #Validacion que no haya ningun articulo apuntando es este detalle proveedor
        flash(f'No se puede eliminar el detalle proveedor porque está establecido como predeterminado para el articulo "{articulo.nombre_articulo}".', 'danger')
    else:
        db.session.delete(detalle_proveedor)
        db.session.commit()
        flash('Detalle proveedor eliminado con éxito', 'success')
    return redirect(url_for('proveedores.index'))
    

    