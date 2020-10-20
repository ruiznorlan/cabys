# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tests.common import Form
import logging
import base64
import urllib.request



_logger = logging.getLogger(__name__)

try:
    from xlrd import open_workbook
except ImportError:
    _logger.debug('Can not import xlrd`.')

# Column mapping for every Cabys category
categories_map = [  {'category': '1', 'code': 0,  'description': 1                   },
                    {'category': '2', 'code': 2,  'description': 3,  'subcategory': 0},
                    {'category': '3', 'code': 4,  'description': 5,  'subcategory': 2},
                    {'category': '4', 'code': 6,  'description': 7,  'subcategory': 4},
                    {'category': '5', 'code': 8,  'description': 9,  'subcategory': 6},
                    {'category': '6', 'code': 10, 'description': 11, 'subcategory': 8},
                    {'category': '7', 'code': 12, 'description': 13, 'subcategory': 10},
                    {'category': '8', 'code': 14, 'description': 15, 'subcategory': 12}]
# Column mapping of the Cabys product data
products_map = {'category': 14, 'code': 16, 'description': 17, 'tax': 18}
# Headers and columns that should be in the Excel catalog file, 
# we'll use this to check if the Excel file is a Cabys catalog
headers_map = [ {'column':0,  'header': 'Categoría 1'},  {'column':1,  'header': 'Descripción (categoría 1)'},
                {'column':2,  'header': 'Categoría 2'},  {'column':3,  'header': 'Descripción (categoría 2)'},
                {'column':4,  'header': 'Categoría 3'},  {'column':5,  'header': 'Descripción (categoría 3)'},
                {'column':6,  'header': 'Categoría 4'},  {'column':7,  'header': 'Descripción (categoría 4)'},
                {'column':8,  'header': 'Categoría 5'},  {'column':9,  'header': 'Descripción (categoría 5)'},
                {'column':10, 'header': 'Categoría 6'},  {'column':11, 'header': 'Descripción (categoría 6)'},
                {'column':12, 'header': 'Categoría 7'},  {'column':13, 'header': 'Descripción (categoría 7)'},
                {'column':14, 'header': 'Categoría 8'},  {'column':15, 'header': 'Descripción (categoría 8)'},
                {'column':16, 'header': 'Código del bien o servicio'},
                {'column':17, 'header': 'Descripción del bien o servicio'},
                {'column':18, 'header': 'Impuesto'}]


