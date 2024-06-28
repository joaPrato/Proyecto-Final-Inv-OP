from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import *
from app.forms import  ParametrosGeneralesPrediccionForm

bp = Blueprint('demanda_predecida', __name__, url_prefix='/demanda_predecida')


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = ParametrosGeneralesPrediccionForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]
    
    return render_template('demanda_predecida/index.html', form=form )

@bp.route('/parametros', methods=['GET', 'POST'])
def parametros():
    form = ParametrosGeneralesPrediccionForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]
    if form.validate_on_submit():
        # Guarda los parámetros generales
        flash('Parámetros guardados exitosamente', 'success')
        return redirect(url_for('demanda_predecida.parametros'))
    return render_template('demanda_predecida/index.html', form=form )


@bp.route('/promedio_movil', methods=['GET', 'POST'])
def promedio_movil():
    form = ParametrosGeneralesPrediccionForm()

    if form.validate_on_submit():
        articulo_id = form.articulo_id.data
        periodos = form.cantidad_periodos.data
        try:
            prediccion = DemandaPredecida.predecir_promedio_movil(articulo_id, periodos)
            flash(f'Demanda predecida usando Promedio Móvil: {prediccion}', 'success')
        except ValueError as e:
            flash(str(e), 'danger')
        return redirect(url_for('demanda_predecida.resultados'))
    return render_template('demanda_predecida/index.html', form=form)

@bp.route('/promedio_movil_ponderado', methods=['GET', 'POST'])
def promedio_movil_ponderado():
    form = ParametrosGeneralesPrediccionForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]

    if form.validate_on_submit():
        articulo_id = form.articulo_id.data
        periodos = form.cantidad_periodos.data
        factores_ponderacion = [form.factor_ponderacion1.data, form.factor_ponderacion2.data, form.factor_ponderacion3.data]  # Ajustar según el número de factores
        try:
            prediccion = DemandaPredecida.predecir_promedio_movil_ponderado(articulo_id, periodos, factores_ponderacion)
            flash(f'Demanda predecida usando Promedio Móvil Ponderado: {prediccion}', 'success')
        except ValueError as e:
            flash(str(e), 'danger')
        return redirect(url_for('demanda_predecida.resultados'))
    return render_template('demanda_predecida/index.html', form=form)

@bp.route('/promedio_movil_ponderado', methods=['GET', 'POST'])
def promedio_movil_suavizado():
    form = ParametrosGeneralesPrediccionForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]

    if form.validate_on_submit():
        articulo_id = form.articulo_id.data
        alfa = form.alfa.data
        prediccion_raiz = form.prediccion_raiz.data
        try:
            prediccion = DemandaPredecida.predecir_promedio_movil_suavizado(articulo_id, alfa, prediccion_raiz)
            flash(f'Demanda predecida usando Promedio Móvil Suavizado: {prediccion}', 'success')
        except ValueError as e:
            flash(str(e), 'danger')
        return redirect(url_for('demanda_predecida.resultados'))
    return render_template('demanda_predecida/index.html', form=form)

@bp.route('/regresionLineal', methods=['GET', 'POST'])
def regresion_lineal():
    form = ParametrosGeneralesPrediccionForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]

    if form.validate_on_submit():
        try:
            articulo_id = form.articulo_id.data
            prediccion = DemandaPredecida.predecir_regresion_lineal(articulo_id)
            flash(f'Predicción: {prediccion}', 'success')
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('demanda_predecida/index.html', form=form)

@bp.route('/ajusteEstacional', methods=['GET', 'POST'])
def ajuste_estacional():
    form = ParametrosGeneralesPrediccionForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]

    if form.validate_on_submit():
        try:
            articulo_id = form.articulo_id.data
            indices_estacionales = [1.0] * 12  # Aquí puedes definir los índices estacionales adecuados
            predicciones = DemandaPredecida.predecir_ajuste_estacional(articulo_id, indices_estacionales)
            flash(f'Predicciones: {predicciones}', 'success')
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('demanda_predecida/index.html', form=form)


@bp.route('/resultados', methods=['GET'])
def resultados():
    demandas_predecidas = DemandaPredecida.query.all()
    return render_template('demanda_predecida/index.html', demandas_predecidas=demandas_predecidas)
