from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app import db
from app.models import *

bp = Blueprint('ventas', __name__, url_prefix='/ventas')