from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app import db
from app.models import *
from app.forms import DemandaForm
from datetime import datetime

bp = Blueprint('demanda', __name__, url_prefix='/demanda')

@bp.route('/', methods=['GET'])
def get_demanda ():
    form = DemandaForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]
    
    demanda = Demanda.query.all()
    return render_template('demanda/demandaPage.html', demanda=demanda, form=form)  


@bp.route('/', methods=['POST'])
def crear_demanda():
    form = DemandaForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]

    if form.validate_on_submit():
        articulo_id = form.articulo_id.data
        fecha = form.fecha_d.data
        fecha_actual = datetime.now()

        if fecha.month < fecha_actual.month or fecha.year < fecha_actual.year:
            if Demanda.existe_demanda(articulo_id, fecha):
                flash('Ya existe una demanda para este artículo en el mismo mes y año.', 'error')
            else:
                cantidad_demanda = Venta.calcular_demanda_mes(articulo_id, fecha)
                nueva_demanda = Demanda(
                    cantidad=cantidad_demanda,
                    articulo_id=articulo_id,
                    fecha_d=fecha
                )
                try:
                    db.session.add(nueva_demanda)
                    db.session.commit()
                    flash('Demanda guardada con éxito!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error al crear la demanda: {str(e)}', 'danger')
                return redirect(url_for('demanda.get_demanda'))
        else:
            flash('El mes no puede ser el actual', 'danger')
    if form.errors:
        flash(f'Errores en el formulario: {form.errors}', 'danger')
        print("Errores del formulario:", form.errors)
    return redirect(url_for('demanda.get_demanda'))



@bp.route('/eliminar/<int:id>')
def eliminar_demanda(id):
    demanda = Demanda.query.get_or_404(id)
    db.session.delete(demanda)
    db.session.commit()
    flash('Demanda eliminada con éxito', 'success')
    return redirect(url_for('demanda.get_demanda'))

@bp.route('/consultar', methods=['GET'])
def consultar_demanda():
    form = DemandaForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]

    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    articulo_id = request.args.get('articulo_id')

    demanda_consulta = []

    if fecha_inicio and fecha_fin and articulo_id:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m')
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m')
            articulo_id = int(articulo_id)

            demanda_consulta = Demanda.query.filter(
                Demanda.fecha_d >= fecha_inicio,
                Demanda.fecha_d <= fecha_fin,
                Demanda.articulo_id == articulo_id
            ).all()
        except ValueError as e:
            flash(f'Error en los datos proporcionados: {str(e)}', 'danger')

    return render_template('demanda/demandaPage.html', form=form, demanda_consulta=demanda_consulta)