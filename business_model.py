from odoo import api, fields, models
from odoo.exceptions import UserError

class MobileStore(models.Model):
    _name = "mobile.business.store"
    _rec_name = "mobile_name"

    mobile_name = fields.Char(string="Mobile Name")
    mobile_image = fields.Binary(string="Mobile Image")
    mob_unit_price = fields.Float(string="Mobile Price")
    mob_qty = fields.Integer(string="Mobile quantity")

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s' % rec.mobile_name))
        return res


class MobilePurchase(models.Model):
    _name = "mobile.purchase"

    mob_pur_sq = fields.Char(string="Purchase Number", readonly=True, required=True, copy=False, default='POM/')
    customer_id = fields.Many2one("res.partner", string="Customer Name")
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string="state")
    country_id = fields.Many2one('res.country', string='Country')
    zip = fields.Char('zip')
    purchase_line = fields.One2many("mobile.business.line", "mobile_id", string="Purchase Line")
    state = fields.Selection(
        [('draft', 'Draft'),
         ('processing', 'Processing'),
         ('completed', 'Completed'),
         ('cancel', 'Cancelled')],
        string='Status', readonly=True, default="draft")
    subtotal_amount = fields.Float(string="Subtotal", compute="compute_line_price")
    total_amount = fields.Float(string="Total amount", compute="compute_line_price")
    currency_id = fields.Many2one("res.currency")

    @api.depends("purchase_line.mobile_price")
    def compute_line_price(self):
        sub_total = 0

        for i in self.purchase_line:
            sub_total += i.mobile_price
        grand_total = sub_total + sub_total * (sum([x.gst_tax for x in self.purchase_line]) / 100)
        self.subtotal_amount = sub_total
        self.total_amount = grand_total

    def action_processing(self):
        self.state = 'processing'

    def action_complete(self):
        self.state = 'completed'

    def action_cancel(self):
        if self.state == 'completed':
            raise UserError(
                ('The %s record could not be deleted.Because the process was completed.' % self.mob_pur_sq))
        else:
            self.state = 'cancel'

    def action_reset(self):
        self.state = 'draft'

    @api.onchange("customer_id")
    def onchange_customer_add(self):
        customer_obj = self.env['res.partner'].search([('id', '=', self.customer_id.id)])
        self.street = customer_obj.street
        self.street2 = customer_obj.street2
        self.city = customer_obj.city
        self.state_id = customer_obj.state_id
        self.zip = customer_obj.zip
        self.country_id = customer_obj.country_id

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s' % rec.mob_pur_sq))
        return res

    @api.model
    def create(self, values):
        if values.get('mob_pur_sq', 'New') == 'New':
            values['mob_pur_sq'] = self.env['ir.sequence'].next_by_code(
                'mobile.purchase') or 'New'
        return super(MobilePurchase, self).create(values)


class PartnerCustomize(models.Model):
    _inherit = "res.partner"

    github = fields.Char(string="GitHub")





class MobileBusinessLine(models.Model):
    _name = "mobile.business.line"
    mobile_name_line = fields.Many2one("mobile.business.store", string="Mobile Name")
    mobile_id = fields.Many2one("mobile.purchase",string="Mobile Purchase")
    mobile_price = fields.Float(string="Mobile Price")
    mobile_qty = fields.Integer(sring="Mobile quantity")
    gst_tax = fields.Float(string="GST Tax")


    @api.multi
    @api.onchange('mobile_name_line')
    def onchange_mobile(self):
        for x in self:
            x.mobile_price = x.mobile_name_line.mob_unit_price
            x.mobile_qty = x.mobile_name_line.mob_qty


