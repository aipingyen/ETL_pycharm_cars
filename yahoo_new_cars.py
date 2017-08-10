import requests
from bs4 import BeautifulSoup
import json
import sqlite3
from random import randint
# import redis
import sys

referers = ['tw.yahoo.com', 'www.google.com', 'http://www.msn.com/zh-tw/', 'http://www.pchome.com.tw/']
user_agents = [
    'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (Linux; Android 6.0.1; E6653 Build/32.2.A.0.253) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0; HTC One M9 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0.1; SM-G920V Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.36',
    'AppleTV5,3/9.1.1',
    'Mozilla/5.0 (CrKey armv7l 1.5.16041) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.0 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 5.1.1; SM-G928X Build/LMY47X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 Mobile Safari/537.36']

word_dict = {'前輪懸吊': 'front_suspen', '動力型式': 'gasoline', '壓縮比': 'compression', '市區油耗': 'fuel_city',
             '平均油耗': 'fuel_consum',
             '座位數': 'passengers', '引擎型式': 'engine', '後座傾倒行李箱容量': 'trunk_fullcapacity', '後輪懸吊': 'back_suspen',
             '排氣量': 'cc',
             '最大扭力': 'max_torque', '最大馬力': 'max_hp', '標準行李箱容量': 'trunk_capacity', '油箱容量': 'tank_capacity',
             '煞車型式': 'brake',
             '燃料費': 'fuel_expense', '牌照稅': 'license_tax', '變速系統': 'transmission', '車寬': 'width', '車身型式': 'kind',
             '車重': 'weight',
             '車長': 'length', '車門數': 'doors', '車高': 'height', '軸距': 'wheelbase', '輪胎尺碼': 'tire', '驅動型式': 'wd',
             '高速油耗': 'fuel_freeway', '系統總合輸出': 'max_hp', '馬達出力': 'skip'}


def dict_init(car_dict):
    for v in word_dict.values():
        car_dict[v] = None
    return car_dict

def gen_headers():
    headers = {'User-Agent': user_agents[randint(0, len(user_agents) - 1)],
               'Referer': referers[randint(0, len(referers) - 1)]}
    return headers


def get_content(url):
    headers = gen_headers()
    res = requests.get(url, headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'lxml')
    groups = soup.select('.group')


    equip_all = []
    for group in groups:


        # equip
        if "配備" in group.select_one('span.Fw-b').text:
            tds = group.select('td.Py-10.Whs-nw')
            equip_temp = [td.text for td in tds]
            equip_all += equip_temp



    equip = '|'.join(equip_all)
    return equip





if __name__ == '__main__':
    with sqlite3.connect('/home/ubuntu/SQLiteDB/yahoo_new_car0630.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute("select url from yahooNewCars_clean2 where equip='';")
        urls=[]
        for row in cursor:

            urls.append(row[0])
        for idx, line in enumerate(urls):
            try:
                if idx > 0:
                    url = line
                    print(url)
                    equip = get_content(url)


                    cursor.execute('''UPDATE yahooNewCars_clean2 SET equip=? where url=?;''',
                                   (equip,url))
                    print(idx)
                    if idx % 5 == 0:
                        conn.commit()
            except Exception as e:
                print(e)
                conn.rollback()
        conn.commit()
