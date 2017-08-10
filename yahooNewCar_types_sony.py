import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint
import queue
import threading
import time
from random import randint
import multiprocessing

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



def gen_headers():
    headers = {'User-Agent': user_agents[randint(0, len(user_agents) - 1)],
               'Referer': referers[randint(0, len(referers) - 1)]}
    return headers

#
# def get_types:
#     with open('yahoo_models.txt', 'r') as f:
#         data = f.readlines()
#
#         for line in data:
#             infos = line.split('\n')[0].split('|')
#             url = infos[0]
#             typeDic = json.loads(infos[1])
#
#             res = requests.get(url)
#             res.encoding = 'utf-8'
#             soup = BeautifulSoup(res.text, 'lxml')
#             for a in soup.select('.centercol a'):
#                 typeDic['type'] = a.select_one('.title').text
#                 with open('yahoo_types.txt', 'a') as f:
#                     f.write('{}|{}\n'.format(a['href'], json.dumps(typeDic, ensure_ascii=False)))

def get_types(line):
    headers = gen_headers()
    infos = line.split('\n')[0].split('|')
    url = infos[0]
    typeDic = json.loads(infos[1])

    res = requests.get(url, headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'lxml')
    for a in soup.select('.centercol a'):
        typeDic['type'] = a.select_one('.title').text
        with open('yahoo_types.txt', 'a') as f:
            f.write('{}|{}\n'.format(a['href'], json.dumps(typeDic, ensure_ascii=False)))



def read_to_list():
    url_list = []
    with open('yahoo_models.txt', 'r') as f:
        data = f.readlines()
        for line in data:
            url_list.append(line)
        return url_list

if __name__=='__main__':
    url_list = read_to_list()
    temp_list = []
    for url in url_list:
        temp_list.append(url)
        if len(temp_list) == 4 and len(url_list) >= 4:
            pool = multiprocessing.Pool(processes=8)
            res = pool.map(get_types, temp_list)
            pool.close()
            temp_list = []
        elif len(url_list) < 4:
            pool = multiprocessing.Pool(processes=8)
            res = pool.map(get_types, temp_list)
            pool.close()




# if __name__ == "__main__":
#     url_list = []
#     while que.llen('mobile01_list') != 0:
#         url = que.blpop('mobile01_list')[1].decode('utf8')
#         url_list.append(url)
#         if len(url_list) == 5:
#             pool = multiprocessing.Pool(processes=8)
#             res = pool.map(main,url_list)
#             pool.close()
#             url_list = []
#         else:
#             print(len(url_list))