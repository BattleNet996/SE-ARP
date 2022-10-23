'''
@Time    : 2021/7/11 20:30 下午
@Author  : Tang Jiaxin, Wang Jiajie
服务器的各种功能
'''
# coding: utf-8
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import *
import json
import os
import io
import zipfile
import shutil
from werkzeug.utils import secure_filename
import sys
import time
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import string
import smtplib
import socks
import socket
from email.mime.text import MIMEText
from email.utils import formataddr
sys.path.append('./Merge')
sys.path.append('./Model')
sys.path.append('./database')
from BuildModel import Model
from Merge import Merge
from Visualization import Graph
from database.api import DBAction
app = Flask(__name__)
db = DBAction()
CORS(app, supports_credentials=True, resources=r"/*")


@app.route('/', methods = ['GET'])
def welcome():
        return 'welcome!'

def unfold(file_name, path):
        if not zipfile.is_zipfile(file_name):
                return False
        zip_file = zipfile.ZipFile(file_name)
        zip_list = zip_file.namelist()
        for f in zip_list:
                zip_file.extract(f, path)
        zip_file.close()
        return True


def fold(dirpath, resFilePath):
        print(dirpath, resFilePath)
        zip_file = zipfile.ZipFile(resFilePath, 'w', zipfile.ZIP_DEFLATED)
        for path, dirnames, filenames in os.walk(dirpath):
                fpath = path.replace(dirpath, '')
                for filename in filenames:
                        zip_file.write(os.path.join(path, filename), os.path.join(fpath, filename))
        zip_file.close()


@app.route('/file_upload', methods = ['POST'], strict_slashes = False)
def receive_file():
        basedir = os.path.dirname(__file__)
        usr_name = 'usr' + request.form['cookie'] #usr_name: usr0
        file_dir = os.path.join(basedir, 'files', usr_name) #file_dir: ./files/usr0
        if not os.path.exists(os.path.join(basedir, 'files')):
                os.makedirs(os.path.join(basedir, 'files'))
        if not os.path.exists(file_dir):
                os.makedirs(file_dir)
        app = request.form['app']
        datetime = time.asctime(time.localtime(time.time()))
        print(app)
        print(datetime)
        f = request.files['input_file']
        if not f:
                return jsonify({'state': 1001, 'msg': '无法获取上传的文件'})
        fname = secure_filename(f.filename) #fname: file_name.zip
        res_file_name = fname.split('.')[0] #res_file_name: file_name
        print(fname, res_file_name)
        file_list = os.listdir(file_dir) #file_list: all file_name in ./files/usr0
        for file_name in file_list: #file_name: file_name
                if file_name == res_file_name:
                        return jsonify({'state': 1003, 'msg': '该名称的文件已经存在'})
        file_path = os.path.join(file_dir, fname) #file_path: ./files/usr0/file_name.zip
        f.save(file_path)
        res = unfold(file_path, file_dir) #unfold ./files/usr0/file_name.zip to ./files/usr0
        print(usr_name, app, datetime, res_file_name)
        db.upload_data(usr_name, app, datetime, res_file_name)
        os.remove(file_path)
        if not res:
                return jsonify({'state': 1002, 'msg': '无法解压上传的文件'})
        return jsonify({'state': 200, 'msg': '上传成功'})


@app.route('/file_download', methods = ['GET', 'POST'])
def send_download_file():
        basedir = os.path.dirname(__file__)
        if request.method == 'GET':
                return 'ok'
        else:
                file_name = request.form['fileName'] #file_name: files/usr0/file_name/ or temp/tempfile0/
                print(file_name)
                file_name_list = file_name.split('/')
                kind = file_name_list[0] #kind :files or temp
                fname = ''
                usr_name = ''
                if kind == 'files':
                        usr_name = file_name_list[1] #usr_name: usr0
                        fname = file_name_list[2] #fname: file_name
                else:
                        fname = file_name_list[1] #fname: tempfile0
                fold_name = fname + '.zip' #fold_name: file_name.zip or tempfile0.zip
                fold_path = os.path.join(os.path.join(kind, usr_name), fold_name) #fold_path: files/usr0/file_name.zip or temp/tempfile0.zip
                if not os.path.exists(fold_path):
                        fold(file_name, fold_path)
                return send_from_directory(os.path.join(basedir, kind, usr_name), fold_name, as_attachment=True) #send file_name.zip in ./files/usr0 or tempfile0.zip in ./temp


