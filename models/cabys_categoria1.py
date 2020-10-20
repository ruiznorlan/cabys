# -*- coding: utf-8 -*-
#     info@fakturacion.com
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class CabysCategoria1(models.Model):
    _name = 'cabys.categoria1'
    _description = 'Categoría 1 de Cabys'

    name   = fields.Char('Categoria 1')
    codigo = fields.Char('Código')

    cabys_categoria2_ids = fields.One2many('cabys.categoria2', 'cabys_categoria1_id', string='Categorías 2')


