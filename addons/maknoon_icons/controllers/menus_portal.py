# -*- coding: utf-8 -*-
import odoo.http as http
from odoo.http import  request
from odoo import SUPERUSER_ID
from lxml import etree as ElementTree
from odoo.addons.board.controllers.main import Board

import logging
_logger = logging.getLogger(__name__)


class WebFormController(http.Controller):    

    @http.route('/register/allowed_menus/<int:user_id>', type='json', auth='public',  csrf=False)
    def get_parent(self,user_id,**args):
        query = """select m.id, d.module||'.'||d.name as "name", m.action     
                   from ir_ui_menu m, ir_model_data d  
                   where m.parent_id is null and d.model='ir.ui.menu' and m.id=d.res_id and 
                         m.id in (select menu_id 
                                from ir_ui_menu_group_rel 
                                where gid in (select gid 
                                              from res_groups_users_rel 
                                              where uid = %d));""" %(user_id)
        request.env.cr.execute(query)
        result_dic = request.env.cr.dictfetchall()
        query2 = """select m.id, d.module||'.'||d.name as "name", m.action   
                    from ir_ui_menu m, ir_model_data d  
                    where m.parent_id is null and d.model='ir.ui.menu' and m.id=d.res_id and  
                          m.id not in (select menu_id 
                                     from ir_ui_menu_group_rel)"""
                                      
        request.env.cr.execute(query2)
        result = request.env.cr.dictfetchall()
        parent_menus = result + result_dic

        for menu in parent_menus:
            if menu['action']:
                menu['action'] = menu['action'].strip('ir.actions.act_window,')
                
            query3 = """select id, sequence, action 
                        from ir_ui_menu 
                        where parent_id = %d 
                        order by sequence limit 1;""" %(menu['id'])
            request.env.cr.execute(query3)
            result_no_action = request.env.cr.dictfetchall()
            
            if result_no_action:
                if result_no_action[0]['action']:
                    menu['first_child'] = result_no_action[0]['id']
                    menu['action'] = result_no_action[0]['action'].strip('ir.actions.act_window,')
                else:
                    query4 = """select id, sequence, action 
                                from ir_ui_menu 
                                where parent_id = %d and 
                                action is not null 
                                order by sequence limit 1;""" %(result_no_action[0]['id'])
                                
                    request.env.cr.execute(query4)
                    result_action = request.env.cr.dictfetchall()
                    
                    if result_action:
                        if result_action[0]['action']:
                            menu['first_child'] = result_action[0]['id']
                            menu['action'] = result_action[0]['action'].strip('ir.actions.act_window,')
                            
        for rec in parent_menus:
            if rec['action'] == None:
                rec['action'] = False

        return str(parent_menus)

class BoardInherit(Board):
    @http.route('/board/add_to_dashboard', type='json', auth='user')
    def add_to_dashboard(self, action_id, context_to_save, domain, view_mode, name=''):
        # Retrieve the 'My Dashboard' action from its xmlid
        action = request.env.ref('board.open_board_my_dash_action')

        if action and action['res_model'] == 'board.board' and action['views'][0][1] == 'form' and action_id:
            # Maybe should check the content instead of model board.board ?
            view_id = action['views'][0][0]
            board = request.env['board.board'].fields_view_get(view_id, 'form')
            if board and 'arch' in board:
                xml = ElementTree.fromstring(board['arch'])
                column = xml.find('./board/column')
                if column is not None:
                    new_action = ElementTree.Element('action', {
                        'name': str(action_id),
                        'string': name,
                        'view_mode': view_mode,
                        'context': str(context_to_save),
                        'domain': str(domain)
                    })
                    column.insert(0, new_action)
                    arch = ElementTree.tostring(xml, encoding='unicode')
                    print("***************request.session.uid:", request.session.uid)
                    if request.session.uid == SUPERUSER_ID:
                        user_ids = request.env['res.users'].search([])
                        print("***********len(user_ids):", len(user_ids))
                        for user in user_ids:
                            request.env['ir.ui.view.custom'].create({
                                'user_id': user.id,
                                'ref_id': view_id,
                                'arch': arch
                            })
                            print("************dashboard created for user****",user )
                    else:
                        request.env['ir.ui.view.custom'].create({
                            'user_id': request.session.uid,
                            'ref_id': view_id,
                            'arch': arch
                        })
                        print("************dashboard created for simple user****")
                    return True
        return False

