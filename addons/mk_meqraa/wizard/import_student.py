# -*- coding: utf-8 -*-
from datetime import datetime,date,timedelta
from odoo import api, fields, models, _
from tempfile import TemporaryFile
import tempfile
import base64
import xlrd
import logging

from odoo.exceptions import ValidationError

logger=logging.getLogger('_______MD ____________')


class ImportExcelStudent(models.TransientModel):
    _name = 'import.student'
    _description = 'Import Students Excel File Data' 
    
    name =  fields.Char('Name')
    file = fields.Binary('XLS File', required=True)
    path = fields.Char('Path')
    
    def import_meqraa_student(self):
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
                        passport_no = cols[0]
                        no_identity = cols[1]
                        name = cols[2]
                        second_name = cols[3]
                        mobile = cols[4]
                        email = cols[5]
                        birthdate = cols[6]
                        birth_date = ""
                        if birthdate:
                            birth_date = datetime(*xlrd.xldate_as_tuple(birthdate, 0))
                        gender = cols[7]
                        khota_type = cols[8]
                        riwaya = cols[9]
                        memory_direction = cols[10]
                        country = cols[11]
                        country_id = False
                        if country:
                            country_obj = self.env['res.country'].search([('name', '=', country)],limit=1)
                            if country_obj:
                                country_id = country_obj.id
                        student = self.env['mk.student.register'].search([('passport_no', '=', passport_no)])
                        if student:
                            student.write({'name': name,
                                           'second_name': second_name,
                                           'mobile': mobile,
                                           'email': email,
                                           'birthdate': birth_date,
                                           'gender': gender,
                                           'khota_type': khota_type,
                                           'riwaya': riwaya,
                                           'memory_direction': memory_direction})
                        else:
                            self.env['mk.student.register'].create({'no_identity':  True,
                                                                   'is_student_meqraa':True,
                                                                   'passport_no':int(passport_no),
                                                                   'no_identity':no_identity,
                                                                   'name': name,
                                                                   'second_name': second_name,
                                                                   'mobile': int(mobile),
                                                                   'email': email,
                                                                   'birthdate': birth_date,
                                                                   'gender': gender,
                                                                   'khota_type': khota_type,
                                                                   'riwaya': riwaya,
                                                                   'memory_direction': memory_direction,
                                                                   'country_id': country_id})
                    except:
                        raise ValidationError(_('يوجد اشكال في بيانات السطر'+ ' '+ str(rowx)))

                                                            
        return True