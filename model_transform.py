
import pymysql
import csv
import re
import sys

class CK_mySQL:
    IP = '192.168.196.36'
    user = 'team1'
    passwd = 'team1'
    db = 'team1'
    table = 'crawl_temp'
# generate 1.model transform dictionary 2.regular expression dictionary
def gen_transform_dict(csvfile):
    brand_list = []
    modelTransform = {}
    with open(csvfile, "r", encoding='Big5') as f:
        reader = csv.DictReader(f)
        for line in reader:
            brand = line['brand'].lower()
            key = line['key'].strip().lower()
            value = line['value'].strip().lower()
            if brand not in modelTransform.keys():
                brand_list.append(brand)
                modelTransform[brand] = {key: value}
            else:
                modelTransform[brand].update({key: value})
    regex_strs = {}
    for brand in brand_list:
        regex_str = ""
        for keys in modelTransform[brand].keys():
            regex_str += '{}|'.format(keys)
            regex_strs[brand] = regex_str.strip('|')

    return (modelTransform, regex_strs)

def model_transform(model_dict, regex_dict, brand, model):
    regex = regex_dict[brand]
    model_list = re.findall('{}'.format(regex), model, re.IGNORECASE)
    model_list.sort(key=len, reverse=True)
    new_model = model_dict[brand][model_list[0].lower()]
    return new_model


def gen_newdata(CK_mySQL):
    conn1 = pymysql.connect(host=CK_mySQL.IP, port=3306, user=CK_mySQL.user, passwd=CK_mySQL.passwd, db=CK_mySQL.db,
                            charset='utf8')
    cur1 = conn1.cursor()

    sql = "SELECT * FROM {} where years>=2008;".format(CK_mySQL.table)
    cur1.execute(sql)

    newdata = []
    for row in cur1:

        try:
            url = row[1]
            brand = row[3].lower()
            model = row[2] + row[4]
            # model_transfrom is used here
            new = model_transform(m, r, brand, model)
            if (new != row[4]):
                newdata.append((new, url))

        except Exception as e:
            with open('fail_model.csv', 'a') as f:
                f.write('{},{},{},{}\n'.format(brand, row[4], row[2], url))

    conn1.close()
    return newdata

if __name__ == '__main__':
    m, r = gen_transform_dict('./yahoo-model-transformation.csv')
    newdata = gen_newdata(CK_mySQL)
    conn2 = pymysql.connect(host=CK_mySQL.IP, port=3306, user=CK_mySQL.user, passwd=CK_mySQL.passwd, db=CK_mySQL.db,
                            charset='utf8')
    cur2 = conn2.cursor()
    l = len(newdata)
    print('number of data need to be updated:{}'.format(l))
    count = 0
    for idx, car in enumerate(newdata):
        newmodel = car[0]
        url = car[1]
        try:
            sql = 'UPDATE {} SET model=%s WHERE url= %s;'.format(CK_mySQL.table)
            cur2.execute(sql, (newmodel, url))
            if idx % 500 == 0:
                conn2.commit()
        except Exception as e:
            print(e)
            conn2.rollback()
        count += 1
        printStr = 'now is {}, {}% finished'.format(count, round(count / l * 100))
        sys.stdout.write('\r' + printStr)
    conn2.commit()
    conn2.close()