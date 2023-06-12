from odoo import models, fields, api, tools
import datetime
from odoo.exceptions import Warning
from odoo import models, fields, api, tools
import datetime
from odoo.exceptions import Warning
class mk_comments_and_behavior(models.Model):
    _name='mk.comments.behavior.students'
    _rec_name="date"
    teacher = fields.Many2one(
        'hr.employee',
        string='Teacher'
    )
    episode=fields.Many2one(
		'mk.episode',
        string='Episode',
        required=True,ondelete='restrict'
		)
    date=fields.Date(string="Date",required=True)
    masjed=fields.Many2one("mk.mosque","mosque",ondelete='restrict')
    period_id = fields.Many2one('mk.periods', string='Period',readonly=True,ondelete='restrict')
    Period=fields.Selection([('subh', 'Subh'), ('zuhr', 'Zuhr'),('aasr', 'Aasr'),('magrib', 'Magrib'),('esha', 'Esha')],readonly=True)
    period_time=fields.Char(string="period time",store=True)

    @api.onchange('episode')
    def episode_onchange(self):
        episode_object=self.env['mk.episode']
        episode_ids=episode_object.search([('id','=',self.episode.id)])
        if episode_ids:
            self.period_id=episode_ids[0].period_id

            if episode_ids[0].subh:
              self.Period="subh"  
            elif episode_ids[0].zuhr:
              self.Period="zuhr"                  
            elif episode_ids[0].aasr:
              self.Period="aasr"                  
            elif episode_ids[0].magrib:
              self.Period="magrib"                  
            elif episode_ids[0].esha:
              self.Period="esha"
                              

    @api.onchange('period_id')
    def Period_onchange(self):
        if self.Period:
            if self.Period=='subh':
                time = 'from ' +  str(self.period_id.subh_period_from) +' ' +'to ' + str(self.period_id.subh_period_to)  
            elif self.Period=='zuhr':
                time = 'from ' +  str(self.period_id.zuhr_period_from) +' ' +'to ' + str(self.period_id.zuhr_period_to)  
            elif self.Period=='aasr':
                time = 'from ' +  str(self.period_id.aasr_period_from) +' ' +'to ' + str(self.period_id.aasr_period_to)  
            elif self.Period=='magrib':
                time = 'from ' +  str(self.period_id.magrib_period_from) +' ' +'to ' + str(self.period_id.magrib_period_to)  
            elif self.Period=='esha':
                time = 'from ' +  str(self.period_id.esha_period_from) +' ' +'to ' + str(self.period_id.esha_period_to)  

            self.period_time=time 

    student_ids=fields.One2many("mk.comments.behavior.student.lines","link_id","students")
       
class student_comments_and_behavior(models.Model):  
    _name='mk.comments.behavior.student.lines'

    student =fields.Many2one("mk.link",string="Student",required=True,ondelete='restrict')
    comment_id=fields.Many2one("mk.comment.behavior","comment",required=True,ondelete='restrict')
    punishment_id=fields.Many2one("mk.punishment","punishment",ondelete='restrict')
    link_id=fields.Many2one("mk.comments.behavior.students",string="comment and behavior",ondelete='cascade')

    @api.onchange('comment_id')
    def comment_onchange(self):
        punishment_ids=[]
        if self.comment_id:
            for rec in self.comment_id.punishment_ids:
                punishment_ids.append(rec.id)
        return {'domain':{'punishment_id':[('id','in',punishment_ids)]}}

    # @api.multi
    def get_student_behavior_rec(self,student_id):
        #this fuction is return student behavior record of Entred student_id
        #behavior_obj = self.env['mk.comments.behavior.student.lines']*

        student_ids = self.search([('student','=',student_id)])


        records=[]
        rec_dict=[]
        for rec in student_ids:
            links_id = rec.student
            student_name = links_id.student_id.display_name
            episode_id =links_id.episode_id
            episode_name =links_id.episode_id.name
            comment_name =rec.comment_id.name
            if rec.punishment_id:
                punishment_name = rec.punishment_id.name
            else:
                punishment_name = ''
            date=rec.link_id.date
            teach_name =rec.link_id.teacher.name
            masjed_name =rec.link_id.masjed.name

            rec_dict=({
                'id':rec.id,
                'student_id':student_id,
                'student_name':str(student_name),
                'episode_id':episode_id.id,
                'episode_name':str(episode_name),
                'comment_name':str(comment_name),
                'punishment_name':str(punishment_name),
                'teacher_name':str(teach_name),
                'masjed_name':str(masjed_name),
                'punish_date':date,
                'period':rec.link_id.period_id.id,
                'date':rec.create_date,
            })
            records.append(rec_dict)
        return records

