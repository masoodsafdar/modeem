# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from odoo import api, fields, models, _
from tempfile import TemporaryFile
import tempfile
import base64
import xlrd
import logging

from odoo.exceptions import ValidationError

logger = logging.getLogger('_______MD ____________')


class ImportMaknoonExcelStudent(models.TransientModel):
    _name = 'mk.import.student'
    _description = 'Import Students Excel File Data'

    mosque_id = fields.Many2one('mk.mosque', required=True, string='Mosque', domain=[('state', '=', 'accept')])
    file      = fields.Binary('XLS File',    required=True)
    path      = fields.Char('Path')

    def import_student(self):
        file_path = tempfile.gettempdir()+'/student.xls'
        data = self.file
        try:
            f = open(file_path,'wb')
            decode = base64.b64decode(data)
            f.write(decode)
            f.close()
        except OSError:
            pass

        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheets()[0]

        if sheet.ncols != 0:
            for rowx in range(sheet.nrows):
                rowx += 1
                len_nr = len(range(sheet.nrows))
                if rowx < len_nr:
                    try:
                        cols = sheet.row_values(rowx)
                        no_identity = True
                        identity_no = cols[0]
                        passport_no = cols[1]
                        if identity_no:
                            no_identity = False
                        name = cols[2]
                        second_name = cols[3]
                        fourth_name = cols[4]
                        mobile = cols[5]
                        email = cols[6]
                        birthdate = cols[7]
                        birth_date = ""
                        if birthdate:
                            birth_date = datetime(*xlrd.xldate_as_tuple(birthdate, 0))

                        grade = cols[8]
                        grad_id = False
                        if grade:
                            grade_obj = self.env['mk.grade'].search([('name', '=', grade)],limit=1)
                            if grade_obj:
                                grad_id = grade_obj.id
                        country = cols[9]
                        country_id = False
                        if country:
                            # country_obj = self.env['res.country'].search([('name', '=', country)],limit=1)
                            country_obj = self.env['res.country'].search([('name', 'like', '%' + country + '%')],limit=1)
                            if country_obj:
                                country_id = country_obj.id

                        district = cols[10]
                        district_id = False
                        if district:
                            district_obj = self.env['res.country.state'].search([('name', '=', district)],limit=1)
                            if district_obj:
                                district_id = district_obj.id
                        student = self.env['mk.student.register'].search(['|', '&', ('identity_no','=',identity_no),('no_identity', '!=', True),
                                                                                '&', ('passport_no','=',passport_no),('no_identity', '=', True)], limit=1)
                        if student:
                            raise ValidationError(_('this student already exist which is in the line ' + ' ' + str(rowx)))
                            # student.write({'name': name,
                            #             'second_name': second_name,
                            #             'mobile': mobile,
                            #             'email': email,
                            #             'birthdate': birth_date,
                            #             'gender': gender,
                            #             'country_id':country_id,
                            #             'area_id':area_id,
                            #             'city_id':city_id,
                            #             'district_id':district_id,})
                        else:
                            student_new = self.env['mk.student.register'].create({'no_identity':  no_identity,
                                                                    'passport_no': passport_no,
                                                                    'identity_no': identity_no,
                                                                    'name': name,
                                                                    'second_name': second_name,
                                                                    'fourth_name': fourth_name,
                                                                    'mobile': str(mobile),
                                                                    'email': email,
                                                                    'birthdate': birth_date,
                                                                    'gender': self.mosque_id.categ_id.mosque_type,
                                                                    'mosq_id': self.mosque_id.id,
                                                                    'grade_id':grad_id,
                                                                    'country_id':country_id,
                                                                    'district_id':district_id,})
                            request = self.env['mk.link'].create({'mosq_id': student_new.mosq_id.id,
                                                                  'student_id': student_new.id,
                                                                  'state': 'draft'})
                            student_new.request_id = request.id
                    except:
                        raise ValidationError(_('يوجد اشكال في بيانات السطر' + ' ' + str(rowx)))

        return True
