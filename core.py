from flask import Flask, request

import json
import re
import socket
import os
import requests

from bson import ObjectId

import pymongo

from package import food2



send_host = 'http://localhost:5700'
admin_user_id = 934290827


# end_reply = '\n——本条消息由人工智障湛卢自动发送'
end_reply = ''

new_year = ['新年快乐，记得出门戴口罩，勤洗手']

user = {'1052940761':'过钦杰','1993819914':'葛美诚','951893632':'康俊杨','2417910316':'王嘉晨',
'1355487084':'杨国伟','577136233':'陈龙','310610499':'孙佳虎','1448250003':'黄鹏飞','928955899':'韩浩祺',
'593278948':'李磊','957652137':'费寒晓','626741753':'王聪','1223404803':'徐浩','1762534533':'陆佳晨',
'1379837151':'陈佳虹','1710622010':'凌红琴','1803810551':'陈远夏','2464199048':'戴发鑫','1017691216':'谷远军',
'303786244':'黎进坤','1439471037':'秦啸威','1719334503':'唐乐中','1350425981':'王超','511671610':'王小军',
'739727347':'詹志远','975600834':'张文杰','791611013':'钱宇浩','1069205637':'王琼','1486980161':'杨毅杰',
'1274855149':'杨子杰','1165244022':'葛同学','1609375541':'李书杰','1812857441':'王中勤','1512658130':'许士豪',
'441581565':'徐依杰','1789964584':'徐显','2425597623':'徐天耀'}



myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["bot"]
ans_db = mydb['answer']
history_db = mydb["history1"]

req_list = ['姓名','学号','现在是否在苏州（是/否）','现在所处位置（省市区）','联系电话']


def massage_log(raw):
    history_db.insert_one(raw) 





# #随机数生成器
# def randnum(allnum):
#     rand = random.randint(1,allnum)     #产生1-键值对所有值的和的随机数
#     return rand                         #返回产生的随机数


#消息发送
def p_send(user_id,message):
    r = requests.get(send_host + "/send_private_msg?user_id=%s&message=%s" % (user_id,message))



# 判断是否存在
def is_exis(key,value):
    mydoc = ans_db.find_one({key:value},{'_id':0})
    if mydoc:
        print('数据存在')
        return mydoc
    else:
        print('数据不存在')
        return 0

#插入原始数据
def ins_o_data (user_id):
    playload = {'user_id':user_id}
    for i in req_list:
        playload[i] = 'None'
    # print(playload)
    ans_db.insert_one(playload) 

def update_data(user_id,key,value):
    myquery = { "user_id": user_id }
    newvalues = { "$set": { key: value } }
    ans_db.update_one(myquery, newvalues)

def cln(user_id):
    ans_db.delete_one({'user_id':user_id})

def look(user_id):
    mydoc = ans_db.find_one({'user_id':user_id},{'_id':0})
    print(mydoc)
    playload = ''
    for _ in range(0,len(mydoc)):
        a,b = mydoc.popitem()
        playload += '%s:%s\n' % (a,b)
    p_send(user_id,playload)




def dcb(user_id,massage):
    keys = []
    #检查用户是否创建过记录
    if massage == 'None':
        data = is_exis('user_id',user_id)
        if data:
            p_send(user_id,'您已经完成，可回复关键字“查看”查看当前填表')
        else:
            ins_o_data(user_id)
            p_send(user_id,'现在开始填写表格，您可以回复关键字"清除"重新填写，请问您的姓名是：')
    else:
        data = is_exis('user_id',user_id)
        #检查用户填表是否为空
        print(data)
        #提取key，并转换成列表
        for i in data:
            if i == 'user_id':
                continue
            else:
                keys.append(i)
        # print(keys)
        #把答案写入数据库
        for j in range(0,len(keys)):
            if data[keys[j]] == 'None':
                #写入数据库
                update_data(user_id,keys[j],massage)
                #提出下一个问题
                try:
                    print("向%s发送问题：%s" % (user_id,keys[j+1]))
                    p_send(user_id,'请问:%s'% keys[j+1])
                except:
                    print('%s完成了所有问题')
                    p_send(user_id,'您已经填表完所有的问题了，可回复关键字"查看"查看填写')
                break





app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive():
    payload = request.json
    if payload.get('post_type') == 'message':
        user_id = payload.get('user_id')
        message = payload.get('message')
        massage_log(payload)
        
        if '填表' in message:
            dcb(user_id,'None')
        if '查看' in message:
            look(user_id)
        if '清除' in message:
            cln(user_id)
            p_send(user_id,'您的填表已被清除，若要重新填表，请发送"填表"重新开始')
        if not '填表' in message:
            dcb(user_id,message)

        return {'state':'200'}


if __name__ == "__main__":
    # a = watch_me()
    app.run(debug=True)
