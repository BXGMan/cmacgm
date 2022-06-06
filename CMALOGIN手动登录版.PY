import time
import re
import httpx
import os
import codecs
path = os.getcwd()
now = (time.strftime("%Y-%m-%d %H.%M.%S", time.localtime()))
os.makedirs(path+'\\BILL\\'+now+'\\1正本')
os.makedirs(path+'\\BILL\\'+now+'\\2副本')   # 创建文件夹用于之后自动上传提单编号

cookies = open("cookies.txt","r",encoding='gb18030')
cookies = cookies.read()   # 读取cookies
print(cookies)
cookies2 = re.findall(".AspNet.Cookies=(.*?);",cookies)[0]
cookies3 = re.findall("datadome=(.*?);",cookies)[0]
print(cookies2)
print(cookies3)  # 获取2个关键cookies

cookies = {}
cookies['.AspNet.Cookies'] = cookies2
cookies['datadome'] = cookies3

proxies = {'all://': 'http://127.0.0.1:8080'}  # 用于debug
client = httpx.Client(http2=True, verify=False)
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding':'gzip, deflate',
    'Referer':'https://www.cma-cgm.com/ebusiness/document/original',
    'Upgrade-Insecure-Requests':'1',
    'Sec-Fetch-Dest':'document',
    'Sec-Fetch-Mode':'navigate',
    'Sec-Fetch-Site':'same-origin',
    'Sec-Fetch-User':'?1',
    'Cache-Control':'max-age=0',
    'Te':'trailers',
    'Connection':'close'
}
url = 'https://www.cma-cgm.com/ebusiness/document?blType=Negotiable&blStatus=ToBePrinted&category=BL&documentBLType=Original' 
billlist = client.get(url=url,headers=headers,cookies=cookies,timeout=200)  # 获取未打印的提单列表
ff = open(path+"\\billlist.txt",'w',encoding='utf-8')
billlist = billlist.text #.replace('\ufeff','').replace('\xe7','')
ff.write(billlist)
ff.close()  # 临时储存数据
with codecs.open(path+"\\billlist.txt",'r',encoding='utf-8') as ff:
    billlist = (ff.read().replace('utf-8','').encode('gbk','ignore').decode('gbk'))
f2 = open(path+"\\zhuanhuan.txt",'w')
f2.write(billlist)
f2.close
f3 = open(path+"\\zhuanhuan.txt",'r')
ll = f3.read().replace('\\','')
f3.close()  # 转换数据 让程序可读取 ps.以前只会用笨办法 现在不想去改
billnumber = re.findall(r'(CN[0-9A-Z]{8,9}).*?"Id":"[0-9]{9}',ll)
billnumber2 = re.findall(r'CN[0-9A-Z]{8,9}.*?"Id":"([0-9]{9})',ll)  

# 以下代码就是下载提单
for n1,n2 in zip(billnumber,billnumber2):
    url = 'https://www.cma-cgm.com/ebusiness/document/print/'+n1+'/Original/False/'+n2
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding':'gzip, deflate',
        'Referer':'https://www.cma-cgm.com/ebusiness/document?blStatus=CopyAvailable&category=BL',
        'Upgrade-Insecure-Requests':'1',
        'Sec-Fetch-Dest':'document',
        'Sec-Fetch-Mode':'navigate',
        'Sec-Fetch-Site':'same-origin',
        'Sec-Fetch-User':'?1',
        'Te':'trailers',
        'Connection':'close'
    }
    print('延迟3秒')
    time.sleep(3)
    print('下载提单%s'%(n1))
    download = client.get(url=url,headers=headers,cookies=cookies,timeout=200)
    
    f = open(path+'\\BILL\\'+now+'\\1正本\\'+n1+'.pdf','wb')
    f.write(download.content)
    f.close()
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding':'gzip, deflate',
        'Referer':'https://auth.cma-cgm.com/',
        'Upgrade-Insecure-Requests':'1',
        'Sec-Fetch-Dest':'document',
        'Sec-Fetch-Mode':'navigate',
        'Sec-Fetch-Site':'same-site',
        'Te':'trailers',
        'Connection':'close'
    }
    print('下载副本中')
    urlcopyfind = 'https://www.cma-cgm.com/ebusiness/bl/detail/'+ n1
    copyfind = client.get(url=urlcopyfind,cookies=cookies,headers=headers,timeout=200)
    ff = open(path+"\\billlist.txt",'w',encoding='utf-8')
    billlist = copyfind.text#.replace('\ufeff','').replace('\xe7','')
    ff.write(billlist)
    ff.close()
    with codecs.open(path+"\\billlist.txt",'r',encoding='utf-8') as ff:
        billlist = (ff.read().replace('utf-8','').encode('gbk','ignore').decode('gbk'))
    f2 = open(path+"\\zhuanhuan.txt",'w')
    f2.write(billlist)
    f2.close
    f3 = open(path+"\\zhuanhuan.txt",'r')
    ll = f3.read().replace('\\','')
    f3.close()
    try:
        billnumber3 = re.findall(r'/Copy/False/([0-9]{9})',ll)[0]
    except:
        print(n1+'提单没有副本'+'为了正常运行提单登记脚本请手动创建X页名为'+n1+'.pdf的空白副本')
        n1 = n1+'没有副本'
        continue
    print('获取副本号码成功'+billnumber3)
    time.sleep(1)
    urlcopy = 'https://www.cma-cgm.com/ebusiness/document/print/'+n1+'/Copy/False/'+billnumber3

    downloadcopy = client.get(url=urlcopy,cookies=cookies,headers=headers,timeout=200)
    f2 = open(path+'\\BILL\\'+now+'\\2副本\\'+n1+'.pdf','wb')
    f3 = open(path+'\\BILL\\'+now+'\\NO.txt','a')
    f3.write(n1+'	'+now+'\n')
    f3.close()
    f2.write(downloadcopy.content)
    f2.close()
print('运行完成5分钟后自动关闭')
time.sleep(300)