class CabysCatalogImportWizard(models.TransientModel):
    _name = 'cabys.catalog.import.wizard'
    _description = 'Import the Cabys Catalog from an Excel file.'

    cabys_excel_file = fields.Binary(string='Archivo de Excel', copy=False, attachment=True)
    notes = fields.Text("Descripción", readonly=True)
    button_enable = fields.Boolean()
    file_url = fields.Char(default='https://activos.bccr.fi.cr/sitios/bccr/indicadoreseconomicos/cabys/Catalogo-de-bienes-servicios.xlsx')


    def download_catalog(self):
        ''' Download the Cabys catalog Excel file from BCCR.
        '''
        _logger.info('downloading catalog %s' % self)
        response = urllib.request.urlopen(self.file_url)
        _logger.info(response)
        data = response.read()
        self.cabys_excel_file = base64.b64encode(data)


        return {
            'name': _("Catálogo Cabys descargado exitosamente"),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cabys.catalog.import.wizard',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id,
        }


    @api.multi
    def _generate_catalog_from_excel_file(self):

        if self.cabys_excel_file:
            
            excel_file = base64.b64decode(self.cabys_excel_file)
            _logger.info('Loading Cabys catalog from Excel file')

            workbook = open_workbook(file_contents=excel_file)
            _logger.info('workbook %s' % workbook)
            sheet_names = workbook.sheet_names()
            _logger.info('Sheet Names' % sheet_names)

            xl_sheet = workbook.sheet_by_index(0)
            _logger.info(xl_sheet)
            _logger.info ('Sheet name: %s' % xl_sheet.name)

            rows = xl_sheet.get_rows()
            # skip first two header rows
            rows.__next__()
            rows.__next__()

            # here we will keep categories data and product data
            categories = {}
            products = {}

            for category_map in categories_map:
                categories[category_map['category']] = {}

            # iterate over every line in the excel file
            for row in rows:
                # get every subcategory
                for category_map in categories_map:
                    category = category_map['category']
                    code = row[category_map['code']].value
                    description = row[category_map['description']].value

                    if code not in categories[category]:
                        vals = {'code': code, 'description': description}
                        if 'subcategory' in category_map:
                            vals['subcategory'] = row[category_map['subcategory']].value

                        categories[category][code] = vals

                # process product
                category = row[products_map['category']].value
                description = row[products_map['description']].value
                code = row[products_map['code']].value
                tax = 0.0 if row[products_map['tax']].value == 'Exento' else float(row[products_map['tax']].value[:-1]) 
                products[code] = {'name': description, 'codigo': code, 'impuesto': tax, 'cabys_categoria8_id': category}

            # sort categories in order to process them orderly
            order_categories = categories.keys()
            order_categories = [int(cat) for cat in order_categories]
            order_categories.sort()
            order_categories = [str(cat) for cat in order_categories]

            # create categories if they don't yet exist
            for category in order_categories:
                _logger.info('Processing category %s with %s records' % (category, len(categories[category])))
                records_data = categories[category]
                object_name = 'cabys.categoria%s' % category
                for category_data in records_data:
                    record_data = records_data[category_data]
                    record_id = self.env[object_name].search([('codigo', '=', record_data['code'])])
                    if not record_id:
                        vals = { 'codigo': record_data['code'], 'name': record_data['description'] }
                        if 'subcategory' in record_data:
                            subcategory_field = 'cabys_categoria%s_id' % (int(category)-1)
                            vals[subcategory_field] = categories[str((int(category)-1))][record_data['subcategory']]['id']
                        
                        record_id = self.env[object_name].create(vals)
                        # self.env.cr.commit()

                    categories[category][category_data]['id'] = record_id.id


            # up to this point all categories should exist
            # we now add the products
            _logger.info('Processing %s products in catalog' % len(products))
            for code in products:
                record_id = self.env['cabys.producto'].search([('codigo', '=', code)])
                if not record_id:
                    vals = products[code]
                    vals['cabys_categoria8_id'] = categories['8'][vals['cabys_categoria8_id']]['id']
                    record_id = self.env['cabys.producto'].create(vals)
                    # self.env.cr.commit()
        else:
            _logger.info('no file')

        return True

    @api.multi
    def upload_catalog(self):
        ''' Upload the Cabys catalog from an Excel file.
        '''
        _logger.info('upload_catalog %s' % self)
        if not self.cabys_excel_file:
            return
        
        self._generate_catalog_from_excel_file()

        # return True

        return {
            'name': _("Catálogo Cabys actualizado exitosamente"),
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'cabys.producto',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'view_id': False,
            'domain': '[]',
        }


        # action_vals = {
        #     'name': _('Invoices'),
        #     'domain': [('id', 'in', invoices.ids)],
        #     'view_type': 'form',
        #     'res_model': 'account.invoice',
        #     'view_id': False,
        #     'type': 'ir.actions.act_window',
        # }
        # if len(invoices) == 1:
        #     action_vals.update({'res_id': invoices[0].id, 'view_mode': 'form'})
        # else:
        #     action_vals['view_mode'] = 'tree,form'
        # return action_vals


    @api.onchange('cabys_excel_file')
    def onchange_cabys_excel_file(self):
        """Preprocess Excel File."""

        if self.cabys_excel_file:
            # get file contents
            excel_file = base64.b64decode(self.cabys_excel_file)
            # open it as an Excel file
            workbook = open_workbook(file_contents=excel_file)
            # Get first sheet, that's where all the data should be
            xl_sheet = workbook.sheet_by_index(0)
            # second row has the headers of the file
            # we will check the headers names to infer if this is a Cabys catalog file
            for header in headers_map:
                cell = xl_sheet.cell(1, header['column'])
                if cell.value != header['header']:
                    self.notes = 'El archivo seleccionado no parece ser un catálogo Cabys'
                    self.button_enable = False
                    return
            # if we haven't returned, the file's headers are correct
            self.notes = 'El catálogo Cabys seleccionado puede ser importado'
            self.button_enable = True
        
        else:
            self.notes = 'Seleccione el archivo de Excel con el catálogo Cabys'
            self.button_enable = False




        