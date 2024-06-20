
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ArticuloFormCrearEditar(FlaskForm):
    codigo_articulo = IntegerField('Código artículo', validators=[DataRequired(), NumberRange(min=1)])
    nombre_articulo = StringField('Nombre artículo', validators=[DataRequired()])
    coeficiente_seguridad = FloatField('Coeficiente de seguridad', validators=[DataRequired(), NumberRange(min=0)])
    costo_almacenamiento = FloatField('Costo almacenamiento', validators=[DataRequired(), NumberRange(min=0)])
    costo_de_pedido = FloatField('Costo pedido', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[NumberRange(min=0)])
    tiempo_de_pedido = IntegerField('Tiempo de Pedido', validators=[NumberRange(min=0)])
    modelo_inventario_id = SelectField('Modelo de Inventario', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Crear')

    