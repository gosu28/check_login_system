# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BlackList(models.Model):
    _name = 'black.list'
    _description = 'Black List'
    _rec_name = 'ip_address'

    ip_address = fields.Char(string='IP Address')

    def unlink(self):
        for rec in self:
            rec.env['check.login.fail'].sudo().search(
                [('ip_address', '=', rec.ip_address)]
            ).unlink()
        return super(BlackList, self).unlink()
