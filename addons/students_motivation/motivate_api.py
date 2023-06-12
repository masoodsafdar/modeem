# -*- coding: utf-8 -*-
# import psycopg2
# import psycopg2.extras
# from flask import Flask,jsonify,request
# from flask_cors import CORS
# 
# 
# app = Flask(__name__)
# CORS(app)
# app.config['DEBUG'] = True
# 
# params = {
#             'database': 'dB_backup',
#             'user': 'amjed',
#             'password': 'admin',
#             'host': 'localhost',
#             'port': 8069
#         }
# 
# # params = {
# #             'database': 'hr_db',
# #             'user': 'balu',
# #             'password': 'balu',
# #             'host': 'localhost',
# #             'port': 5432
# #         }
# 
# conn = psycopg2.connect(**params)
# # print server.local_bind_port
# cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) #dict cursor 
# print "database connected"
#     
# @app.route('/motivate/')
# def index():
#     return 'Hello, you have reached the api server!'
# 
# @app.route('/motivate/product/')
# def product():
#     try:
#         query_string = ''' 
# 		select name,available_quantity,list_price  from product_template 
# 		where publish_prize ='t' ;
#         '''
#         cur.execute(query_string)
#         product_list = cur.fetchall()
#         return jsonify(product_list)
#     except Exception as e:
#         conn.rollback()
#         msg = {'error':str(e)}
#         return jsonify(msg),403
# 
# 
# @app.route('/motivate/teacher/episode')
# def episode():
#     try:
#         episode_id = request.args.get('episode_id')
#         employee_id = request.args.get('employee_id')
#         query_string = ''' 
#         select link.student_id as st,st_po.total_points as points from mk_link as link,
# 	mk_episode as ep,mk_student_register as reg,
# 	hr_employee as emp ,student_points as st_po where ep.id=link.episode_id and
# 	link.student_id=reg.id and ep.teacher_id=emp.id and link.state='accept' and st_po.name=link.student_id and ep.teacher_id={} and 
#         link.episode_id={};
#         '''.format(employee_id,episode_id)
#         cur.execute(query_string)
#         episode_list = cur.fetchall()
#         return jsonify(episode_list)
#     except Exception as e:
#         conn.rollback()
#         msg = {'error':str(e)}
#         return jsonify(msg),403
# 
# 
# @app.route('/motivate/item/list')
# def points():
#     try:       
#         query_string = ''' 
#         select name,points from standard_items ;
#         '''
#         cur.execute(query_string)
#         item_list = cur.fetchall()
#         return jsonify(item_list)
#     except Exception as e:
#         conn.rollback()
#         msg = {'error':str(e)}
#         return jsonify(msg),403
# 
# @app.route('/motivate/student/points')
# def student_points():
#     try:
#         student_id = request.args.get('student_id')       
#         query_string = ''' 
#         select total_points from student_points where name={};
#         '''.format(student_id)
#         cur.execute(query_string)
#         point = cur.fetchall()
#         return jsonify(point)
#     except Exception as e:
#         conn.rollback()
#         msg = {'error':str(e)}
#         return jsonify(msg),403
# 
# 
# @app.route('/motivate/student/request')
# def student_request():
#     try:
#         student_id = request.args.get('student_id')       
#         query_string = ''' 
#         select sale.name, sale.total_prize_points as total_points,
# sale.date_order as date ,line.name as product ,line.total_points as product_point,
# sale.state as state from sale_order as sale,sale_order_line as line 
# where line.order_id=sale.id and sale.student_id ={};
#         '''.format(student_id)
#         cur.execute(query_string)
#         request = cur.fetchall()
#         return jsonify(request)
#     except Exception as e:
#         conn.rollback()
#         msg = {'error':str(e)}
#         return jsonify(msg),403
# 
# 
# @app.route('/motivate/student/notify')
# def student_notify():
#     try:
#         student_id = request.args.get('student_id')       
#         query_string = ''' 
#         select count(id) from sale_order 
# where date_order+ INTERVAL '7 day' <= date('now') and state !='deliverd' and student_id ={} ;
#         '''.format(student_id)
#         cur.execute(query_string)
#         no = cur.fetchall()
#         return jsonify(no)
#     except Exception as e:
#         conn.rollback()
#         msg = {'error':str(e)}
#         return jsonify(msg),403
# 
# 
# @app.route('/motivate/student/save',methods = ['GET','POST'])
# def insert_point():
#     if request.method == 'POST':
#         try:
#             data = request.get_json(force = True)
#             student_id = data['student_id']
#             point = data['point']            
#             item = data['item']
#             query_string = ''' 
#             INSERT INTO
#             student_item
#             (student_id,item,point)
#             VALUES
#             ({},{},'{}')
#             RETURNING id;        
#             '''.format(student_id,point,item)
#             cur.execute(query_string)
#             return_row = cur.fetchall()
#             if len(return_row) > 0:
#                 msg = {'success':0}
#                 return jsonify(msg)
#             else:
#                 msg = {'success':1}
#                 return jsonify(msg)
#         except Exception as e:
#             msg = {'error':str(e)}
#             return jsonify(msg),403
