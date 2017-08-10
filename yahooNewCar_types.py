import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint
import queue
import threading
import time


def get_types:
    with open('yahoo_models.txt', 'r') as f:
    data = f.readlines()

    for line in data:
        infos = line.split('\n')[0].split('|')
        url = infos[0]
        typeDic = json.loads(infos[1])

        res = requests.get(url)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'lxml')
        for a in soup.select('.centercol a'):
            typeDic['type'] = a.select_one('.title').text
            with open('yahoo_types.txt', 'a') as f:
                f.write('{}|{}\n'.format(a['href'], json.dumps(typeDic, ensure_ascii=False)))
if __name__=='__main__':
    get_types()