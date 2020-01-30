# coding:utf-8
from bottle import request, route, get, post, hook, response, static_file, template, redirect, run
from selenium import webdriver 
import mysql.connector
import datetime
import os.path
import random   
import string 
import random
import time
import json
import os


#status
PASTDAY = 'pastday'
ALL = 'all'

#ファイルパス
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

#CSS
@route('/static/css/<filename:path>')
def send_static_css(filename):
    return static_file(filename, root=f'{STATIC_DIR}/css')

#JS
@route('/static/js/<filename:path>')
def send_static_js(filename):
    return static_file(filename, root=f'{STATIC_DIR}/js')

#img
@route('/static/img/<filename:path>')
def send_static_img(filename):
    return static_file(filename, root=f'{STATIC_DIR}/img')

#rootの場合
@route("/")
def index():
    return template('top')

@post('/other')
def postOther():
    #値取得
    data = request.json
    date = data['date']
    qerytype = data['other']
    url = dbconn(qerytype, date)
    #ID NULLチェック
    if isUrlCheck(url):
        print('checkedUrl:')
        #json作成
        jsonUrl = makeJson(url)
        print(type(jsonUrl))
        return jsonUrl
    else:
        return postOther()

@post('/getPastDay')
def pastDay():
    date = None
    qerytype = PASTDAY
    url = dbconn(qerytype, date)
    #ID NULLチェック
    if isUrlCheck(url):
        print('checkedUrl:')
        #json作成
        jsonUrl = makeJson(url)
        print(type(jsonUrl))
        return jsonUrl
    else:
        return postOther()

@post('/scraping')
def scraping():
    if scrayping():
        return 'False'
    else:
        return 'True'

i = 0
def isUrlCheck(url):
    if url == None:
        print('チェックNG')
        global i
        i += 1
        print('i')
        print(i)
        if i < 5:
            return None 
        else:
            return True
    else:
        print('チェックOK')
        return True

def makeJson(url):
    jsonUrl = jsonDumps(url)
    return jsonUrl
    
def jsonDumps(url):
    url = json.dumps(url)
    return isTypeCheck(url)

def isTypeCheck(jsonUrl):
    if type(jsonUrl) is str:
        return jsonUrl
    else:
        jsonDumps(jsonUrl)
    

def dbconn(qerytype, date):

    f = open('./conf/prop.json', 'r')
    info = json.load(f)
    f.close()
    #DB設定
    
    conn = mysql.connector.connect(
            host = info['host'],
            port = info['port'],
            user = info['user'],
            password = info['password'],
            database = info['database'],
    )
    
    cur = conn.cursor(dictionary=True)   
    
    try:    
        #接続クエリ
        if qerytype == ALL:
            sql = "SELECT site_id,title,url,img_id,CAST(dt AS CHAR) as dt FROM scrapingInfo WHERE dt LIKE '"+date+'%'"' ORDER BY dt DESC"
        elif qerytype == PASTDAY:
            sql = "SELECT DISTINCT DATE_FORMAT(dt,'%Y-%m-%d') as dt FROM scrapingInfo ORDER BY dt DESC"

        #クエリ発行
        print(sql)
        cur.execute(sql)
        cur.statement    
        url = cur.fetchall()

        if url is not None:
            return url
        else:
            return None

    except:
        import traceback
        traceback.print_exc()
        print("DBエラーが発生しました")
        return None
    finally:
        cur.close()
        conn.close()

def scrayping():
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    try:
        #ディレクトリ存在確認
        dpath = BASE_DIR+'/static/img/Selenium'
        if not os.path.exists(dpath):
            os.makedirs(dpath)
        else:
            now = datetime.datetime.now()
            dt = "{0:%Y%m%d}".format(now)
            path = BASE_DIR+'/static/img/Selenium/'+dt
        if not os.path.isdir(path):
            os.makedirs(path)       
    except:
        print('------------------------error------------------------')
        return None
    finally:
        time.sleep(1)
        scrapingSet()

def scrapingSet():
    driver = webdriver.Chrome(BASE_DIR+'./static/chromedriver.exe')
    TARGETURL = 'https://news.yahoo.co.jp/'

    driver.get(TARGETURL)

    i = 1             
    i_max = 1
    try:
        while i <= i_max:
            class_group = driver.find_elements_by_class_name("topicsListItem")
            for elem in class_group:
                # データ登録用
                title = elem.find_element_by_tag_name('a').text
                url = elem.find_element_by_tag_name('a').get_attribute('href')
                #ディレクトリ確認
                now = datetime.datetime.now()
                d = str("{0:%Y%m%d}".format(now))
                letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                p = ''.join(random.choices(letters, k=1))
                #img名前
                iid = str("{0:%H%M%S}".format(now))
                imgId = iid + p
                #make new tab
                driver.execute_script("window.open()") 
                #switch new tab
                driver.switch_to.window(driver.window_handles[1]) 
                driver.get(url)
                time.sleep(1)
                driver.get_screenshot_as_file(BASE_DIR+'/static/img/Selenium/'+d+'/'+imgId+'.png')
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                #DB設定
                f = open('./conf/prop.json', 'r')
                info = json.load(f)
                f.close()
                conn = mysql.connector.connect(
                    host = info['host'],
                    port = info['port'],
                    user = info['user'],
                    password = info['password'],
                    database = info['database']
                )

                now = datetime.datetime.now()
                dt = "{0:%Y-%m-%d %H:%M:%S}".format(now)
                c = conn.cursor()
                #データ登録
                sql = "INSERT INTO scraping.scrapingInfo(site_id,title,url,img_id,dt) VALUES (1,%s,%s,%s,%s)"
                c.execute(sql, (title, url, imgId, dt))
                sql = 'SET @i := 0' 
                c.execute(sql)
                sql = 'UPDATE `scraping`.`scrapingInfo` SET id = (@i := @i +1);'
                c.execute(sql)
                conn.commit()
                conn.close()
            i = i_max + 1  
    except:
        print('------------------------error------------------------')
        return None
    finally:
        driver.quit()     
    return True    
    

if __name__ == "__main__":
    run(host='localhost', port=8081, reloader=True, debug=True)