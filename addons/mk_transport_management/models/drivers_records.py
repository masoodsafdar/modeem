from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class drivers_records(models.Model):
    _name = 'drivers.records'

    found_driver=0
    mosque_new =0
    new_rec=0

    @api.depends('identity_no')
    def get_drivers(self):
    	drivers=self.sudo().search([('identity_no','=', self.identity_no),('id','!=', self.id)], limit=1)
    	if drivers:
    		self.found_driver=drivers[0].id

    name =fields.Char('Driver' )
    found_driver = fields.Integer(
        string='Found driver',
        required=False,
        readonly=False,
        index=False,
        compute=get_drivers,
        default=0,
        help=False
    )
    country_id = fields.Many2one('res.country', string='Country')
    identity_no = fields.Char('Identity No', size=10)
    egama_exp_date = fields.Date()
    License_exp_date = fields.Date()
    phone_no = fields.Char('Phone No',size=9)
    driver_guarantor = fields.Char('Driver Guarantor')
    center_id=fields.Many2one('hr.department', 'Center')
    mosque_new=fields.Many2one('mk.mosque', 'new mosque')
    mosques = fields.Many2many(
        string='Mosque',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='mk.mosque',
        
    )
    flag = fields.Boolean(
        string='Flag',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )
    # vehicle_ids= fields.Many2one(comodel_name='vehicle.records',domain=[],context={},ondelete='cascade')
    driver_name = fields.Char(
        string='driver name',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=False
    )
    mosque_name = fields.Char(
        string='Mosque name',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=False
    )
    center_name = fields.Char(
        string='Center name',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=False
    )
    flag2 = fields.Boolean(
        string='Flag2',
        readonly=False,
        index=False,
        default=False,
        help=False
    )
    
    @api.model
    def create(self,vals):
        emp=self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)

        if vals['flag2']==True:
            drivers=self.sudo().search([('identity_no','=', vals['identity_no'])])
            if vals['mosque_new']:
                global mosque_new
                mosque_new= vals['mosque_new']
                vals['center_id']=emp.department_id.id
                vals['mosques']=[(4,id) for id in emp.mosqtech_ids.ids]
            
        else:
            vals['flag']=True
        return super(drivers_records, self).create(vals)
                                                                                                                

    @api.onchange('identity_no')
    def invistigate_identity(self):
        self.flag2=False
        self.driver_name=''
        self.mosque_name=''
        self.center_name=''
        if self.identity_no:

            if not self.create_date:
                drivers=self.sudo().search([('identity_no','=', self.identity_no)])
                global found_driver
                if drivers:
                    found_driver = drivers[0].id
                
                    #query_mosque="""select mk_mosque.name as mosque_name ,mk_mosque.id, hr_department.name from mk_mosque , hr_department where hr_department.id=mk_mosque.center_department_id and mk_mosque.id in( SELECT mk_mosque_id FROM mk_mosque_mk_student_register_rel where mk_student_register_id = %d);""" %(student[0]['id'])
                    #self.env.cr.execute(query_mosque)
                    #results=self.env.cr.dictfetchall()


                    
                    self.flag2=True
                    mosque_names=""
                    center_names=""

                    if not drivers[0].mosques:
                        mosque_names="لا يوجد حاليا إرتباط بمسجد"
                        center_names="لا يوجد حاليا إرتباط بمركز"
                    elif drivers[0].mosques:
	                    for rec in drivers[0].mosques:
	                        mosque_names+=rec.name
	                        mosque_names+=","
	                        center_names+=rec.center_department_id.name
	                        center_names+=","


                    self.driver_name=drivers[0].name
                    #self.mosque_id=[(4,emp.mosque_id.id)]
                    self.mosque_name=str(mosque_names)
                    self.center_name=str(center_names)
                    #self.name="_"
                else:
                    self.flag=True


    @api.multi
    def add_mosq(self):
        if mosque_new != 0:
            driver=self.sudo().search([('id','=', found_driver)])
            driver.sudo().write({'mosques':[(4,mosque_new)]})
            self.unlink()
            return {
                'type': 'ir.actions.act_window',
                'name': 'drivers_records_form_view',
                'res_model': 'drivers.records',
                'res_id': found_driver,
                'view_type': 'form',
                'view_mode': 'form',
                'target' : 'current',
                }

        '''

        if self.identity_no:
            query="""SELECT id, display_name FROM mk_student_register where identity_no = '%s' and date(create_date) < date(now());""" %(str(self.identity_no))
        elif self.passport_no:
            query="""SELECT id, display_name FROM mk_student_register where passport_no = '%s' and date(create_date) < date(now());""" %(str(self.passport_no))

        self.env.cr.execute(query)
        student=self.env.cr.dictfetchall()
        if student:
            query_mosque=""" SELECT mk_mosque_id FROM mk_mosque_mk_student_register_rel where mk_student_register_id = %d;""" %(student[0]['id'])
            self.env.cr.execute(query_mosque)
            results=self.env.cr.dictfetchall()
            if self.mosque_new.id in [result['mk_mosque_id'] for result in results]:
                self.create_date=False
                res={}
                res = self.env.ref('mk_student_register.warning_form',False)
                return {
                            'type': 'ir.actions.act_window',
                            'view_type': 'form',
                            'view_mode': 'form',
                                'views': [(res.id, 'form')],
                                'view_id': res.id,
                                'res_model': 'wizard.message',
                                'context': {'default_name':'هذا الطالب موجود مسبقا بالمسجد','default_passport':self.passport_no,'default_identity':self.identity_no,'default_original_id':self.id},
                                'nodestroy': True,
                                'target': 'new',
                                'res_id':  False,

                        } 
                delete_query='delete from mk_student_register where id = %d' %(self.id)
                self.env.cr.execute(delete_query)
          
            else:
                query2 ="""INSERT INTO public.mk_mosque_mk_student_register_rel(
                mk_student_register_id, mk_mosque_id)
                VALUES (%d, %d);""" % (student[0]['id'], self.mosque_new.id)
                self.env.cr.execute(query2)

        self.env.cr.execute('select id from mk_student_register order by id desc limit 1')

        id_returned = self.env.cr.fetchone()
        delete_query='delete from mk_student_register where id = %d' %(self.id)
        self.env.cr.execute(delete_query)
        form_view=self.env.ref('mk_student_register.view_student_register_form')
        return {

                    'type': 'ir.actions.act_window',
                    'res_model': 'mk.student.register',
                    'target': 'current',
                    'res_id':student[0]['id'],
                    'views': [(form_view.id,'form'),],
                    'nodestroy': False,
                    'tag':'reload'
                }
        '''
    '''
    @api.constrains('identity_no')
    def check_identity_no(self):
        
        
        ff=len(self.sudo().search([('identity_no','=',str(self.identity_no)),('id','!=',self.id)]))
        
        if ff:

            raise ValidationError(_('رقم الهوية المدخل موجود مسبقا'))
        if self.identity_no == 0:
            raise ValidationError(_('الرقم المدخل خطأ ﻷنه أصفار من فضلك أدخل الرقم الصحيح من واقع البطاقة'))
        
        if len(str(self.identity_no)) != 10:
            raise ValidationError(_('عذراٍ لابد من إدخال رقم هوية من 10 خانات'))

        if not str(self.identity_no).isdigit():
            raise ValidationError(_('فضلا رقم الهوية المدخل لابد ان يتكون من ارقام فقط'))
    '''
    
