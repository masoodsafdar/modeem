# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from odoo import api, fields, models, _
from tempfile import TemporaryFile
import tempfile
import base64
import xlrd
import logging

from odoo.exceptions import ValidationError
import xmlrpc.client as xmlrpclib
_logger = logging.getLogger('_______logger ____________')


class ImportMaknoonExcelStudent(models.TransientModel):
    _name = 'mk.import.mosque'
    _description = 'Import mosque Excel File Data'

    file = fields.Binary('XLS File', required=True)

    def _get_district_name(self,district):
        name=district.split(' ')
        stripped_name = ''
        for rec in name:
            stripped_name +=rec +' '
        return stripped_name

    def import_mosques(self):
        # file_path = 'C:\\Users\\Pc\\Desktop\\maknoon\\synch_administrative_educational\\final_data.xlsx'
        _logger.info('\n\n ________ START ________ \n\n' )

        file_path = tempfile.gettempdir() + '/final_data.xls'
        data = self.file
        try:
            f = open(file_path, 'wb')
            decode = base64.b64decode(data)
            f.write(decode)
            f.close()
        except OSError:
            pass

        workbook = xlrd.open_workbook(file_path)
        sheets = workbook.sheets()
        _logger.info('\n\n ________ sheets : %s\n\n', sheets)


        for i in range(len(sheets)):
            _logger.info('\n\n ________ sheet %s|%s\n\n', i, len(sheets))
            writed = 0
            archived = 0
            synchronized = 0
            mq_not_exist = []
            mq_not_writed = []
            sheet = sheets[i]
            if sheet.ncols != 0:
                for rowx in range(1,sheet.nrows):
                    rowx += 1
                    len_nr = len(range(sheet.nrows))
                    if rowx < len_nr:
                        try:
                            cols = sheet.row_values(rowx)
                            educational_id = cols[5]
                            if len(str(educational_id))>0 and type(educational_id) is float:
                                episode_type = cols[0].strip()
                                if episode_type:
                                    if episode_type == 'مجمع تعليمي [ رجالي ]':
                                        ep_code = '00006'
                                    elif episode_type == 'مجمع قرآني [ رجالي ]':
                                        ep_code = '00007'
                                    elif episode_type == 'حلقات اعتيادية [ رجالي ]':
                                        ep_code = '00005'
                                    elif episode_type == 'مدرسة نسائية صباحية [ نسائي ]':
                                        ep_code = '00008'
                                    elif episode_type == 'مدرسة نسائية مسائية [ نسائي ]':
                                        ep_code = '00009'

                                    ep_type = self.env['mk.mosque.category'].sudo().search([('code', 'like', ep_code)], limit=1)
                                mosque_type = cols[1].strip()
                                if mosque_type:
                                    mosq_type = self.env['hr.department.category'].search([('name', 'like', mosque_type)], limit=1)

                                mosque_name = cols[2]
                                complexe_name = cols[3]
                                district_name = cols[4].strip()
                                vals = {}
                                if district_name and district_name not in['لايوجد','حي العارض لا يوجد في الأكواد','لا يوجد في الأكواد']:
                                    district = self.env['res.country.state'].sudo().search([('name', 'like', district_name)], limit=1)
                                    if not district:
                                        name = self._get_district_name(district_name)
                                        district = self.env['res.country.state'].sudo().search([('name', 'ilike', name.strip())], limit=1)
                                    if district:
                                        vals.update({'district_id':district.id})


                                educational_code = cols[6]

                                admin_id = cols[7]
                                admin_code = cols[8]

                                if educational_id and len(str(educational_id)) >= 1:
                                    mosque = self.env['mk.mosque'].sudo().search([('id', '=', int(educational_id)),
                                                                                  '|',('active', '=', True),
                                                                                       ('active', '=', False)], limit=1)
                                    _logger.info('\n\n ________ mosque with id : %s\n\n', mosque)

                                    if not mosque:
                                        if type(educational_code) is float:
                                            code = str(int(educational_code))
                                        else:
                                            code = str(educational_code)
                                        mosque = self.env['mk.mosque'].sudo().search([('register_code', '=', code),
                                                                                      '|', ('active', '=', True),
                                                                                           ('active', '=', False)], limit=1)
                                        _logger.info('\n\n ________ mosque with code : %s\n\n', mosque)

                                vals.update({'name': mosque_name,
                                            'complex_name': complexe_name,
                                            'mosq_type': mosq_type.id,
                                            'categ_id': ep_type.id})
                                _logger.info('\n\n ________ mosque vals : %s\n\n', vals)
                                if mosque:
                                    if mosque.active == True:
                                        mosque.sudo().write(vals)
                                        writed += 1
                                        _logger.info('\n\n ________ mosque writed \n\n')
                                        mosque.is_synchronized_admin = True
                                        synchronized += 1
                                    else:
                                        archived += 1
                                        mq_not_writed.append(int(educational_id))
                                else:
                                   mq_not_exist.append(int(educational_id))

                        except Exception as e:
                            _logger.info('\n\n ________ Exception as e : %s\n\n', e)
                            raise ValidationError(_('يوجد اشكال في بيانات السطر' + ' ' + str(rowx)))
                    _logger.info('\n\n ________ row  %s|%s|%s|%s\n\n', rowx,writed, archived,sheet.nrows)

            _logger.info('\n\n ________ mq_not_writed     %s\n\n', mq_not_writed)
            _logger.info('\n\n ________ len mq_not_writed     %s\n\n', len(mq_not_writed))

            _logger.info('\n\n ________ mq_not_exist     %s\n\n', mq_not_exist)
            _logger.info('\n\n ________ lenn mq_not_exist     %s\n\n', len(mq_not_exist))

        _logger.info('\n\n ________ END ________ \n\n' )


        return True

    def _redundant_id(self, id, sheet, row):
        for rowx in range(2, sheet.nrows):
            if rowx != row:
                cols = sheet.row_values(rowx)
                if cols[7] == id:
                    return True
        return False

    def import_unified_code(self):
        _logger.info('\n\n ________ START ________ \n\n' )

        file_path = tempfile.gettempdir() + '/final_data.xls'
        data = self.file
        try:
            f = open(file_path, 'wb')
            decode = base64.b64decode(data)
            f.write(decode)
            f.close()
        except OSError:
            pass

        workbook = xlrd.open_workbook(file_path)
        sheets = workbook.sheets()
        _logger.info('\n\n ________ sheets : %s\n\n', sheets)

        for i in range(len(sheets)):
            _logger.info('\n\n ________ sheet %s|%s\n\n', i, len(sheets))
            writed = 0
            sheet = sheets[i]
            if sheet.ncols != 0:
                for rowx in range(1,sheet.nrows):
                    rowx += 1
                    len_nr = len(range(sheet.nrows))
                    if rowx < len_nr:
                        try:
                            cols = sheet.row_values(rowx)
                            educational_id = cols[5]
                            educational_code = cols[6]
                            admin_id = cols[7]
                            administrative_code = cols[8]

                            if len(str(educational_id))>0 and len(str(administrative_code)) > 0 :
                                redundant_id = self._redundant_id(admin_id, sheet, rowx)
                                if not redundant_id:
                                    mosque = self.env['mk.mosque'].sudo().search([('id', '=', int(educational_id)),
                                                                                  '|', ('active', '=', True),
                                                                                       ('active', '=', False)], limit=1)
                                    _logger.info('\n\n ________ mosque with id : %s\n\n', mosque)

                                    if not mosque:
                                        if type(educational_code) is float:
                                            code = str(int(educational_code))
                                        else:
                                            code = str(educational_code)
                                        mosque = self.env['mk.mosque'].sudo().search([('register_code', '=', code),
                                                                                      '|', ('active', '=', True),
                                                                                      ('active', '=', False)], limit=1)
                                        _logger.info('\n\n ________ mosque with code : %s\n\n', mosque)

                                    if mosque:
                                        if mosque.active == True:
                                            mosque.sudo().write({'code': str(administrative_code)})
                                            writed += 1
                                            _logger.info('\n\n ________ mosque writed \n\n')

                        except Exception as e:
                            _logger.info('\n\n ________ Exception as e : %s\n\n', e)
                            raise ValidationError(_('يوجد اشكال في بيانات السطر' + ' ' + str(rowx)))
                    _logger.info('\n\n ________ row  %s|%s|%s\n\n', rowx,writed,sheet.nrows)
        _logger.info('\n\n ________ END ________ \n\n' )
        return True

    @api.model
    def set_is_synchro_edu_admin_cron(self):
        _logger.info('\n\n ++++++++++++++++++ START ++++++++++++++++++ \n\n' )

        mosques2 = self.env['mk.mosque'].search([('is_synchronized_admin', '=', True)])
        total = len(mosques2)
        i = 0
        updated = 0
        _logger.info('\n\n ++++++++++++++++++ total 2    : %s', total)
        for mosq in mosques2:
            _logger.info('\n\n ++++++++++++++++++ mosq    : %s', mosq)
            _logger.info('\n\n ++++++++++++++++++ mosq    : %s', mosq)

            i +=1
            if "." in mosq.register_code:
                mosq.write({'register_code': mosq.register_code[:-2]})
            if mosq.code :
                mosq.write({'code': mosq.code[:-2]})
                updated += 1
            _logger.info('\n\n ++++++++++++++++++ 22   %s/%s/%s', i, updated, total)
        _logger.info('\n\n ++++++++++++++++++ END ++++++++++++++++++ \n\n' )


