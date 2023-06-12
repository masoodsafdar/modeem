from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

class vehicle_records(models.Model):
    _name = 'vehicle.records'   


    
    Vehicle_Type=fields.Many2one('vehicle.types', )
    serial_no=fields.Char('Serial No')
    model=fields.Char('Model')
    form_exp_date=fields.Date('Form Expired Date')
    insurance= fields.Char()
    insurance_exp_date =fields.Date('Insurance Expired Date') 
    responsible= fields.Many2one('hr.employee', 'Responsible', domain="[('category','=','admin')]")
    superviser_id= fields.Many2one('hr.employee','Bus Supervisor', domain="[('category','=','bus_sup')]")
    driver= fields.Many2one('drivers.records', 'Driver')
    no_of_seats= fields.Integer('Number of Seats')
    center_id=fields.Many2one('hr.department', 'Center') 
    mosque=fields.Many2one('mk.mosque', 'Mosque',domain="[('center_department_id','=',self.center_id.id)]")
    Property=fields.Many2one('mk.vehicle.asset', 'Property')

    rent_info = fields.Char('Rent Info')



    work_days= fields.Many2many('mk.work.days', string='vehicle work Days')
    #work_periods=fields.Selection([('subh', 'subh'),('zuhr', 'zuhr'),('aasr','aasr'),('magrib','magrib'),('esha','esha')])
    
    work_period_subh=fields.Boolean()
    work_period_zuhr=fields.Boolean()
    work_period_aasr=fields.Boolean()
    work_period_magrib=fields.Boolean()
    work_period_esha=fields.Boolean()
    vehicle_created = fields.Boolean(
        string='Vehicle created',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )
    

    @api.model
    def create(self,vals):
        vehicle_manag_obj=self.env['vehicle.management']
        id=super(vehicle_records, self).create(vals)
        periods=[]
        lines=[]
        #('subh', 'subh'),('zuhr', 'zuhr'),('aasr','aasr'),('magrib','magrib'),('esha','esha')
        if vals['work_period_subh']:
            periods.append('subh')
        if vals['work_period_zuhr']:
            periods.append('zuhr')
        if vals['work_period_aasr']:
            periods.append('aasr')
        if vals['work_period_magrib']:
            periods.append('magrib')
        if vals['work_period_esha']:
            periods.append('esha')
        
        for day in vals['work_days'][0][2]:
            for period in periods:
                lines.append((0,0,{'work_days':day,'work_periods':period,'go_return':'go','avilable_seats':vals['no_of_seats']}))
                lines.append((0,0,{'work_days':day,'work_periods':period,'go_return':'return','avilable_seats':vals['no_of_seats']}))
        vehicle_rec=vehicle_manag_obj.sudo().create({'vehicle_id':id.id,'max_capcity':vals['no_of_seats'],'v_lines':lines})
        if vehicle_rec:
            id.sudo().write({'vehicle_created':True})


        return id

    @api.multi
    def name_get(self):
        
        result = []
        
        for record in self:
            result.append((record.id,"%s %s" % (record.Vehicle_Type.name, record.model)))
        return result

    @api.onchange('mosque')
    def get_responsible(self):
        for rec in self:
            rec.responsible=rec.mosque.responsible_id.id



    @api.multi
    def write(self, vals):
        vehicle_rec=self.env['vehicle.management'].sudo().search([('vehicle_id','=',self.id)])
        lines=[]
        periods=[]
        '''
        if vals.get('no_of_seats') and vehicle_rec:
            raise ValidationError(_('عذرا ! لا يمكنك تعديل عدد مقاعد المركبة'))
        '''
        
        if vals.get('work_days'):
            diff=set(vals.get('work_days')[0][2])-set(self.work_days.ids)
            if diff:
                
                if self.work_period_subh:
                    periods.append('subh')
                if self.work_period_zuhr:
                    periods.append('zuhr')
                if self.work_period_aasr:
                    periods.append('aasr')
                if self.work_period_magrib:
                    periods.append('magrib')
                if self.work_period_esha:
                    periods.append('esha')
                for day in diff:

                    for period in periods:
                        lines.append((0,0,{'work_days':day,'work_periods':period,'go_return':'go','avilable_seats':self.no_of_seats}))
                        lines.append((0,0,{'work_days':day,'work_periods':period,'go_return':'return','avilable_seats':self.no_of_seats}))
                vehicle_rec.sudo().write({'v_lines':lines})

            removed=list(set(self.work_days.ids)-set(vals.get('work_days')[0][2]))
            if removed:
                vehicle_lines=self.env['vehicle.emanagement.line'].sudo().search([('vehicle_ide','=',vehicle_rec.id),('work_days','in',removed),('avilable_seats','<',vehicle_rec.max_capcity)])
                if vehicle_lines:
                    raise ValidationError(_('عفوا ! لا يمكن حذف يوم من  الأيام المرتبطة بطلبات نقل'))




        if 'work_period_subh' in vals:
        
            if vals.get('work_period_subh') == False:
                

                vehicle_lines=self.env['vehicle.emanagement.line'].sudo().search([('vehicle_ide','=',vehicle_rec.id),('work_periods','=','subh'),('avilable_seats','<',vehicle_rec.max_capcity)])
                if vehicle_lines:
                    raise ValidationError(_('عفوا ! لا يمكن حذف فترة الصبح لإرتباط طلاب بها'))
            else:
                for day in self.work_days.ids:
                    lines.append((0,0,{'work_days':day,'work_periods':'subh','go_return':'go','avilable_seats':self.no_of_seats}))
                    lines.append((0,0,{'work_days':day,'work_periods':'subh','go_return':'return','avilable_seats':self.no_of_seats}))

        
        if 'work_period_zuhr' in vals:
            if  vals.get('work_period_zuhr') == False:
                

                vehicle_lines=self.env['vehicle.emanagement.line'].sudo().search([('vehicle_ide','=',vehicle_rec.id),('work_periods','=','zuhr'),('avilable_seats','<',vehicle_rec.max_capcity)])
                if vehicle_lines:
                    raise ValidationError(_('عفوا ! لا يمكن حذف فترة الظهر لإرتباط طلاب بها'))
            else:
                for day in self.work_days.ids:
                    lines.append((0,0,{'work_days':day,'work_periods':'zuhr','go_return':'go','avilable_seats':self.no_of_seats}))
                    lines.append((0,0,{'work_days':day,'work_periods':'zuhr','go_return':'return','avilable_seats':self.no_of_seats}))

        if 'work_period_aasr' in vals:
            if  vals.get('work_period_aasr')== False:


                vehicle_lines=self.env['vehicle.emanagement.line'].sudo().search([('vehicle_ide','=',vehicle_rec.id),('work_periods','=','aasr'),('avilable_seats','<',vehicle_rec.max_capcity)])
                if vehicle_lines: 
                    raise ValidationError(_('عفوا ! لا يمكن حذف فترة العصر لإرتباط طلاب بها'))
            else:
                for day in self.work_days.ids:
                    lines.append((0,0,{'work_days':day,'work_periods':'aasr','go_return':'go','avilable_seats':self.no_of_seats}))
                    lines.append((0,0,{'work_days':day,'work_periods':'aasr','go_return':'return','avilable_seats':self.no_of_seats}))

        if 'work_period_magrib' in vals:
            if  vals.get('work_period_magrib')== False:


                vehicle_lines=self.env['vehicle.emanagement.line'].sudo().search([('vehicle_ide','=',vehicle_rec.id),('work_periods','=','magrib'),('avilable_seats','<',vehicle_rec.max_capcity)])
                if vehicle_lines:
                    raise ValidationError(_('عفوا ! لا يمكن حذف فترة المغرب لإرتباط طلاب بها'))
            else:
                for day in self.work_days.ids:
                    lines.append((0,0,{'work_days':day,'work_periods':'magrib','go_return':'go','avilable_seats':self.no_of_seats}))
                    lines.append((0,0,{'work_days':day,'work_periods':'magrib','go_return':'return','avilable_seats':self.no_of_seats}))
        if 'work_period_esha' in vals:
            if  vals.get('work_period_esha')== False:


                vehicle_lines=self.env['vehicle.emanagement.line'].sudo().search([('vehicle_ide','=',vehicle_rec.id),('work_periods','=','esha'),('avilable_seats','<',vehicle_rec.max_capcity)])
                if vehicle_lines:
                    raise ValidationError(_('عفوا ! لا يمكن حذف فترة العشاء لإرتباط طلاب بها'))
            else:
                for day in self.work_days.ids:
                    lines.append((0,0,{'work_days':day,'work_periods':'esha','go_return':'go','avilable_seats':self.no_of_seats}))
                    lines.append((0,0,{'work_days':day,'work_periods':'esha','go_return':'return','avilable_seats':self.no_of_seats}))
        return super(vehicle_records, self).write(vals)


