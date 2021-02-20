import os
import re
import sys
import time
import aiml
import requests
from tkinter import *
from bs4 import BeautifulSoup
from selenium import webdriver
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

def main():

    def sendMsg():  # 发送消息
        strMsg1 = '我:' + \
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n'
        strMsg2 = '机器人:' + \
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n'
        txtMsgList.insert(END, strMsg1, 'greencolor')
        msg = txtMsg.get('0.0', END)
        Msg = msg.replace('\n', '').replace('\r', '')
        message = "ㅤ"+msg+"ㅤ"
        txtMsgList.insert(END, "ㅤ"+msg, 'greencolor')
        if(re.match('查询天气：', Msg) == None and re.match('计算：', Msg) == None):
            response = alice.respond(message).replace(' ', '')
        elif(re.match('计算：', Msg) != None):
            count(Msg)
            response = alice.respond(message)
        else:
            weather(Msg)
            response = alice.respond(message).replace(' ', '\n'+"ㅤ")
        txtMsgList.insert(END, strMsg2, 'redcolor')
        txtMsgList.insert(END, "ㅤ"+response+'\n', 'redcolor')
        
        if(re.match('查询：', Msg) != None):
            search(Msg)
        
        txtMsg.delete('0.0', END)  # 删除中间刚输入的内容
    
    def weather(Msg):
        y = Msg.replace('查询天气：', '')
        x = 'http://www.tianqiapi.com/api?version=v6&appid=22723956&appsecret=JXcAa1fQ&city='
        r1 = requests.get(x+y)
        r1.encoding = 'utf-8'
        a1 = '查询城市：'+r1.json()['city']+'\t'
        b1 = '天气：'+r1.json()['wea']+'\t'
        c1 = '最低温：'+r1.json()['tem2']+'°C'+'\t'
        d1 = '最高温：'+r1.json()['tem1']+'°C'+'\t'
        e1 = '风向：'+r1.json()['win']
        file1 = open("weather.aiml", "w")
        file1.write(tem1.format(Msg, a1, b1, c1, d1, e1))
        file1.close()
        alice.learn("weather.aiml")
        
    def search(Msg):
        y = Msg.replace('查询：', '')
        chromedriver = "C:\Program Files\Google\Chrome//Application\chromedriver.exe"  # 这里是你的驱动的绝对地址
        driver = webdriver.Chrome(chromedriver)
        url = "http://www.baidu.com"
        driver.get(url)
        driver.find_element_by_id("kw").send_keys(y)
        driver.find_element_by_xpath('//*[@id="su"]').click()
        driver.set_window_size(960,1080)
        time.sleep(2)
        #关闭浏览器
        # driver.quit()
        # #关闭窗口
        # driver.close()
    
    def count(Msg):
        y = Msg.replace('计算：', '')
        x=eval(y)
        file2 = open("count.aiml", "w")
        file2.write(tem2.format(x))
        file2.close()
        alice.learn("count.aiml")

    def cancelMsg():  # 取消消息
        txtMsg.delete('0.0', END)

    def sendMsgEvent(event):  # 发送消息事件:
        if event.keysym == "Return":
            sendMsg()
            return 'break'

    # 创建窗口
    t = Tk()
    t.title('与对话机器人聊天中')
    # 创建frame容器
    frmLT = Frame(width=500, height=320, bg='white')
    frmLC = Frame(width=500, height=150, bg='white')
    frmLB = Frame(width=500, height=30)
    txtMsgList = Text(frmLT, width=40)
    # 创建控件
    txtMsgList = Text(frmLT)
    txtMsgList.tag_config('greencolor', foreground='#00cc6a')  # 创建tag
    txtMsgList.tag_config('bulecolor', foreground='#0078d7')
    txtMsgList.tag_config('redcolor', foreground='#e81123')
    txtMsgList.tag_config('yellowcolor', foreground='#ffb900')
    txtMsg = Text(frmLC)
    txtMsg.bind("<KeyPress-Return>", sendMsgEvent)
    # 发送取消按钮和图片
    btnSend = Button(frmLB, text='发送', width=35, command=sendMsg)
    btnCancel = Button(frmLB, text='取消', width=35, command=cancelMsg)
    # 窗口布局columnspan选项可以指定控件跨越多列显示，
    # 而rowspan选项同样可以指定控件跨越多行显示。
    frmLT.grid(row=0, column=0, columnspan=2, padx=1, pady=3, ipady=28)
    frmLC.grid(row=1, column=0, columnspan=2, padx=1, pady=3)
    frmLB.grid(row=2, column=0, columnspan=2)
    # 固定大小
    frmLT.grid_propagate(0)
    frmLC.grid_propagate(0)
    frmLB.grid_propagate(0)
    # 按钮和图片
    btnSend.grid(row=2, column=0)
    btnCancel.grid(row=2, column=1)
    txtMsgList.grid()
    txtMsg.grid()
    # 主事件循环
    t.mainloop()


if __name__ == '__main__':
    main()
