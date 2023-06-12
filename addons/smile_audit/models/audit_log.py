# -*- coding: utf-8 -*-
# (C) 2010 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil import tz

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
import logging
_logger = logging.getLogger(__name__)

class AuditLog(models.Model):
    _name = 'audit.log'
    _description = 'Audit Log'
    _order = 'create_date desc, id desc'

    name = fields.Char('Resource Name', size=256, compute='_get_name')
    create_date = fields.Datetime('Date', readonly=True)
    user_id = fields.Many2one(
        'res.users', 'User', required=True, readonly=True)
    model_id = fields.Many2one(
        'ir.model', 'Model', required=True, readonly=True)
    model = fields.Char(
        related='model_id.model', store=True, readonly=True, index=True)
    res_id = fields.Integer('Resource Id', readonly=True)
    method = fields.Char('Method', size=64, readonly=True)
    data = fields.Text('Data', readonly=True)
    data_html = fields.Html(
        'HTML Data', readonly=True, compute='_render_html')

    @api.one
    def _get_name(self):
        if self.model_id and self.res_id:
            record = self.env[self.model_id.model].browse(self.res_id).exists()
            if record:
                self.name = record.display_name
            else:
                data = safe_eval(self.data or '{}')
                rec_name = self.env[self.model_id.model]._rec_name
                if rec_name in data['new']:
                    self.name = data['new'][rec_name]
                elif rec_name in data['old']:
                    self.name = data['old'][rec_name]
                else:
                    self.name = 'id=%s' % self.res_id
        else:
            self.name = ''

    @api.multi
    def _format_value(self, field, value):
        self.ensure_one()
        if not value and field.type not in ('boolean', 'integer', 'float'):
            return ''
        if field.type == 'selection' and value != 'none':
            selection = field.selection
            if callable(selection):
                selection = selection(self.env[self.model_id.model])
            return dict(selection).get(value, value)
        if field.type == 'many2one' and value:
            return self.env[field.comodel_name].browse(
                value).exists().display_name or value
        if field.type == 'reference' and value:
            res_model, res_id = value.split(',')
            return self.env[res_model].browse(
                int(res_id)).exists().display_name or value
        if field.type in ('one2many', 'many2many') and value:
            for rec_id in value:
                if self.env[field.comodel_name].browse(rec_id).exists():
                    values = ''.join(['<li>' + self.env[field.comodel_name].browse(
                                          rec_id).display_name +
                                      '</li>' or '<li>' + str(rec_id) +
                                      '</li>'])
                else:
                    values = ''.join(['<li>' + str(self.env[field.comodel_name].browse(
                                          rec_id).id) +
                                      '</li>' or '<li>' + str(rec_id) +
                                      '</li>'])
            return '<ul>' + values + '</ul>'
        if field.type == 'binary' and value:
            return '&lt;binary data&gt;'
        if field.type == 'datetime':
            from_tz = tz.tzutc()
            to_tz = tz.gettz(self.env.user.tz)
            datetime_wo_tz = fields.Datetime.from_string(value)
            datetime_with_tz = datetime_wo_tz.replace(tzinfo=from_tz)
            return fields.Datetime.to_string(
                datetime_with_tz.astimezone(to_tz))
        return value

    @api.multi
    def _get_content(self):
        self.ensure_one()
        content = []
        data = safe_eval(self.data or '{}')
        RecordModel = self.env[self.model_id.model]
        for fname in set(data['new'].keys()) | set(data['old'].keys()):
            field = RecordModel._fields.get(fname)
            if field:
                old_value = self._format_value(
                    field, data['old'].get(fname, ''))
                new_value = self._format_value(
                    field, data['new'].get(fname, ''))
                if old_value != new_value:
                    label = field.get_description(self.env)['string']
                    content.append((label, old_value, new_value))
        return content

    @api.one
    def _render_html(self):
        thead = ''
        for head in (_('Field'), _('Old value'), _('New value')):
            thead += '<th>%s</th>' % head
        thead = '<thead><tr>%s</tr></thead>' % thead
        tbody = ''
        for line in self._get_content():
            row = ''
            for item in line:
                row += '<td>%s</td>' % item
            tbody += '<tr>%s</tr>' % row
        tbody = '<tbody>%s</tbody>' % tbody
        self.data_html = '<table class="o_list_view table table-condensed ' \
                         'table-striped">%s%s</table>' % (thead, tbody)

    @api.multi
    def unlink(self):
        raise UserError(_('You cannot remove audit logs!'))

    @api.multi
    def display_history_revision(self):
        _logger.info("222222222222222222222222222222222222222222222222222222222")
        self.ensure_one()
        self._cr.execute('SELECT create_date FROM %s WHERE id = %%s'
                         % self._table, (self.id,))
        create_date = self._cr.dictfetchall()[0]['create_date']
        _logger.info("333333333333333333333333333333333333333333",create_date)
        x= {
            'name': self.model_id.name,
            'type': 'ir.actions.act_window',
            'res_model': self.model,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_id': self.res_id,
            'context': {'history_revision': create_date},
        }
        _logger.info("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",x)
        return x
