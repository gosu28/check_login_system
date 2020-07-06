# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CheckLoginFail(models.Model):
    _name = 'check.login.fail'
    _description = 'Check Login Fail'

    name = fields.Char(string='User Name')
    ip_address = fields.Char(string='IP Address')
    state = fields.Selection(string='Status',
                             selection=[('fail', 'Fail'), ('ban', 'Ban')],
                             compute="_compute_state", store=True)
    count = fields.Integer(string="Count")

    @api.depends('count')
    def _compute_state(self):
        for rec in self:
            rec.state = 'fail'
            if rec.count >= 10:
                rec.state = 'ban'
