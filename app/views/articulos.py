from flask import Blueprint, render_template, request, redirect, url_for
from ..models import db, Articulo

bp = Blueprint('articulos', __name__, url_prefix='/articulos')

@bp.route('/')
def index():
    articulos = Articulo.query.all()
    return render_template('articulos/index.html', articulos=articulos)

@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # Código para crear un artículo
        pass
    return render_template('articulos/create.html')

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    articulos = Articulo.query.get_or_404(id)
    if request.method == 'POST':
        # Código para editar un artículo
        pass
    return render_template('articulos/edit.html', articulos=articulos)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    articulos = Articulo.query.get_or_404(id)
    # Código para eliminar un artículo
    pass
