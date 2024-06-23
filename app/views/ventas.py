from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify 
from app import db
from app.models import *
from app.forms import VentaFormCrearEditar


bp = Blueprint('ventas', __name__, url_prefix='/ventas')
@bp.route('/', methods=['GET'])
def get_ventas ():
    form = VentaFormCrearEditar()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]
    
    ventas = Venta.query.all()
    return render_template('ventas/ventaPage.html', ventas=ventas, form=form) 

@bp.route('/', methods=['POST'])
def crear_venta():
    form = VentaFormCrearEditar()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]
    
    if form.validate_on_submit():
        #validar si hay suficiente stock disponible 
        cantidad = form.cantidad.data
        articulo_id = form.articulo_id.data

        articulo = Articulo.query.get(form.articulo_id.data) #busca de articulo que tenga id = articulo_id
        
        if articulo.stock >= cantidad:
            articulo.stock -= cantidad # Restar la cantidad vendida del stock del artículo
            
            nueva_venta= Venta(
            nro_venta= form.nro_venta.data, 
            fecha=form.fecha.data, 
            cantidad= form.cantidad.data,
            articulo_id= form.articulo_id.data
            )
        
            try:
                db.session.add(nueva_venta)
                db.session.commit()
                flash('Venta creada con éxito', 'success')
                return redirect(url_for('ventas.get_ventas'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al crear la venta: {str(e)}', 'danger')
        else:
            flash('No hay suficiente stock para realizar la venta', 'danger')
  
    return redirect(url_for('ventas.get_ventas'))

    
@bp.route('/eliminar/<int:nro_venta>')
def eliminar_venta(nro_venta):
    venta = Venta.query.get_or_404(nro_venta)
    db.session.delete(venta)
    db.session.commit()
    flash('Venta eliminada con éxito', 'success')
    return redirect(url_for('ventas.get_ventas'))
   
    
    
    
    
    
    
    