def get_file_lines(file_name):
        f = open(file_name, 'r')
        count = -1
        for index, line in enumerate(f):
                count += 1
        f.close()
        return count


@app.route('/file_display', methods = ['POST'])
def send_display_file():
        basedir = os.path.dirname(__file__)
        data = json.loads(request.get_data(as_text=True))
        file_name = data['file'] #file_name: files/usr0/file_name
        print(file_name)
        file_path = os.path.join(basedir, file_name) #file_path: ./files/usr0/file_name
        if not os.path.exists(file_path):
                return jsonify({'state': 1004, 'msg': '无法打开希望获取的文件'})
        transitions_path = os.path.join(file_path, 'transitions.lst') #transitions_path: ./files/usr0/file_name/transitions.lst
        s = 'transition数：' + str(get_file_lines(transitions_path)) + '<br>'
        state_path = os.path.join(file_path, 'window_info.lst')
        s += ('state数：' + str(get_file_lines(state_path)) + '<br>')
        return jsonify({'state': 200, 'data': s})


@app.route('/file_graph', methods = ['POST'])
def send_graph_file():
        basedir = os.path.dirname(__file__)
        data = json.loads(request.get_data(as_text=True))
        file_name = data['file'] #file_name: files/usr0/file_name
        print(file_name)
        file_path = os.path.join(basedir, file_name) #file_path: ./files/usr0/file_name
        if not os.path.exists(file_path):
                return jsonify({'state': 1004, 'msg': '无法打开希望获取的文件'})
        model = Model()
        model.Build_Model_From_Project(file_path)
        graph = Graph()
        graph.generate_graph(model)
        graph.visualization()
        f = open('force_layout_graph.html', 'r')
        s = f.read()
        return jsonify({'state': 200, 'data': s})


@app.route('/file_list', methods = ['POST'])
def send_file_list():
        basedir = os.path.dirname(__file__)
        data = json.loads(request.get_data(as_text=True))
        usr_name = 'usr' + data['cookie'] #usr_name: usr0
        file_dir = os.path.join(basedir, 'files', usr_name) #file_dir: ./files/usr0
        file_list = os.listdir(file_dir) #file_list: all files in ./files/usr0
        di = db.select_data(usr_name)
        li = {}
        for file_name in file_list:
                print(file_name) #file_name: file_name or file_name.zip
                if not os.path.isdir(os.path.join(file_dir, file_name)): #ignore ./files/usr0/file_name.zip
                        continue
                time, app = di[file_name]
                file_path = 'files/' + usr_name + '/' + file_name + '/' #file_path: files/usr0/file_name/
                t_di = {'file': file_path, 'time': time}
                if not app in li:
                        li[app] = [t_di]
                else:
                        li[app].append(t_di)
        return jsonify({'state': 200, 'data': li})


def merge_models(files, resPath):
        merge = Merge()
        for f in files:
                model = Model()
                model.Build_Model_From_Project(f)
                merge.add_model(model)
        merge.merge_models()
        res = merge.get_res_model()
        print('resPath:' + resPath)
        res.Save_Model_To_Local(resPath)


@app.route('/file_merge', methods = ['POST'])
def file_merge():
        basedir = os.path.dirname(__file__)
        file_dir = os.path.join(basedir, 'temp') #file_dir: ./temp
        file_cnt = 0
        if not os.path.exists(file_dir):
                os.makedirs(file_dir)
        else:
                file_cnt = len(os.listdir(file_dir)) #file_cnt: number of files in ./temp
        data = json.loads(request.get_data(as_text=True))
        app = data['app']
        files = data['files']
        print(app, files)
        file_name = 'tempfile' + str(file_cnt) + '/' #file_name: tempfile0/
        file_path = os.path.join(file_dir, file_name) #file_path: ./temp/tempfile0/
        merge_models(files, file_path)
        return jsonify({'state': 200, 'file': 'temp/' +  file_name}) #send temp/tempfile0/


