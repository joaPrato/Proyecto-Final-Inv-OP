
from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, IntegerField, FloatField, SelectField, SubmitField, DateField # type: ignore
from wtforms.validators import DataRequired, NumberRange # type: ignore
import datetime


class ArticuloFormCrear(FlaskForm):
    codigo_articulo = IntegerField('Código artículo', validators=[DataRequired(), NumberRange(min=1)])
    nombre_articulo = StringField('Nombre artículo', validators=[DataRequired()])
    coeficiente_seguridad = FloatField('Coeficiente de seguridad', validators=[DataRequired(), NumberRange(min=0)])
    costo_almacenamiento = FloatField('Costo almacenamiento', validators=[DataRequired(), NumberRange(min=0)])
    costo_de_pedido = FloatField('Costo pedido', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[NumberRange(min=0)])
    tiempo_de_pedido = IntegerField('Tiempo de Pedido', validators=[NumberRange(min=0)])
    modelo_inventario_id = SelectField('Modelo de Inventario', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Crear')   

class ArticuloFormEditar(FlaskForm):
    codigo_articulo = IntegerField('Código artículo', validators=[DataRequired(), NumberRange(min=1)])
    nombre_articulo = StringField('Nombre artículo', validators=[DataRequired()])
    coeficiente_seguridad = FloatField('Coeficiente de seguridad', validators=[DataRequired(), NumberRange(min=0)])
    costo_almacenamiento = FloatField('Costo almacenamiento', validators=[DataRequired(), NumberRange(min=0)])
    costo_de_pedido = FloatField('Costo pedido', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[NumberRange(min=0)])
    tiempo_de_pedido = IntegerField('Tiempo de Pedido', validators=[NumberRange(min=0)])
    modelo_inventario_id = SelectField('Modelo de Inventario', coerce=int, validators=[DataRequired()])
    detalle_proveedor_predeterminado_id=SelectField('Proveedor predeterminado', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Crear')  

class ProveedorFrom (FlaskForm):
    nombre=StringField('Nombre proveedor', validators=[DataRequired()])
    submit=SubmitField('Crear')

class DetalleProveedorForm(FlaskForm):
     proveedor_id = SelectField('Proveedor', coerce=int, validators=[DataRequired()])
     costo_pedido_proveedor=FloatField('Costo de pedido',validators=[DataRequired(), NumberRange(min=0)])
     precio_articulo=FloatField('Precio Articulo', validators=[DataRequired(), NumberRange(min=0)])
     tiempo_demora=IntegerField('Tiempo de demora',validators=[DataRequired(), NumberRange(min=0)])
     articulo_id=SelectField('Articulo', coerce=int, validators=[DataRequired()])
     submit=SubmitField('Crear')

class DetalleProveedorFormEditar(FlaskForm):
     costo_pedido_proveedor=FloatField('Costo de pedido',validators=[DataRequired(), NumberRange(min=0)])
     precio_articulo=FloatField('Precio Articulo', validators=[DataRequired(), NumberRange(min=0)])
     tiempo_demora=IntegerField('Tiempo de demora',validators=[DataRequired(), NumberRange(min=0)])
     submit=SubmitField('Guardar Cambios')

class OrdenCompraForm(FlaskForm):
    lote = IntegerField('Lote', validators=[DataRequired(),NumberRange(min=0)])
    articulo_id = SelectField('Artículo', coerce=int, validators=[DataRequired()])
    estado_id = SelectField('Estado orden', coerce=int, validators=[DataRequired()])
    detalle_proveedor_id= SelectField('Proveedor', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')
    
class VentaFormCrearEditar(FlaskForm):
    nro_venta = IntegerField('Numero de venta', validators=[DataRequired(), NumberRange(min=1)])
    cantidad = IntegerField('Cantidad de articulos', validators=[DataRequired(), NumberRange(min=1)])
    articulo_id = SelectField('Artículo', coerce=int, validators=[DataRequired()] )
    fecha = DateField('Fecha', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.date.today) #predeterminada la fecha actual
    submit = SubmitField('Guardar Venta')

