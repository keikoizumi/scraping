import os
import os.path
import json
import time
import datetime         
import random   
import string           
import mysql.connector
#import logging
# Webブラウザを自動操作する（python -m pip install selenium)
from selenium import webdriver 


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_LEVEL_FILE = 'ERROR'
# フォーマットを指定
_detail_formatting = '%(asctime)s %(levelname)-8s [%(module)s#%(funcName)s %(lineno)d] %(message)s'

#logging.basicConfig(
#    level=getattr(logging, LOG_LEVEL_FILE),
#    format=_detail_formatting,
#    filename=BASE_DIR+'/logs/yahoo.log'
#)

#logger = logging.getLogger(__name__)
#logger.error('IF EXIT ERROR, SHOW BELLOW')

    

#定数一覧
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

    driver = webdriver.Chrome(BASE_DIR+'./static/chromedriver.exe')
    targetUrl = 'https://news.yahoo.co.jp/'
    #遷移   
    driver.get(targetUrl)   
except Exception as e:
    print('error')
finally:
    time.sleep(1)

def main(driver):
    # ループ番号、ページ番号を定義
    i = 1 
    # 最大何ページまで分析するかを定義              
    i_max = 1
    try:
        while i <= i_max:
            # リンクはclass="topicsListItem"に入っている
            class_group = driver.find_elements_by_class_name("topicsListItem")
            # タイトルとリンクを抽出しリストに追加するforループ    
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

                driver.execute_script("window.open()") #make new tab
                driver.switch_to.window(driver.window_handles[1]) #switch new tab
                driver.get(url)
                time.sleep(1)
                driver.get_screenshot_as_file(BASE_DIR+'/static/img/Selenium/'+d+'/'+imgId+'.png')
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                #DB設定
                #f = open('./bottle_spa_test3/conf/prop.json', 'r')
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
                #日にち取得
                now = datetime.datetime.now()
                dt = "{0:%Y-%m-%d %H:%M:%S}".format(now)
                # データベースに接続する
                c = conn.cursor()
                #データ登録
                sql = "INSERT INTO testdb.yahoo_news_urls (site_id,title,url,dt,img_id) VALUES (1,%s,%s,%s,%s)"
                c.execute(sql, (title, url, dt, imgId))
                print(sql)
                #idを振りなおす
                sql = 'SET @i := 0' 
                c.execute(sql)
                sql = 'UPDATE `testdb`.`yahoo_news_urls` SET id = (@i := @i +1);'
                c.execute(sql)
                # 挿入した結果を保存（コミット）する
                conn.commit()
                # データベースへのアクセスが終わったら close する
                conn.close()
            i = i_max + 1  
        
    except Exception as e:
        #logger.error(e)
    finally:
        # ブラウザを閉じる
        driver.quit()         
        
# ranking関数を実行
main(driver)

