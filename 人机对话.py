#!/usr/bin/env python
# encoding=utf-8
import requests
from py2neo import *
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
import pymysql
import aiml
import os
import jieba
app = Flask(__name__)
jieba.enable_paddle()
alice_path = 'C://Tools//VScode Work//Python//aiml'
os.chdir(alice_path)
alice = aiml.Kernel()
alice.learn("startup.xml")
alice.respond('LOAD ALICE')
tem1 = """<?xml version="1.0" encoding="UTF-8"?>
<aiml version="1.0">
    <category>
        <pattern>*{}*</pattern>
        <template>
            {}{}{}{}{}
        </template>
    </category>
</aiml>"""
tem2 = """<?xml version="1.0" encoding="UTF-8"?>
<aiml version="1.0">
    <category>
        <pattern>*计算：*</pattern>
        <template>
            结果是：{}
        </template>
    </category>
</aiml>"""
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    passwd='root',
    db='webjob',
    charset='utf8'
)

cursor = conn.cursor()


class AnalysisQuestion():
    def analysis(self, question):
        params = []
        if('脑卒中的概率' in question and '和' not in question):
            index = 0
            a = ['的', '概率', '是', '为', '多少', '脑', '卒中',
                 '脑卒中', '得', '症状', '这一', '一', '这', '\n']
            b = jieba.cut(question)
            for i in b:
                if i not in a:
                    params.append(i)
            params = eval(str(params).replace(',', '').replace(' ', ''))
        elif('概率为' in question):
            index = 1
            a = ['的', '症状', '有', '哪些', '%', '脑',
                 '脑卒中', '卒中', '得', '概率', '为', '\n']
            b = jieba.cut(question)
            for i in b:
                if i not in a:
                    params.append(i)
            params = eval(str(params).replace(',', '').replace(' ', ''))
        elif('哪些症状' in question and '引发' in question):
            index = 2
        elif('会引发' in question and '哪些症状' not in question):
            index = 3
            a = ['是否', '会', '引发', '脑卒中', '症状', '这一', '一', '这', '\n']
            b = jieba.cut(question)
            for i in b:
                if i not in a:
                    params.append(i)
            params = eval(str(params).replace(',', '').replace(' ', ''))
        else:
            index = 14
            params = []
        return index, params


class Get_answer():
    def __init__(self):
        self.graph = Graph("http://localhost:7474",
                           username="neo4j", password="3170611042")

    def get_data(self, index, params):
        query = ''
        if index == 0:
            query = "match(n:Ncz) where n.symptom='{}' return  n.probability;".format(
                params[0])  # 一症状查一概率
            # print(query)
        elif index == 1:
            query = "match(n:Ncz) where n.probability='{}' return  n.symptom;".format(
                params[0])  # 一概率查一症状
        elif index == 2:
            query = "match(n:Ncz) return n.symptom;"  # 多症状查多概率
            print(query)
        elif index == 3:
            query = "match(n:Ncz) where n.symptom='{}' return  n.symptom;".format(
                str(params[0]).replace(',', '').replace(' ', '').replace('[', '').replace(']', '').replace("'", ''))  # 简介

        result = self.graph.run(query)
        print(result)
        print(type(result))
        return result
# sys.setdefaultencoding('utf-8')


@app.route('/', methods=['POST', 'GET'])
def Login():
    if request.method == 'POST':
        useracc = request.form['useracc']
        userpwd = str(request.form['userpwd'])
        adminacc = request.form['adminacc']
        adminpwd = str(request.form['adminpwd'])
        if(useracc != '' and userpwd != ''):
            result = funUserLogin(useracc, userpwd)
            print(result)
            if(result == 1):
                return redirect('/user')
                return render_template('User.html')
            elif(result == 0):
                return redirect('/')
                return render_template('Login1.html')
        elif(adminacc != '' and adminpwd != ''):
            result = funAdminLogin(adminacc, adminpwd)
            print(result)
            if(result == 1):
                return redirect('/index')
                return render_template('index.html')
            elif(result == 0):
                return redirect('/')
                return render_template('Login1.html')
        else:
            return render_template('Login1.html')
    else:
        return render_template('Login1.html')