@app.route('/merge_process', methods = ['POST'])
def merge_process():
        f = open('process.txt', 'r')
        data = f.readlines()
        f.close()
        return jsonify({'state': 200, 'process': data[-1]})


@app.route('/save_result', methods = ['POST'])
def save_result():
        basedir = os.path.dirname(__file__)
        data = json.loads(request.get_data(as_text=True))
        usr_name = 'usr' + data['cookie'] #usr_name: usr0
        temp_name = data['tempname'] #temp_name: temp/tempfile0/
        file_name = data['filename'] #file_name: file_name
        app = data['app']
        file_dir = os.path.join(basedir, 'files', usr_name) #file_dir: ./files/usr0
        print(temp_name, file_name)
        file_list = os.listdir(file_dir) #file_list: all file_name in ./files/usr0
        for fname in file_list: #fname: file_name
                if file_name == fname:
                        return jsonify({'state': 1003, 'msg': '该名称的文件已经存在'})
        file_path = os.path.join(file_dir, file_name) #file_path: ./files/usr0/file_name
        shutil.copytree(temp_name, file_path)
        shutil.rmtree('temp')
        os.mkdir('temp')
        temp_time = time.asctime( time.localtime(time.time()) )
        db.upload_data(usr_name, app, temp_time, file_name)
        return jsonify({'state': 200, 'msg': '保存成功'})


@app.route('/abort_result', methods = ['POST'])
def abort_result():
        data = json.loads(request.get_data(as_text=True))
        temp_name = data['tempname'] #temp_name: temp/tempfile0/
        shutil.rmtree('temp')
        os.mkdir('temp')
        return jsonify({'state': 200, 'msg': '删除成功'})


@app.route('/file_remove', methods = ['POST'])
def remove_file():
        data = json.loads(request.get_data(as_text=True))
        file_list = data['files'] #file_list: list of files/usr0/file_name
        for file_name in file_list: #file_name: files/usr0/file_name
                print(file_name)
                file_name_list = file_name.split('/')
                db.delete_data(file_name_list[1], file_name_list[2])
                shutil.rmtree(file_name)
        return jsonify({'state': 200, 'msg': '删除成功'})


@app.route('/register', methods=['POST'])
def register():
        data = json.loads(request.get_data(as_text=True))
        username = data['user_name']
        password = data['password']
        print(username, password)
        uid = db.get_uid()
        #判断用户名是否已经存在，若数据库中不存在则返回uid，否则返回“注册失败，用户名已存在”
        if db.register_check(username):
                db.create_user(uid, username, password)
                basedir = os.path.dirname(__file__)
                usr_name = 'usr' + str(uid) #usr_name: usr0
                file_dir = os.path.join(basedir, 'files', usr_name) #file_dir: ./files/usr0
                if not os.path.exists(os.path.join(basedir, 'files')):
                        os.makedirs(os.path.join(basedir, 'files'))
                if not os.path.exists(file_dir):
                        os.makedirs(file_dir)
                return jsonify({'state': 200, 'uid': uid})
        else:
                return jsonify({'state': 1005, 'msg': '注册失败，用户名已存在'})


@app.route('/login', methods = ['POST'])
def login():
        data = json.loads(request.get_data(as_text=True))
        user_name = data['user_name']
        password = data['password']
        uid = db.get_name_uid(user_name)
        if uid:
                mail_addr = db.check_email_uid(uid)
                if db.login_check(user_name, password):
                        #print(username, password)
                        return jsonify({'state': 200, 'uid': uid, 'mail_addr': mail_addr})
                else:
                        return jsonify({'state': 1006, 'msg': '密码错误'})
        else:
                return jsonify({'state': 1007, 'msg': '用户不存在'})


@app.route('/change_password', methods = ['POST'])
def change_password():
        data = json.loads(request.get_data(as_text=True))
        uid = data['cookie']
        old_password = data['old_password']
        new_password = data['new_password']
        if db.check_password(uid, old_password):
                db.change_password(uid,new_password)
                return jsonify({'state': 200, 'msg': '密码修改成功'})
        else:
                return jsonify({'state': 1006, 'msg': '密码错误'})


