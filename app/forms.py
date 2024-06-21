
from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, IntegerField, FloatField, SelectField, SubmitField # type: ignore
from wtforms.validators import DataRequired, NumberRange # type: ignore

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

class OrdenCompraForm(FlaskForm):
    lote = IntegerField('Lote', validators=[DataRequired()])
    modeloOrdenCompra_id = SelectField('Modelo Orden de Compra', coerce=int, validators=[DataRequired()])
    articulo_id = SelectField('Artículo', coerce=int, validators=[DataRequired()])
    estado_orden_id = SelectField('Estado Orden', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')
    
