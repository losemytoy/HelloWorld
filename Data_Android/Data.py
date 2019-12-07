import requests
from lxml import etree
import time
import re
import csv
import pymssql


# 定义函数抓取每页前30条商品信息
def crow_first(keyword,n):
    # 构造每一页的url变化
    url = 'https://search.jd.com/Search?keyword='+str(keyword)+'&enc=utf-8&page=%d'+str(2 * n - 1)
    # url = 'https://search.jd.com/Search?keyword='+str(keyword)+'&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&cid2=653&cid3=655&page=%d'+str(2 * n - 1)
    head = {'authority': 'search.jd.com',
            'method': 'GET',
            # 'path': '/s_new.php?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&cid2=653&cid3=655&page=4&s=84&scrolling=y&log_id=1529828108.22071&tpl=3_M&show_items=7651927,7367120,7056868,7419252,6001239,5934182,4554969,3893501,7421462,6577495,26480543553,7345757,4483120,6176077,6932795,7336429,5963066,5283387,25722468892,7425622,4768461',
            'scheme': 'https',
            # 'referer': 'https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&cid2=653&cid3=655&page=3&s=58&click=0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'Cookie': 'qrsc=3; pinId=RAGa4xMoVrs; xtest=1210.cf6b6759; ipLocation=%u5E7F%u4E1C; _jrda=5; TrackID=1aUdbc9HHS2MdEzabuYEyED1iDJaLWwBAfGBfyIHJZCLWKfWaB_KHKIMX9Vj9_2wUakxuSLAO9AFtB2U0SsAD-mXIh5rIfuDiSHSNhZcsJvg; shshshfpa=17943c91-d534-104f-a035-6e1719740bb6-1525571955; shshshfpb=2f200f7c5265e4af999b95b20d90e6618559f7251020a80ea1aee61500; cn=0; 3AB9D23F7A4B3C9B=QFOFIDQSIC7TZDQ7U4RPNYNFQN7S26SFCQQGTC3YU5UZQJZUBNPEXMX7O3R7SIRBTTJ72AXC4S3IJ46ESBLTNHD37U; ipLoc-djd=19-1607-3638-3638.608841570; __jdu=930036140; user-key=31a7628c-a9b2-44b0-8147-f10a9e597d6f; areaId=19; __jdv=122270672|direct|-|none|-|1529893590075; PCSYCityID=25; mt_xid=V2_52007VwsQU1xaVVoaSClUA2YLEAdbWk5YSk9MQAA0BBZOVQ0ADwNLGlUAZwQXVQpaAlkvShhcDHsCFU5eXENaGkIZWg5nAyJQbVhiWR9BGlUNZwoWYl1dVF0%3D; __jdc=122270672; shshshfp=72ec41b59960ea9a26956307465948f6; rkv=V0700; __jda=122270672.930036140.-.1529979524.1529984840.85; __jdb=122270672.1.930036140|85.1529984840; shshshsID=f797fbad20f4e576e9c30d1c381ecbb1_1_1529984840145'
            }


    r = requests.get(url, headers=head)
    r.encoding = 'utf-8'
    i = 0
    html1 = etree.HTML(r.text)
    # 定位到每一个商品标签li
    datas = html1.xpath('//li[contains(@class,"gl-item")]')
    # 将抓取的结果保存到本地CSV文件中
    with open('JD_DATA.csv', 'a', newline='', encoding='utf-8')as f:
        write = csv.writer(f)
        write.writerow(['商品名','价格','图片'])
        p_pic=[]
        for data in datas:
            i=i+1
            detail_url = ''.join(data.xpath('.//div[@class="gl-i-wrap"]/div[1]/a/@href'))
            # 以https:开头的url无用，去掉
            if not detail_url.startswith("http"):
                detail_url = "https:" + detail_url
                ret = requests.get(detail_url).text
                # print(">>>", type(ret))
            # try:
                # 捕获异常，当正则表达式没有获取到对象时，为了让程序正常运行
                res = re.findall(r"imageList\:(.*?jpg\"\])", ret)[0]
                # 字符串嵌套列表 处理成列表，再遍历
                imageList = res.replace('[', '').replace(']', '').replace('"', '').split(',')
                r=0
                for image in imageList:
                    if(r==0):
                        # 图片的url的最后部分作为文件名
                        image_title = image.split('/')[-1]  # 取列表最后一项
                        if image.startswith(" "):
                            #拼接的时候去掉字符串开始的空格
                            image = image.lstrip()
                        # 拼接成完整img_url
                        fullImageUrl = "https://img11.360buyimg.com/n1/" + image
                        # print(fullImageUrl)
                        # print(image_title)
                        p_pic= fullImageUrl
                        r=r+1
                    else:
                        continue
                # print(p_pic)
            # except:
            #     ''' 出现异常则打印，不阻止程序奔溃 '''
            #     print('图片加载异常！')
            p_price = data.xpath('div/div[@class="p-price"]/strong/i/text()')
            p_comment = data.xpath('div/div[5]/strong/a/text()')
            p_name = data.xpath('div/div[@class="p-name p-name-type-2"]/a/em')
            # 这个if判断用来处理那些价格可以动态切换的商品，比如上文提到的小米MIX2，他们的价格位置在属性中放了一个最低价
            if len(p_price) == 0:
                p_price = data.xpath('div/div[@class="p-price"]/strong/@data-price')
                # xpath('string(.)')用来解析混夹在几个标签中的文本
            write.writerow([p_name[0].xpath('string(.)'), p_price[0],p_pic])
    f.close()


