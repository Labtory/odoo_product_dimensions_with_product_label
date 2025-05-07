# -*- coding: utf-8 -*-
from collections import defaultdict
from odoo import models, api

class ProductLabelReportCustom(models.AbstractModel):
    _inherit = 'report.product.report_producttemplatelabel2x7'

    def _get_report_values(self, docids, data):
        return self._prepare_custom_data(self.env, docids, data)

    def _prepare_custom_data(self, env, docids, data):
        layout_wizard = env['product.label.layout'].browse(data.get('layout_wizard'))
        
        if data.get('active_model') == 'product.template':
            Product = env['product.template'].with_context(display_default_code=False)
        elif data.get('active_model') == 'product.product':
            Product = env['product.product'].with_context(display_default_code=False)
        else:
            return {}

        if not layout_wizard:
            return {}

        qty_by_product_in = data.get('quantity_by_product')
        products = Product.search([('id', 'in', [int(p) for p in qty_by_product_in.keys()])], order='name desc')

        quantity_by_product = defaultdict(list)
        production_data = {}

        for product in products:
            q = qty_by_product_in[str(product.id)]
            quantity_by_product[product].append((product.barcode, q))

            # Obtener la orden de fabricación más reciente asociada al producto
            production = env['mrp.production'].search([
                ('product_id', '=', product.id)
            ], order='date_start desc', limit=1)

            production_data[product.id] = production.lot_producing_id.name if production.lot_producing_id else ""

        return {
            'quantity': quantity_by_product,
            'production_data': production_data,
            'page_numbers': (sum(qty_by_product_in.values()) - 1) // (layout_wizard.rows * layout_wizard.columns) + 1,
            'price_included': data.get('price_included'),
            'extra_html': layout_wizard.extra_html,
            'pricelist': layout_wizard.pricelist_id,
        }

class ProductLabelReportDymo(models.AbstractModel):
    _inherit = 'report.product.report_product_label_dymo'

    def _get_report_values(self, docids, data):
        return self._prepare_custom_data(self.env, docids, data)