def funUserLogin(useracc, userpwd):
    sql = "SELECT useracc,userpwd FROM User WHERE useracc='{}' and userpwd='{}' ".format(
        useracc, userpwd)
    l = cursor.execute(sql)
    if(l == 1):
        res = 1
    else:
        res = 0
    return res


def funAdminLogin(adminacc, adminpwd):
    sql = "SELECT adminacc,adminpwd FROM Admin WHERE adminacc='{}' and adminpwd='{}' ".format(
        adminacc, adminpwd)
    l = cursor.execute(sql)
    if(l == 1):
        res = 1
    else:
        res = 0
    return res


@app.route('/index', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        question = request.form['question']
        result = funsearch(question)
        return render_template('index.html', result=result)
    else:
        return render_template('index.html')


@app.route('/user', methods=['POST', 'GET'])
def User():
    if request.method == 'POST':
        question = request.form['question']
        result = funsearch(question)
        return render_template('User.html', result=result)
    else:
        return render_template('User.html')


def funsearch(question):
    response = ''
    aq = AnalysisQuestion()
    ga = Get_answer()
    print(question)
    index, params = aq.analysis(question)
    x = str(params).replace(',', '').replace(' ', '').replace(
        '[', '').replace(']', '').replace("'", '')
    print(index, params)
    message = "ㅤ"+question+"ㅤ"
    if(index == 14):
        if('查询天气：' not in question and '计算：' not in question):
            response = alice.respond(message).replace(' ', '')
        elif('计算：' in question):
            count(question)
            response = alice.respond(message)
        elif('查询天气：' in question):
            weather(question)
            response = alice.respond(message).replace(' ', '\n'+"ㅤ")
    elif(index == 0):
        query = "match(n:Ncz) where n.symptom='{}' return  n.symptom;".format(x)
        non = ga.graph.run(query)
        print(non)
        non = str(non)
        print(non)
        if(x in non):
            answers = ga.get_data(index, params)
            for ans in answers:
                response = '该症状得脑卒中得概率为：'+str(ans[0])
        else:
            response = '暂无该症状'
    elif(index == 1):
        z = []
        query = "match(n:Ncz) where n.probability='{}' return  n.probability;".format(
            x)
        non = ga.graph.run(query)
        print(non)
        non = str(non)
        print(non)
        if(x in non):
            answers = ga.get_data(index, params)
            print(answers)
            for ans in answers:
                print(ans)
                z.append(str(ans[0]))
            response = '该概率对应的症状有：'+str(z).replace(',', '、').replace(
                ' ', '').replace('[', '').replace(']', '').replace("'", '')
        else:
            response = '暂无该概率'
    elif(index == 2):
        z = []
        answers = ga.get_data(index, params)
        print(answers)
        for ans in answers:
            print(ans)
            z.append(str(ans[0]))
        x = str(z).replace(',', '、').replace(' ', '').replace(
            '[', '').replace(']', '').replace("'", '')
        if(x != ''):
            response = '能引发脑卒中的症状有：'+x
        else:
            response = '暂无数据'
    elif(index == 3):
        answers = ga.get_data(index, params)
        print(answers)
        non = str(answers)
        params = str(params).replace(',', '').replace(
            ' ', '').replace('[', '').replace(']', '').replace("'", '')
        if(params in non):
            response = params+'会引发脑卒中'
        else:
            response = params+'不会引发脑卒中'
    res = response

    return res


def weather(Msg):
    y = Msg.replace('查询天气：', '')
    x = 'http://www.tianqiapi.com/api?version=v6&appid=22723956&appsecret=JXcAa1fQ&city='
    r1 = requests.get(x+y)
    r1.encoding = 'utf-8'
    a1 = '查询城市：'+r1.json()['city']+'\t'
    b1 = r1.json()['wea']
    print(b1)
    if(b1 == None):
        b1 = '没有信息'
    print(b1)
    c1 = r1.json()['tem2']
    if(c1 == None):
        c1 = '没有信息'
    d1 = r1.json()['tem1']
    if(d1 == None):
        d1 = '没有信息'
    e1 = r1.json()['win']
    if(e1 == None):
        e1 = '没有信息'

    b1 = '天气：'+b1+'\t'
    c1 = '最低温：'+c1+'°C'+'\t'
    d1 = '最高温：'+d1+'°C'+'\t'
    e1 = '风向：'+e1
    file1 = open("weather.aiml", "w", encoding='utf-8')
    file1.write(tem1.format(Msg, a1, b1, c1, d1, e1))
    file1.close()
    alice.learn("weather.aiml")


def count(Msg):
    y = Msg.replace('计算：', '')
    x = eval(y)
    file2 = open("count.aiml", "w", encoding='utf-8')
    file2.write(tem2.format(x))
    file2.close()
    alice.learn("count.aiml")


@app.route('/Add', methods=['POST', 'GET'])
def Add():
    if request.method == 'POST':
        symptom = request.form['symptom']
        probability = str(request.form['probability'])
        result = funAdd(symptom, probability)
        return render_template('Add.html', result=result)
    else:
        return render_template('Add.html')


def funAdd(symptom, probability):
    ga = Get_answer()
    a = 0
    i = str(a)
    print(symptom, probability)
    query = "match(n:Ncz) where n.symptom='{}' return  n.symptom;".format(
        symptom)
    non = ga.graph.run(query)
    print(non)
    non = str(non)
    print(non)
    if(symptom not in non):
        query = "CREATE (n:Ncz {} id:{},symptom:'{}',probability:'{}%'{})"
        query = query.format('{', i, symptom, probability, '}')
        ga.graph.run(query)
        res = '添加成功'
        return res
    else:
        res = '已有该症状'
        return res


@app.route('/Delete', methods=['POST', 'GET'])
def Delete():
    if request.method == 'POST':
        symptom = request.form['symptom']
        probability = str(request.form['probability'])
        result = funDelete(symptom)
        return render_template('Delete.html', result=result)
    else:
        return render_template('Delete.html')


def funDelete(symptom):
    ga = Get_answer()
    print(symptom)
    query = "match(n:Ncz) where n.symptom='{}' return  n.symptom;".format(
        symptom)
    non = ga.graph.run(query)
    print(non)
    non = str(non)
    print(non)
    if(symptom in non):
        query = "match (n:Ncz{} symptom:'{}' {}) delete n"
        query = query.format('{', symptom, '}')
        ga.graph.run(query)
        res = '删除成功'
        return res
    else:
        res = '不存在该症状'
        return res


@app.route('/Update', methods=['POST', 'GET'])
def Update():
    if request.method == 'POST':
        symptom = request.form['symptom']
        probability = str(request.form['probability'])
        result = funUpdate(symptom, probability)
        return render_template('Update.html', result=result)
    else:
        return render_template('Update.html')


def funUpdate(symptom, probability):
    ga = Get_answer()
    a = 0
    i = str(a)
    print(symptom)
    query = "match(n:Ncz) where n.symptom='{}' return  n.symptom;".format(
        symptom)
    non = ga.graph.run(query)
    print(non)
    non = str(non)
    print(non)
    if(symptom in non):
        query = "match (n:Ncz{} symptom:'{}' {}) delete n"
        query = query.format('{', symptom, '}')
        ga.graph.run(query)
        query = "CREATE (n:Ncz {} id:{},symptom:'{}',probability:'{}%'{})"
        query = query.format('{', i, symptom, probability, '}')
        ga.graph.run(query)
        res = '修改成功'
        return res
    else:
        res = '不存在该症状'
        return res


if __name__ == '__main__':
    app.run(host='0.0.0.0',  # 任何ip都可以访问
            port=5000,  # 端口
            debug=True
            )