@app.route('/mail_login', methods = ['POST'])
def mail_login():
        data = json.loads(request.get_data(as_text=True))
        code = data['check_code']
        if 'user_name' in data:
                user_name = data['user_name']
                uid = db.get_name_uid(user_name)
                mail_addr = db.check_email_uid(uid)
                if not mail_addr:
                        return jsonify({'state': 1100, 'msg': '用户未绑定邮箱'})
        else:
                mail_addr = data['mail_addr']
                uid = db.check_email_email(mail_addr)
                if not uid:
                        return jsonify({'state': 1101, 'msg': '邮箱对应的用户不存在'})
                user_name = db.get_user_name(uid)
        print(mail_addr, code)
        ret = send_mail(mail_addr, code)
        if ret:
                return jsonify({'state': 200, 'uid': uid, 'user_name': user_name, 'mail_addr': mail_addr})
        else:
                return jsonify({'state': 1102, 'msg': '发送邮件时出错'})


@app.route('/mail_bind', methods = ['POST'])
def mail_bind():
        data = json.loads(request.get_data(as_text=True))
        uid = data['cookie']
        mail_addr = data['mail_addr']
        index = db.check_email_email(mail_addr)
        if index:
                return jsonify({'state':1105,'msg':'邮箱已被其他用户绑定'})
        else:
                if 'check_code' in data:
                        code = data['check_code']
                        print(mail_addr, code)
                        ret = send_mail(mail_addr, code)
                        if ret:
                                return jsonify({'state': 200, 'msg': '邮件发送成功'})
                        else:
                                return jsonify({'state': 1102, 'msg': '发送邮件时出错'})
                else:
                        db.create_email(uid, mail_addr)
                        return jsonify({'state': 200, 'msg': '邮箱绑定成功'})

@app.route('/check_code', methods = ['POST'])
def check_code():
        data = json.loads(request.get_data(as_text=True))
        s = data['str']
        code = create_check_code(200, 50, s)
        return code


def send_mail(receiver, code):
        sender = '405903102@qq.com'  # 发件人邮箱账号
        password = 'xozekekxpckqbjfb'  # 发件人邮箱授权码
        try:
                socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '114.212.83.198', 1080)
                socks.wrapmodule(smtplib)
                msg = MIMEText('验证码为：' + code + '，如非本人操作，请忽略此邮件', 'plain', 'utf-8') #填写邮件内容
                msg['From'] = formataddr(["distant east coast", sender])  # 设置发件人邮箱账号
                msg['To'] = formataddr(["", receiver])  # 设置收件人邮箱账号
                msg['Subject'] = "验证码"  # 设置邮件主题
                server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 使用发件人邮箱中的SMTP服务器
                server.login(sender, password)  # 登录发件人邮箱
                server.sendmail(sender, [receiver, ], msg.as_string())  # 发送邮件
                server.quit()  # 关闭连接
        except Exception:
                return False
        return True


def create_check_code(w, h, s):
        '''
        根据给定的字符串生成一个验证码
        '''
        # 随机背景色创建图片
        bgcolor = (random.randrange(160,255), random.randrange(50,160), 255)
        img = Image.new(
                mode = "RGB",
                size = (w, h),
                color = bgcolor)
        draw = ImageDraw.Draw(img, mode = "RGB")

        # 绘制干扰线
        line_number = random.randint(3, 5)
        for i in range(line_number):
                begin = (random.randint(0, w), random.randint(0, h))
                end = (random.randint(0, w), random.randint(0, h))
                linecolor = (
                        random.randint(150, 255),
                        random.randint(150, 255),
                        random.randint(150, 255))
                draw.line([begin, end], fill=linecolor)

        # 绘制字符
        for i in range(4):
                char = s[i]
                textcolor = (
                        random.randint(0, 150),
                        random.randint(0, 150),
                        random.randint(0, 150))
                fontsize = random.randint(2 * (h // 3), h)
                font = ImageFont.truetype("Times.ttc", fontsize)
                draw.text((i * (w // 4) + random.randint(0, (w // 8)), random.randint(0, h - fontsize)), char, textcolor, font)

        # 加边缘滤镜
        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

        # 保存图片
        buf = io.BytesIO()
        img.save(buf, "png")

        return buf.getvalue()


if __name__ == '__main__':
        app.run(host='0.0.0.0', port='8001')
