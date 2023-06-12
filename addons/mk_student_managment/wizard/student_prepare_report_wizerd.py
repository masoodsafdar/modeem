from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class StudentPrepareReport(models.TransientModel):
    _name = 'student.prepare.report'

    student_id = fields.Many2one("mk.link","student", required=True, String="Student")
    episode_id = fields.Many2one("mk.episode","Episode", required=True)

    def print_report(self):
        datas = self.get_data_report(self.student_id.id)
        return self.env.ref('mk_student_managment.student_prepare_report').report_action(self, data=datas)

    def get_data_report(self, link_id):
        student_prepare = self.env['mk.student.prepare'].search([('link_id','=', link_id)],limit=1)

        link    = self.env['mk.link'].search([('id', '=', link_id)], limit=1)

        listen_records = []
        review_small_records = []
        review_big_records = []
        tlawa_records = []
        listen_plan_lines = self.env['mk.listen.line'].search([('preparation_id','=',student_prepare.id),
                                                               ('type_follow','=','listen')])
        for listen_line in listen_plan_lines:
            listen_records += [
                        {'date':   listen_line.date,
                         'state': listen_line.state,
                         'from_surah': listen_line.from_surah.name,
                         'from_aya': listen_line.from_aya.original_surah_order,
                         'to_surah': listen_line.to_surah.name,
                         'to_aya': listen_line.to_aya.original_surah_order}
                         ]

        review_small_plan_lines = self.env['mk.listen.line'].search([('preparation_id', '=', student_prepare.id),
                                                                     ('type_follow', '=', 'review_small')])
        for review_small_line in review_small_plan_lines:
            review_small_records += [
                {'date': review_small_line.date,
                 'state': review_small_line.state,
                 'from_surah': review_small_line.from_surah.name,
                 'from_aya': review_small_line.from_aya.original_surah_order,
                 'to_surah': review_small_line.to_surah.name,
                 'to_aya': review_small_line.to_aya.original_surah_order}
            ]

        review_big_plan_lines = self.env['mk.listen.line'].search([('preparation_id', '=', student_prepare.id),
                                                                     ('type_follow', '=', 'review_big')])
        for review_big_line in review_big_plan_lines:
            review_big_records += [
                {'date': review_big_line.date,
                 'state': review_big_line.state,
                 'from_surah': review_big_line.from_surah.name,
                 'from_aya': review_big_line.from_aya.original_surah_order,
                 'to_surah': review_big_line.to_surah.name,
                 'to_aya': review_big_line.to_aya.original_surah_order}
            ]

        tlawa_plan_lines = self.env['mk.listen.line'].search([('preparation_id', '=', student_prepare.id),
                                                              ('type_follow', '=', 'tlawa')])
        for tlawa_line in tlawa_plan_lines:
            tlawa_records += [
                {'date': tlawa_line.date,
                 'state': tlawa_line.state,
                 'from_surah': tlawa_line.from_surah.name,
                 'from_aya': tlawa_line.from_aya.original_surah_order,
                 'to_surah': tlawa_line.to_surah.name,
                 'to_aya': tlawa_line.to_aya.original_surah_order}
            ]

        form = {'student': link.student_id.display_name,
                'episode': link.episode_id.display_name,
                'listen_lines': listen_records,
                'review_small_lines': review_small_records,
                'review_big_records': review_big_records,
                'tlawa_records': tlawa_records,
                }

        datas = {'ids': [],
                'model': 'student.prepare.report',
                'form': form}

        return datas

    def get_pdf(self, link_id):
        return self.env.ref('mk_student_managment.student_prepare_report').render_qweb_pdf(self.ids, data = self.get_data_report(link_id))
