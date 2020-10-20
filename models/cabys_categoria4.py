# -*- coding: utf-8 -*-
#     info@fakturacion.com
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class CabysCategoria4(models.Model):
    _name = 'cabys.categoria4'
    _description = 'Categoría 4 de Cabys'

    name   = fields.Char('Categoria 4')
    codigo = fields.Char('Código')

    cabys_categoria3_id = fields.Many2one(comodel_name='cabys.categoria3')
    cabys_categoria5_ids = fields.One2many('cabys.categoria5', 'cabys_categoria4_id', string='Categorías 5')


