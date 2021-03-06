# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Dion Martin @Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Deby Wahyu Kurdian <deby.wahyu.kurdian@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = ['product.template']

    last_purchase_price = fields.Float(string="Last purchase price")

class PriceListItem(models.Model):
    _inherit = 'product.pricelist.item'

    base = fields.Selection(selection_add=[('last_purchase_price','Last purchase price')])

class AccountInvoice(models.Model):
    _inherit = ['account.invoice']

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice,self).action_invoice_open()
        for inv in self.filtered(lambda i: i.type == 'in_invoice'):
            for line in inv.invoice_line_ids:
                if line.uom_id:
                    unit_price = line.price_unit if line.uom_id == line.product_id.uom_id else line.uom_id._compute_price(line.price_unit, line.product_id.uom_id)
                else:
                    unit_price = line.price_unit
                company_currency = inv.company_id.currency_id
                if inv.currency_id != company_currency:
                    unit_price = inv.currency_id.with_context(
                    date=inv._get_currency_rate_date()).compute(
                    abs(unit_price), inv.company_id.currency_id)
                if unit_price > 0.0 and line.product_id:
                    line.product_id.product_tmpl_id.last_purchase_price = unit_price
                # if hasattr(line.product_id.product_tmpl_id, 'pack'):
                #     line.product_id.product_tmpl_id.set_parent_pack_price()
        return res