# 定义函数抓取每页后30条商品信息
def crow_last(keyword,n):
    # 获取当前的Unix时间戳，并且保留小数点后5位
    a = time.time()
    b = '%.5f' % a
    url = 'https://search.jd.com/Search?keyword=' + str(keyword) + '&enc=utf-8&page=%d' +str(2 * n) + '&s=' + str(48 * n - 20) + '&scrolling=y&log_id=' + str(b)
    # url = 'https://search.jd.com/s_new.php?keyword='+str(keyword)+'&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&cid2=653&cid3=655&page=%d' +str(2 * n) + '&s=' + str(48 * n - 20) + '&scrolling=y&log_id=' + str(b)
    head = {'authority': 'search.jd.com',
            'method': 'GET',
            'path': '/s_new.php?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA',
            'scheme': 'https',
            # 'referer': 'https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&cid2=653&cid3=655&page=3&s=58&click=0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'Cookie': 'qrsc=3; pinId=RAGa4xMoVrs; xtest=1210.cf6b6759; ipLocation=%u5E7F%u4E1C; _jrda=5; TrackID=1aUdbc9HHS2MdEzabuYEyED1iDJaLWwBAfGBfyIHJZCLWKfWaB_KHKIMX9Vj9_2wUakxuSLAO9AFtB2U0SsAD-mXIh5rIfuDiSHSNhZcsJvg; shshshfpa=17943c91-d534-104f-a035-6e1719740bb6-1525571955; shshshfpb=2f200f7c5265e4af999b95b20d90e6618559f7251020a80ea1aee61500; cn=0; 3AB9D23F7A4B3C9B=QFOFIDQSIC7TZDQ7U4RPNYNFQN7S26SFCQQGTC3YU5UZQJZUBNPEXMX7O3R7SIRBTTJ72AXC4S3IJ46ESBLTNHD37U; ipLoc-djd=19-1607-3638-3638.608841570; __jdu=930036140; user-key=31a7628c-a9b2-44b0-8147-f10a9e597d6f; areaId=19; __jdv=122270672|direct|-|none|-|1529893590075; PCSYCityID=25; mt_xid=V2_52007VwsQU1xaVVoaSClUA2YLEAdbWk5YSk9MQAA0BBZOVQ0ADwNLGlUAZwQXVQpaAlkvShhcDHsCFU5eXENaGkIZWg5nAyJQbVhiWR9BGlUNZwoWYl1dVF0%3D; __jdc=122270672; shshshfp=72ec41b59960ea9a26956307465948f6; rkv=V0700; __jda=122270672.930036140.-.1529979524.1529984840.85; __jdb=122270672.1.930036140|85.1529984840; shshshsID=f797fbad20f4e576e9c30d1c381ecbb1_1_1529984840145'

            }
    r = requests.get(url, headers=head)
    r.encoding = 'utf-8'
    html1 = etree.HTML(r.text)
    datas = html1.xpath('//li[contains(@class,"gl-item")]')
    with open('JD_DATA.csv', 'a', newline='', encoding='utf-8')as f:
        write = csv.writer(f)
        write.writerow(['商品名', '价格', '图片'])
        p_pic = []
        for data in datas:
            detail_url = ''.join(data.xpath('.//div[@class="gl-i-wrap"]/div[1]/a/@href'))
            # 以https:开头的url无用，去掉
            if not detail_url.startswith("http"):
                detail_url = "https:" + detail_url
                ret = requests.get(detail_url).text
                # print(">>>", type(ret))
                # try:
                # 捕获异常，当正则表达式没有获取到对象时，为了让程序正常运行
                res = re.findall(r"imageList\:(.*?jpg\"\])", ret)[0]
                # 字符串嵌套列表 处理成列表，再遍历
                imageList = res.replace('[', '').replace(']', '').replace('"', '').split(',')
                r = 0
                for image in imageList:
                    if (r == 0):
                        # 图片的url的最后部分作为文件名
                        image_title = image.split('/')[-1]  # 取列表最后一项
                        if image.startswith(" "):
                            # 拼接的时候去掉字符串开始的空格
                            image = image.lstrip()
                        # 拼接成完整img_url
                        fullImageUrl = "https://img11.360buyimg.com/n1/" + image
                        # print(fullImageUrl)
                        # print(image_title)
                        p_pic = fullImageUrl
                        r = r + 1
                    else:
                        continue
            p_price = data.xpath('div/div[@class="p-price"]/strong/i/text()')
            p_comment = data.xpath('div/div[5]/strong/a/text()')
            p_name = data.xpath('div/div[@class="p-name p-name-type-2"]/a/em')
            if len(p_price) == 0:
                p_price = data.xpath('div/div[@class="p-price"]/strong/@data-price')
            write.writerow([p_name[0].xpath('string(.)'), p_price[0],p_pic])
    f.close()

def Save_Database():
    # -*- coding:utf-8 -*-

    # 数据库连接
    conn = pymssql.connect(host='127.0.0.1', user='sa', password='123456', database='JD_Data')

    # 打开游标
    cur = conn.cursor();

    if not cur:
        raise Exception('数据库连接失败！')

    # 4.修改数据

    reader = csv.reader(open(r'JD_DATA.csv', 'r',encoding='utf-8'))
    for item in reader:
        script = "insert into Product(ProName,Price,Img_url) values ('{0}','{1}','{2}')".format(item[0], item[1],item[2])
        cur.execute(script)

    conn.commit()  # 修改数据後提交事务
    conn.close()


if __name__ == '__main__':


    print('请输入产品：')
    x = input()
    for i in range(1, 2):#爬取页数范围
        # 下面的print函数主要是为了方便查看当前抓到第几页了
        print('***************************************************')
        try:
            print('   First_Page:   ' + str(i))
            crow_first(x,i)
            print('   Finish')
        except Exception as e:
            print(e)
        print('------------------')
        try:
            print('   Last_Page:   ' + str(i))
            crow_last(x,i)
            print('   Finish')
        except Exception as e:
            print(e)
        time.sleep(2)
    Save_Database();