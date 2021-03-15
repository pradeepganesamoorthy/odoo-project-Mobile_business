# -*- coding: utf-8 -*-

from odoo import api, fields, models
import datetime


class PurchaseMobileWizard(models.TransientModel):
    _name = 'purchase.wizard'

    mobile_name = fields.Many2one("mobile.business.store", string="Mobile Name")
    mob_price = fields.Float(string="Mobile Price")
    from_date = fields.Datetime(string="Starting Date")
    to_date = fields.Datetime(string="Ending Date")
    cus_name = fields.Char(string="Customer Name")

    @api.onchange("mobile_name")
    def onchange_mob_price(self):
        for i in self:
            i.mob_price = i.mobile_name.mob_unit_price

    @api.multi
    def Quotation_purchase(self):
        journals = self.env['sale.order'].search([('confirmation_date', '>', self.from_date), ('confirmation_date', '<', self.to_date)])
        for record in journals:
            print(record)

        tree_view = self.env.ref('sale.view_quotation_tree')
        return {
            'name': 'Sale Order',
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'sale.order',
            'domain': ['&', ('date_order', '>', self.from_date), ('date_order', '<', self.to_date)],
            'view_id': False,
            'views': [
                (tree_view.id, 'tree'),
                (False, 'calendar'),
                (False, 'graph')
            ],
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def cus_purchase(self):
        tree_view = self.env.ref('base.view_partner_tree')
        return{
            'name': 'Customer',
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'res.partner',
            'view_id': False,
            'domain': [('name', 'ilike', self.cus_name)],
            'views': [(tree_view.id, 'tree')],
            'type': 'ir.actions.act_window',
        }