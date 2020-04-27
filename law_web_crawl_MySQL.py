import requests  #数据抓取模块
from parsel import Selector  #标签解析模块
import pymysql  #数据库模块
import html  #网页解析模块
import re  #正则
import json  #jason模块

# 连接数据库及建表函数
def create():
    connect = pymysql.connect(host="127.0.0.1",             #数据库地址，一般为127.0.0.1或者localhost
                              port=3306,                    #数据库端口
                              user={databaseaccount},       #数据库账户
                              password={password},          #数据库密码
                              database={databasename},      #数据库名称
                              charset="utf8")               #数据库字符集，可略去
    cursor = connect.cursor() #创建游标对象cursor
    cursor.execute("drop table if exists law_list") #使用 execute() 方法执行 SQL，若同名表存在则删除
    sql = """ create table law_list(
                     id            int          not null auto_increment primary key comment '序号',
                     case_id       varchar(255) not null comment 'cBh 案件编码',
                     case_num      varchar(255) not null comment 'cBt 案件编号',
                     case_name     varchar(255) not null comment 'cFymc 案件标题',
                     case_date     date         not null comment 'dtUpdatetime 案件时间',
                     case_url      varchar(255) not null comment '案件网址',
                     case_text     longtext     not null comment '案件内容'
                   ) engine=InnoDB default charset=utf8""" #建表
    cursor.execute(sql) #执行语句
    connect.close() #关闭连接


# 插入数据函数
def insert(value):
    connect = pymysql.connect(host='127.0.0.1',
                              port=3306,
                              user={databaseaccount},
                              password={databaseaccount},
                              database={databasename},
                              charset='utf8') #连接数据库，同上
    cursor = connect.cursor() #创建游标对象cursor
    sql = 'insert into law_list (case_id,case_num,case_name,case_date,case_url,case_text) values(%s,%s,%s,%s,%s,%s)' #创建插入数据封装
    try:
        cursor.execute(sql, value) #插入数据函数
        connect.commit() #确保运行
        print('插入数据成功')
    except:
        connect.rollback() #数据操作回滚
        print("插入数据失败")
    connect.close()


create() #建表

# 抓取数据
for pageNum in range(1, 8):
    ses = requests.session() #抓取数据
    ses.headers.update({"Origin": "https://splcgk.court.gov.cn"}) #更新请求headers
    url_main = 'https://splcgk.court.gov.cn/gzfwww//qwallist' #url
    data = {'fbdw': '最高人民法院', 'bt': '', 'lx': 'lzdx', 'pageNum': str(pageNum)} #请求函数
    res = ses.post(url_main, data=data, timeout=(60, 60)) #post请求函数
    if res.status_code == 200: #是否正常抓取
        print('网页正常采集')
    else:
        print('网页采集失败')
    result = res.text #获取文本
    result = json.loads(result) #返回字典格式
    law_list = result['list'] #获取字典意向信息

    #遍历字段并转码
    for content in law_list:
        case_id = html.unescape(content['cBh'])
        case_num = html.unescape(content['cBt'])
        case_name = html.unescape(content['cFymc'])
        case_date = content['dtUpdatetime']
        url_case = 'https://splcgk.court.gov.cn/gzfwww//qwal/qwalDetails?id='
        case_url = url_case + case_id #拼接代码

        #提取网页内容
        res_text = requests.get(case_url) #抓取网页正文
        sel = Selector(text=res_text.text) #获取文本信息
        for x in sel.css('.fd-fix'): #正则剔除不必要信息
            text_result = x.css('span::text').getall()
            text_result = ''.join(text_result)
            case_text = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", text_result)

        value = (case_id, case_num, case_name, case_date, case_url, case_text) #函数列表
        insert(value)#插入数据
