import requests  #数据抓取模块
from parsel import Selector  #标签解析模块
import html  #网页解析模块
import re  #正则
import json  #jason模块
import time #时间模块

lines = [] #集合

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

    #存储数据
    for content in law_list:
        case_id = html.unescape(content['cBh'])
        case_num = html.unescape(content['cBt'])
        case_name = html.unescape(content['cFymc'])
        case_date = content['dtUpdatetime']
        url_case = 'https://splcgk.court.gov.cn/gzfwww//qwal/qwalDetails?id='
        case_url = url_case + case_id

        res_text = requests.get(case_url)
        sel = Selector(text=res_text.text)
        for x in sel.css('.fd-fix'):
            text_result = x.css('span::text').getall()
            text_result = ''.join(text_result)
            case_text = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", text_result)
            case_url = url_case + case_id #拼接代码

            #提取网页内容
            res_text = requests.get(case_url) #抓取网页正文
            sel = Selector(text=res_text.text) #获取文本信息
            for x in sel.css('.fd-fix'): #正则剔除不必要信息
                text_result = x.css('span::text').getall()
                text_result = ''.join(text_result)
                case_text = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", text_result)          
                
        lines.append('%s,%s,%s,%s,%s,%s' % (case_id, case_num, case_name, case_date, case_url, case_text)) #集合数据封装
print("lines", lines) #打印集合数据
    
#保存数据
with open('law_list.csv', 'w') as f:
    for line in lines:
        f.write(line)
        f.write('\n')
