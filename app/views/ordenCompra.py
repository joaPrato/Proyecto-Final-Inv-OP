from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app import db
from app.models import *

bp = Blueprint('ordenCompra', __name__, url_prefix='/ordenCompra')