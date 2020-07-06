# -*- coding: utf-8 -*-

from odoo.addons.web.controllers.main import Home
import socket
import odoo
import odoo.modules.registry
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.tools.translate import _


class CheckLogin(Home):
    @http.route('/web/error', type='http', auth="none")
    def error_login(self, mod=None, **kwargs):
        return request.render('check_login.notify_error_login')

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        odoo.addons.web.controllers.main.ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            client_ip = socket.gethostbyname(socket.gethostname())
            ip_address_client = request.env['black.list'].search([('ip_address', '=', client_ip)])
            if len(ip_address_client) == 1:
                request.params['login_success'] = False
                return request.redirect('/web/error')
            try:
                uid = request.session.authenticate(request.session.db, request.params['login'],
                                                   request.params['password'])
                request.params['login_success'] = True
                return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    old_check_login_detail = request.env['check.login.fail'].sudo().search(
                        [('ip_address', '=', client_ip), ('name', '=', values['login'])], limit=1)
                    if old_check_login_detail:
                        if old_check_login_detail.state == 'ban':
                            request.env['black.list'].sudo().create({
                                'ip_address': client_ip
                            })
                            request.params['login_success'] = False
                            return request.redirect('/web/error')
                        old_check_login_detail.sudo().update({
                            'count': old_check_login_detail.count + 1
                        })
                    else:
                        request.env['check.login.fail'].sudo().create({
                            'name': values['login'],
                            'ip_address': client_ip,
                            'count': 1
                        })
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employee can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
