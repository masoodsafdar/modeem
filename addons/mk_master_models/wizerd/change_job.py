#-*- coding:utf-8 -*-

##############################################################################
#
#    Copyright (C) Appness Co. LTD **hosam@app-ness.com**. All Rights Reserved
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from datetime import datetime
class change_job(models.TransientModel):
    """ The summary line for a class docstring should fit on one line.
                  user.write({'role_line_ids': [(6, 0, self.job_id.role_id)]})                                         
    Fields:
      name (Char): Human readable name which will identify each record.

    """

    _name = 'change.job'
    
    employee_id=fields.Many2one("hr.employee",string="employee")
    responsible_id=fields.Many2one("hr.employee",string="مسؤول المسجد", domain=[('category','=','admin')])


    job_id=fields.Many2one("hr.job")
    department_id=fields.Many2one("hr.department","Center name")
    teacher_id=fields.Many2many("hr.employee",'teach_change_rel','tech_id','emp_id',string="employee",domain=[('category','=','teacher')])


    mosque_id=fields.Many2many("mk.mosque",string="chose mosques / mosque")
    mosque_id2=fields.Many2many("mk.mosque","mosq_job_rel",'mos_id','rel_id',string="Mosque")

    @api.model
    def _get_priority_list(self):
        categories=self.env['hr.employee'].sudo()._get_priority_list()
        return  categories
        # # get logged user group
        # categories=[]
        #
        # active_id=self.env.context.get("active_id", False)
        # obj=self.env['hr.employee'].browse(active_id)
        #
        #
        #
        # user = self.env['res.users'].sudo().search([('id','=',self.env.user.id)])
        # #resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)])
        # employee_id = self.env['hr.employee'].sudo().search([('user_id','=',self.env.user.id)])
        # if  employee_id.category=='center_admin' or self.env.user.has_group('base.group_system'):
        #
        #    if obj.category=='admin':
        #
        #         categories.append(('teacher', 'المعلمين'))
        #         categories.append(('supervisor', 'مشرفين وإداريين المسجد / المدرسة'))
        #         categories.append(('managment','إداري\إداريين'))
        #
        #
        #
        #    if obj.category=='teacher' :
        #         categories.append(('admin', 'المشرف العام للمسجد /المدرسة'))
        #         categories.append(('supervisor', 'مشرفين وإداريين المسجد / المدرسة'))
        #         categories.append(('managment','إداري\إداريين'))
        #
        #
        #
        #
        #    if obj.category=='managment':
        #         categories.append(('admin', 'المشرف العام للمسجد /المدرسة'))
        #         categories.append(('supervisor', 'مشرفين وإداريين المسجد / المدرسة'))
        #         categories.append(('teacher', 'المعلمين'))
        #
        #    if obj.category=='supervisor':
        #         categories.append(('admin', 'المشرف العام للمسجد /المدرسة'))
        #         categories.append(('teacher', 'المعلمين'))
        #         categories.append(('managment','إداري\إداريين'))
        # else:
        #
        #    if obj.category=='teacher' :
        #         categories.append(('supervisor', 'مشرفين وإداريين المسجد / المدرسة'))
        #         categories.append(('managment','إداري\إداريين'))
        #
        #
        #
        #
        #    if  obj.category=='managment':
        #         categories.append(('supervisor', 'مشرفين وإداريين المسجد / المدرسة'))
        #         categories.append(('teacher', 'المعلمين'))
        #
        #    if  obj.category=='supervisor':
        #
        #         categories.append(('teacher', 'المعلمين'))
        #         categories.append(('managment','إداري\إداريين'))
        #
        # return categories

    @api.model
    def _get_flage(self):
        active_id=self.env.context.get("active_id", False)
        obj=self.env['hr.employee'].browse(active_id)
        flag=False
        if obj.category2=='teacher': 
               flag=True
        
        return flag

########################
    @api.model
    def _get_response(self):
        active_id=self.env.context.get("active_id", False)
        obj=self.env['hr.employee'].browse(active_id)
        flag2=False
        if obj.category2=='admin': 
               flag2=True
        
        return flag2

    #### HERE
    @api.onchange('employee_id')
    def onchange_em(self):
        active_id=self.env.context.get("active_id", False)
        obj=self.env['hr.employee'].browse(active_id)
        rec_episode=self.env['mk.episode'].search([('teacher_id','=',obj.id)])
        list_w=[]
        for episode in rec_episode:
          list_w.append({'ep_id':episode.id})

        self.update({'list_append':list_w})
        #return True
              

    category2=fields.Selection("_get_priority_list","category",readonly=False,store=True)  
    flage=fields.Boolean(string="is_dept",default=_get_flage) 
    flage2=fields.Boolean(string="is_dept",default=_get_response) 
    episode_ids=fields.Many2many("mk.episode",string="Episode")   

