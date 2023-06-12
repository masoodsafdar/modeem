from odoo import models,fields,exceptions,api
from langdetect import detect
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class mk_general_sending(models.Model):
    _name = 'mk.general_sending'
    _description = 'Maknoon Sms and Emails'

    name = fields.Char(string='Name',default="general sending library")

    def send(self, vals):
        mail_obj = self.env['mail.mail']
        msg_id = mail_obj.create(vals)
        #msg_id = mail_obj.create(vals)
        if msg_id:
            result=mail_obj.send([msg_id])
            return result

    def send_by_template(self, template_id, record_ids):        
        ids=[]
        returned=[]
        user = self.env['res.users'].search([('id','=',self.env.user.id)])
        resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)])
        employee_id = self.env['hr.employee'].search([('resource_id','in',resource.ids)])

        if  not user.partner_id.email:
            user.partner_id.update({'email': employee_id.work_email})
        
        template=self.env['mail.template'].search([('name', '=', str(template_id))],limit=1)
        #record_ids=record_ids.encode('utf-8')
        if template:
            res = []
            ids = record_ids.split(',', )

            for id in ids:
                res.append(int(id))
            
            ids = self.env[template.model].search([('id', 'in', res)])
            for record in res:
                if record in ids.ids:
                    result=template.send_mail(record, force_send=True)
                    returned.append(result)
                    
            return returned
             
    def get_phone(self, parent_phone, country_id,output=True):
        if parent_phone and country_id:
            if len(str(parent_phone))==9:
                if str(parent_phone)[0]!= '0':
                    if country_id.phone_code:
                    	return str(country_id.phone_code)+str(parent_phone)
                    else:
                        if output==False:
                            return 'please enter country phone code'
                        """
                        else:
                            raise UserError(_('please enter country phone code '))
                        """
            else:
                if output==False:
                    return 'phone number must contain 9 digits'
                """
                if output==True:         
                    raise Warning(_('phone number must contain 9 digits'))
                else:
                    return 'phone number must contain 9 digits' 
                #return False
                """
                
        else:
            if output==False:
                return 'Please insert phone number and country code'
            """
            if output==True:
            
                raise UserError(_('Please insert phone number and country code'))
            else:
                return 'Please insert phone number and country code'
            """

    # to : return value of calling get_phone, messsage
    def send_sms(self, to, message):
        sms_partner_obj=self.env['partner.sms.send']
        if len(to)==9:
            to='966'+to
        result=sms_partner_obj.send(to, message)
        if result:
            return True

class new_sms_partner(models.Model):
    _inherit = 'partner.sms.send'

    def validate_message(self, text):
        language=detect(text)
        points=0
        no_of_messages=0
        extension=153
        length=0
        validity=False
        if language == "en":
            extension= 153
            if len(text) <= 160:
                no_of_messages=1
        elif language=="ar":
            extension = 67
            if len(text) <= 70:
                no_of_messages = 1
        text_lst=[text[i:i+extension] for i in range(0, len(text),extension)]
        no_of_messages=len(text_lst)
        if no_of_messages <= 10:
            validity=True
        if not validity:
            raise exceptions.except_orm(_('Error'), _('Message is too long'))

        return validity

    def send(self,  phone, message):
        # if context is None:
        #     context = {}
        client_obj = self.env['smsclient']
        #default_gateway=self.default_get(self._cr, self._uid,['gateway_id'],self._context)
        #default_gateway=[]
        default_gateway=self.env['smsclient'].search([],limit=1)

        # if default_gateway:
        #     default_gateway=default_gateway.browse([default_gateway[0].id])
        if not default_gateway:
            try:
                raise exceptions.except_orm(_('Error'), _('No Gateway Found'))
                #raise UserError(_("No Gateway Found"))
            except:
                return False
        else:
            vals = {
                'gateway_id':default_gateway[0].id,
                'mobile_to':phone,
                'text':message
            }
            sms_obj_id=self.create(vals)
            sms_obj=self.browse([sms_obj_id[0].id])
            if self.validate_message(sms_obj.text):
                client_obj._send_message(sms_obj)
        return True
