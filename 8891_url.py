import requests
from bs4 import BeautifulSoup
import re
import threading
import time
import json
import pprint
from random import randint
import math
import datetime

def gen_headers():
    referers = ['tw.yahoo.com', 'www.google.com', 'http://www.msn.com/zh-tw/', 'http://www.pchome.com.tw/']
    user_agents = ['Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
              'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)']
    headers = {'user-agent': user_agents[randint(0, len(user_agents) - 1)],
               'referer': referers[randint(0, len(referers) - 1)]}
    return headers


# get total number of cars
def get_car_no(url):
    res = requests.get(url)
    js = json.loads(res.text)
    car_no = int(js['data']['total'])

    return car_no


# get url and first info group(without doors, color, gasoline, equip)
def get_car_urls(brand_list, car_no, headers, file_out):

    page_no = math.ceil(car_no / 20)
    for page in range(1, page_no + 1):
        count = 0

        # try 3 requests
        while count < 3:

            try:
                url = 'https://auto.8891.com.tw/usedauto-search.html?page={}'.format(page)
                res = requests.get(url, headers=headers)
                #8891每頁的res回傳一個有20輛車的json(有12欄資訊直接由此獲得)
                js = json.loads(res.text.lower())
                data = ""
                for i in range(1, len(js['data']['data'].keys()) + 1):
                    info = js['data']['data'][str(i)]
                    if (info['auto_brand_en'].upper() in brand_list):
                        carDic = {'source': '8891'}
                        carDic['url'] = 'https://auto.8891.com.tw/usedauto-infos-{}.html'.format(info['id'])
                        carDic['title'] = info['auto_title_all']
                        carDic['brand'] = info['auto_brand_en']
                        carDic['model'] = info['item_kind_name_en']
                        carDic['cc'] = int(float(info['auto_gas_size'].lower().split('l')[0]) * 1000)
                        carDic['transmission'] = info['auto_tab_name']
                        mile_search = re.search(r'[0-9.]+', info['auto_mileage_num'])
                        wen_search = re.search(r'萬', info['auto_mileage_num'])
                        if mile_search:
                            if wen_search:
                                carDic['mileage'] = int(float(mile_search.group()) * 10000)
                            else:
                                carDic['mileage'] = int(float(mile_search.group()))
                        else:
                            carDic['mileage'] = -1
                        carDic['years'] = int(re.search(r'[0-9]+', info['auto_year_type']).group())
                        carDic['location'] = info['auto_address']
                        date_str = info['item_post_date']
                        carDic['posttime'] = int(datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").timestamp())
                        carDic['price'] = float(info['auto_price'])
                        data += "{}|{}|{}\n".format(carDic['url'], carDic['posttime'],
                                                    json.dumps(carDic, ensure_ascii=False))
                    else:
                        continue  # jump over the car where its brand is not in our brand_list

                #每頁會輸出20行的data 每行的格式："url|posttime(string)|{已經有12欄資料的Dictionary}"
                with open(file_out, 'a') as f:
                    f.write(data)
                # progree存到csv
                with open('progress.csv', 'w') as f:
                    f.write('{}\n'.format(page))
                break  # after succefully write data, break while
            except Exception as e:
                count += 1
                if count == 3:
                    message = 'fail page:{},error:{}'.format(page, e)
                    #exception直接印出
                    print(message)
            finally:
                time.sleep(0.2)

if __name__=='__main__':
    headers= gen_headers()
    car_no= get_car_no()
    brand_list = ['AUDI', 'MERCEDES-BENZ', 'BMW', 'FORD', 'HONDA', 'LEXUS', 'MAZDA', 'MITSUBISHI',
                  'NISSAN', 'PORSCHE', 'SUZUKI', 'SUBARU', 'TOYOTA', 'VOLVO', 'VOLKSWAGEN']
    fileOut='url.txt'

    #測試時car_no可以自己填100(只爬100輛車)
    get_car_urls(brand_list, car_no, headers, fileOut)
