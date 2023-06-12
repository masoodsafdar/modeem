from odoo import models, fields, api, tools
import datetime
from odoo.exceptions import Warning
from odoo import models, fields, api, tools
import datetime
from odoo.exceptions import Warning
class student_attendace(models.Model):
    _name='mk.episode.attendace'
    _rec_name="date"
    teacher = fields.Many2one(
        'hr.employee',
        string='Teacher'
    )
    episode=fields.Many2one(
		'mk.episode',
        string='Episode',ondelete='restrict'
		)
    date=fields.Date(string="Date",required=True)
    masjed=fields.Many2one("mk.mosque","mosque",ondelete='restrict')
    student_ids=fields.One2many("mk.student.attendace","episode_attendace_id","students")
    period_id = fields.Many2one('mk.periods', string='Period',ondelete='restrict')

    subh = fields.Boolean('Subh')
    zuhr = fields.Boolean('Zuhr')
    aasr = fields.Boolean('Aasr')
    magrib = fields.Boolean('Magrib')
    esha = fields.Boolean('Esha')


    period_subh = fields.Char('Subh')
    period_zuhr = fields.Char('Zuhr')
    period_aasr = fields.Char('Aasr')
    period_magrib = fields.Char('Magrib')
    period_esha = fields.Char('Esha')

    @api.onchange('masjed')
    def _onchange_masjed(self):
       episode_ids=self.env['mk.episode'].search(['&',('mosque_id','=',self.masjed.id),('state','=','accept')])
       return {'domain':{'episode': [('id', 'in', episode_ids.ids)]}}


    @api.onchange('episode')
    def period_onchange(self):
        self.period_id=self.episode.period_id
        self.student_ids=False
        self.period_subh = ' '
        self.period_zuhr = ' '
        self.period_aasr = ' ' 
        self.period_magrib = ' '
        self.period_esha = ' '
        self.subh = False
        self.zuhr = False
        self.aasr = False
        self.magrib = False
        self.esha = False

        if self.episode.subh:
            self.period_subh = 's'
        if self.episode.zuhr:
            self.period_zuhr = 'z'
        if self.episode.aasr:
            self.period_aasr = 'a' 
        if self.episode.magrib:
            self.period_magrib = 'm'
        if self.episode.esha:
            self.period_esha = 'e'


    @api.onchange('subh')
    def subh_onchange(self):
        self.student_ids=False

    @api.onchange('zuhr')
    def zuhr_onchange(self):
        self.student_ids=False

    @api.onchange('aasr')
    def aasr_onchange(self):
        self.student_ids=False

        
    @api.onchange('magrib')
    def magrib_onchange(self):
        self.student_ids=False

    @api.onchange('esha')
    def esha_onchange(self):
        self.student_ids=False
                              