#     @api.onchange('category2')
#     def onchange_category_id(self):
#         list1=[]
#         if self.category2=='teacher':
#           cr = self.env.cr
#           query = """ select name,id from hr_job where name like'معلم%'
#
#   """
#           res={}
#
#           x=cr.execute(query)
#           user_ids = cr.dictfetchall()
#           for user in user_ids:
#             rec_user=user['id']
#             list1.append(rec_user)
#         if self.category2=='supervisor':
#           cr = self.env.cr
#           query = """ select name,id from hr_job where name like'مشرف%'
#
#   """
#           res={}
#           list1=[]
#           x=cr.execute(query)
#           user_ids = cr.dictfetchall()
#           for user in user_ids:
#             rec_user=user['id']
#             list1.append(rec_user)
#         if self.category2=='managment':
#           cr = self.env.cr
#           query = """ select name,id from hr_job where name like'%اداري%' or name like '%إداري%'
#
#
#
#
# """
#
#
#
#           res={}
#           list1=[]
#           x=cr.execute(query)
#           user_ids = cr.dictfetchall()
#           for user in user_ids:
#             rec_user=user['id']
#             list1.append(rec_user)
#         if self.category2=='admin':
#           cr = self.env.cr
#           query = """ select name,id from hr_job where name like'مشرف عام للمسجد%'
#
#   """
#           res={}
#
#           x=cr.execute(query)
#           user_ids = cr.dictfetchall()
#           for user in user_ids:
#             rec_user=user['id']
#             list1.append(rec_user)
#         return {'domain':{'job_id':[('id','in',list1)]}}


    # @api.multi
    def  yes(self):
        user=[]
        active_id=self.env.context.get("active_id", False)
        obj=self.env['hr.employee'].browse(active_id)
        user=self.env['res.users'].search([('login','=',obj.identification_id)])
        if user:       
           user=user[0]
        else:
           user=obj.user_id

        if self.category2=='teacher':
            #self.job_id.role_id.write({'line_ids':[(0,0,{'department_id':obj.department_id.id,'user_id':obj.user_id.id})]})
            group_ids = []
            if self.job_id.is_role==True:
               self.env['res.users.role.line'].sudo().create({'department_id':obj.department_id.id,'user_id':user.id,'role_id':self.job_id.role_id.id})

               for line in obj.job_id.sudo().role_id.line_ids:
                   if line.user_id==obj.user_id:
                      #obj.job_id.role_id.write({'line_ids':[(0,0,{'is_enabled':False})]})
                      line.unlink()

               groups=self.job_id.sudo().role_id.group_id.implied_ids.ids+[self.job_id.sudo().role_id.group_id.id]          
               user.sudo().write({'groups_id': [(4,group) for group in groups]})
               user.sudo().write({'sel_groups_1_11_12':1})
            else:
               user.sudo().write({'sel_groups_1_11_12':1}) 
           
            if self.mosque_id2:
               obj.write({'category2':self.category2,'category':self.category2,'job_id':self.job_id.id})
            if self.mosque_id:


               obj.write({'mosqtech_ids':[(5, id)for id in self.mosque_id.ids]})
               obj.write({'mosqtech_ids':[(4, id)for id in self.mosque_id.ids],'category2':self.category2,'category':self.category2,'job_id':self.job_id.id})
            if self.department_id:
               obj.write({'department_id':self.department_id.id})
            mosq=self.env['mk.mosque'].search([('responsible_id','=',obj.id)])
            for mosque in mosq: 
                if self.responsible_id:
                   mosque.write({'responsible_id':self.responsible_id.id}) 

                   self.responsible_id.write({'mosqtech_ids':[(4, id)for id in self.mosque_id2.ids]})               
                else:   
                    mosque.write({'responsible_id':False}) 
                  
        else:

              if self.category2=='supervisor' or self.category2=='managment' and self.employee_id.category=='teacher':
                  
                 if self.job_id.is_role==True:

                    self.env['res.users.role.line'].sudo().create({'department_id':obj.department_id.id,'user_id':user.id,'role_id':self.job_id.role_id.id})

                    for line in obj.job_id.sudo().role_id.line_ids:
                        if line.user_id==obj.user_id:
                           #obj.job_id.role_id.write({'line_ids':[(0,0,{'is_enabled':False})]})
                           line.unlink()

                    groups=self.job_id.sudo().role_id.group_id.implied_ids.ids+[self.job_id.sudo().role_id.group_id.id]          
                    user.sudo().write({'groups_id': [(4,group) for group in groups]})
                    user.sudo().write({'sel_groups_1_11_12':1})
                 else:
                    user.sudo().write({'sel_groups_1_11_12':1}) 
		    
                 for ep_rec in self.list_append:

                      if ep_rec.employee_id:
                         ep_rec.ep_id.write({'teacher_id':ep_rec.employee_id.id})
                      else:
                         ep_rec.ep_id.write({'teacher_id':False})
                  
              if self.category2=='admin' and self.employee_id.category=='teacher':

                 if self.job_id.is_role==True:

                    self.env['res.users.role.line'].sudo().create({'department_id':obj.department_id.id,'user_id':user.id,'role_id':self.job_id.role_id.id})

                    for line in obj.job_id.sudo().role_id.line_ids:
                        if line.user_id==obj.user_id:
                           #obj.job_id.role_id.write({'line_ids':[(0,0,{'is_enabled':False})]})
                           line.unlink()

                    groups=self.job_id.sudo().role_id.group_id.implied_ids.ids+[self.job_id.sudo().role_id.group_id.id]          
                    user.sudo().write({'groups_id': [(4,group) for group in groups]})
                    user.sudo().write({'sel_groups_1_11_12':1})
                 else:
                    user.sudo().write({'sel_groups_1_11_12':1}) 
            
                 for mosq in self.employee_id.mosqtech_ids:

                      mosq.write({'responsible_id':self.employee_id.id})                  

                 for ep_rec in self.list_append:

                      if ep_rec.employee_id:
                         ep_rec.ep_id.write({'teacher_id':ep_rec.employee_id.id})
                      else:
                          ep_rec.ep_id.write({'teacher_id':False})
              if self.category2=='supervisor' or self.category2=='managment' and self.employee_id.category!='teacher':

                 if self.job_id.is_role==True:

                    self.env['res.users.role.line'].sudo().create({'department_id':obj.department_id.id,'user_id':user.id,'role_id':self.job_id.role_id.id})

                    for line in obj.job_id.sudo().role_id.line_ids:
                        if line.user_id==obj.user_id:
                           #obj.job_id.role_id.write({'line_ids':[(0,0,{'is_enabled':False})]})
                           line.unlink()

                    groups=self.job_id.sudo().role_id.group_id.implied_ids.ids+[self.job_id.sudo().role_id.group_id.id]          
                    user.sudo().write({'groups_id': [(4,group) for group in groups]})
                    user.sudo().write({'sel_groups_1_11_12':1})
                 else:
                    user.sudo().write({'sel_groups_1_11_12':1}) 
                 mosq=self.env['mk.mosque'].search([('responsible_id','=',obj.id)])
                 for mosque in mosq: 
                     if self.responsible_id:
                        mosque.write({'responsible_id':self.responsible_id.id}) 
                        self.responsible_id.write({'mosqtech_ids':[(4, id)for id in self.mosque_id2.ids]})               
                     else:   
                         mosque.write({'responsible_id':False}) 
            
              if self.category2=='admin':
                 if self.job_id.is_role==True:

                    self.env['res.users.role.line'].sudo().create({'department_id':obj.department_id.id,'user_id':user.id,'role_id':self.job_id.role_id.id})

                    for line in obj.job_id.sudo().role_id.line_ids:
                        if line.user_id==obj.user_id:
                           #obj.job_id.role_id.write({'line_ids':[(0,0,{'is_enabled':False})]})
                           line.unlink()

                    groups=self.job_id.sudo().role_id.group_id.implied_ids.ids+[self.job_id.sudo().role_id.group_id.id]          
          
                    user.sudo().write({'groups_id': [(4,group) for group in groups]})
                    user.sudo().write({'sel_groups_1_11_12':1})
                 else:
                    user.sudo().write({'sel_groups_1_11_12':1}) 
            
                 for mosq in self.employee_id.mosqtech_ids:

                      mosq.write({'responsible_id':self.employee_id.id})

              if self.mosque_id2:
                  obj.write({'category2':self.category2,'category':self.category2,'job_id':self.job_id.id})
              if self.mosque_id:

                  obj.write({'mosqtech_ids':[(5, id)for id in self.mosque_id.ids]})
                  obj.write({'mosqtech_ids':[(4, id)for id in self.mosque_id.ids],'category2':self.category2,'category':self.category2,'job_id':self.job_id.id})
              if self.department_id:
                 obj.write({'department_id':self.department_id.id})  
 
    list_append=fields.One2many("episode.teacher","link","")
class change_job(models.TransientModel):
  _name='episode.teacher'
  link=fields.Many2one("change.job",string="list")
  ep_id=fields.Many2one("mk.episode","Episode")
  employee_id=fields.Many2one("hr.employee",string="teacher",domain=[('category','=','teacher')])
