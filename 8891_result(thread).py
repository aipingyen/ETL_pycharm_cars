import requests
from bs4 import BeautifulSoup
import re
import threading
import time
import json
import pprint
from random import randint

import sqlite3

def gen_headers():
    referers = ['tw.yahoo.com', 'www.google.com', 'http://www.msn.com/zh-tw/', 'http://www.pchome.com.tw/']
    user_agents = ['Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
              'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)']
    headers = {'user-agent': user_agents[randint(0, len(user_agents) - 1)],
               'referer': referers[randint(0, len(referers) - 1)]}
    return headers

# def vectorize(input_list):
#     standard  = ['安全氣囊','倒車顯影系統','倒車雷達','keyless免鑰系統','LED頭燈','電動天窗','衛星導航','循跡系統','動態穩定系統','定速系統','ABS防鎖死','真皮/皮革座椅','自動停車系統','胎壓偵測','多功能方向盤']
#     output_list = []
#     for each in standard:
#         if each in input_list:
#             output_list.append('1')
#         else:
#             output_list.append('0')
#     return output_list

def get_car_infos(fileIn, fileOut, failUrl, conn, cursor, line):
    headers=gen_headers()
    with open(fileIn, 'r') as f:
        data = f.readlines()
#每行內容："url|posttime|{已經有12欄資料的Dictionary}"
    for line in data:
        carDic = {}
        infos = line.split('\n')[0].split('|')
        url = infos[0] #得到url
        carDic = json.loads(infos[2]) #得到已經有12欄資料的dictionary

        count = 0
        while count < 3:
            soup = ''
            try:
                res = requests.get(url, headers=headers)
                soup = BeautifulSoup(res.text, 'lxml')
                carDic['color'] = soup.select('.right-info .car-info ul li span')[7].text.strip('色')
                carDic['doors'] = soup.select('.car-detail-equipment .car-detail-base span')[1].text.split("：")[1]
                carDic['gasoline'] = soup.select('.car-detail-equipment .car-detail-base span')[2].text.split("：")[
                    1].strip('車')
                carDic['wd'] = soup.select('.car-detail-equipment .car-detail-base span')[4].text.split("：")[1]
                if soup.select('div.tip > a'):
                    carDic['certificate'] = '其他'
                else:
                    carDic['certificate'] = 'na'
                equip = ''
                for item in soup.select('.car-equipment-show .info'):
                    equip += '{}|'.format(item.text)
                carDic['equip'] = equip.strip('|')

                with open(fileOut, 'a') as f:
                    f.write('{}\n'.format(json.dumps(carDic, ensure_ascii=False)))

                cursor.execute('INSERT INTO cars0616 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                               (carDic['source'], carDic['url'], carDic['title'], carDic['brand'], carDic['model'],
                                carDic['doors'],
                                carDic['color'], carDic['gasoline'], carDic['cc'], carDic['transmission'],
                                carDic['equip'],
                                carDic['mileage'], carDic['years'], carDic['location'], carDic['posttime'],
                                carDic['price'], carDic['certificate'], carDic['wd']))
                conn.commit()
                break
            #IndexError:  8891有的url會被轉址到商店(用以下code解析)
            except IndexError as e:
                try:
                    carDic['color'] = soup.select('.mb-info span')[3].text.strip('色')
                    carDic['gasoline'] = soup.select('.auto_standard span')[1].text.strip('車')
                    carDic['wd'] = soup.select('.auto_standard span')[2].text
                    carDic['doors'] = soup.select('.auto_standard span')[4].text
                    certi_list = ['sum', 'save', 'hot']
                    if soup.select_one('.auto-check-t'):
                        text = soup.select_one('.auto-check-t').text.lower()
                        keyword = re.search(r'[a-z]+', text).group()
                        if keyword in certi_list:
                            carDic['certificate'] = keyword
                        else:
                            carDic['certificate'] = '其他'
                    else:
                        carDic['certificate'] = 'na'
                    equip = ''
                    for item in soup.select('.additionConfig'):
                        equip += '{}|'.format(item.text)
                    carDic['equip'] = equip.strip('|')

                    with open(fileOut, 'a') as f:
                        f.write('{}\n'.format(json.dumps(carDic, ensure_ascii=False)))

                    cursor.execute('INSERT INTO cars0616 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                   (carDic['source'], carDic['url'], carDic['title'], carDic['brand'], carDic['model'],
                                    carDic['doors'],
                                    carDic['color'], carDic['gasoline'], carDic['cc'], carDic['transmission'],
                                    carDic['equip'],
                                    carDic['mileage'], carDic['years'], carDic['location'], carDic['posttime'],
                                    carDic['price'], carDic['certificate'], carDic['wd']))
                    conn.commit()

                    break
                except Exception as e:
                    message = 'fail url={},error:{}'.format(url, e)
                    print(message)
                    with open(failUrl, 'a') as f:
                        f.write(line)
                    break
            except Exception as e:
                count += 1
                if count == 3:
                    message = 'fail url={},error:{}'.format(url, e)
                    print(message)
                    with open(failUrl, 'a') as f:
                        f.write(line)

if __name__ == '__main__':
    headers= gen_headers()
    fileIn='url.txt'
    fileOut = 'result.txt'
    failUrl = 'failUrl.txt'
    conn = sqlite3.connect('/home/ubuntu/SQLiteDB/testCar.db')
    cursor = conn.cursor()
    # cursor.execute('''CREATE TABLE cars0615(source text, url text, title text, brand text, model text, doors text, color text, gasoline text,
    #              cc INTEGER , transmission text, equip text, mileage INTEGER , years INTEGER , location text,
    #              posttime INTEGER, price NUMERIC, certificate text, wd text)''')

    get_car_infos(headers, fileIn, fileOut, failUrl, conn, cursor)