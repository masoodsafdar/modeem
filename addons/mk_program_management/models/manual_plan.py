from odoo import models, fields, api


class MkmanualPlan(models.Model):
    _name = 'mk.manual.plan'
    
    #primary fields
    is_test     = fields.Boolean('is test')
    from_surah  = fields.Many2one('mk.surah',        string='From Sura', ondelete='restrict')
    # from aya
    from_aya    = fields.Many2one('mk.surah.verses', string='From Aya',  ondelete='restrict')
    #sura 2
    to_surah    = fields.Many2one('mk.surah',        string='To Sura',   ondelete='restrict')
    #aya2
    to_aya      = fields.Many2one('mk.surah.verses', string='To Aya',    ondelete='restrict')
    order       = fields.Integer('Order', default=1)
    type_follow = fields.Selection([('listen',       'Listening'),
								    ('review_small', 'Smll Review'),
								    ('review_big',   'Big Review'),
								    ('tlawa',        'Recitation')], string='Type of Follow', required=True)
    approche_id = fields.Many2one('mk.approaches', string='approche')
    small_id    = fields.Many2one('mk.approaches', string='approche')
    big_id      = fields.Many2one('mk.approaches', string='approche')
    tlawa_id    = fields.Many2one('mk.approaches', string='approche')

    @api.onchange('from_surah')
    def _onchange_from(self):
        self.from_aya=False

    @api.onchange('to_surah')
    def _onchange_to(self):
        self.to_aya=False
