'''
Author: GanJianWen
Date: 2020-10-25 16:04:28
LastEditors: GanJianWen
LastEditTime: 2021-02-17 22:37:53
QQ: 1727949032
Gitee: https://gitee.com/gan_jian_wen_main
'''
from selenium import webdriver
from bs4 import BeautifulSoup
from mysql import create_connect, operation_database
from time import sleep
import re
import requests
import json
import sys
from pprint import pprint
from os.path import exists
from os import makedirs
file_path = "D:/files/python/code/django/mysite/static"


class Scrapy51XXX():
    def __init__(self):
        self.ip = "localhost"
        self.user = "root"
        self.password = "123456"
        self.database = "sex"
        self.db = create_connect(
            self.ip, self.user, self.password, self.database)

    def __del__(self):
        self.db.close()

    def get_number(self):
        with open("number.txt", "r") as fp:
            return int(fp.readline())

    def save_number(self, number):
        with open("number.txt", "w") as fp:
            fp.write(str(number))
            fp.close()

    def get_m3u8_number(self):
        if not exists("m3u8_number.txt"):
            self.save_m3u8_number(10)

        with open("m3u8_number.txt", "r") as fp:
            return int(fp.readline())

    def save_m3u8_number(self, number):
        with open("m3u8_number.txt", "w") as fp:
            fp.write(str(number))
            fp.close()

    def add_data(self, id: int, content: str, url: str):
        sql = "insert into videos values(%d,'%s',NULL,'%s',NULL,NULL,NULL,NULL);" % (
            id, content, url)
        operation_database(self.db, sql, "id", id)

    def select_null_data(self):
        sql = "select id,content from videos where image is NULL or updateDate is NULL or duration is NULL or sduration is NULL;"
        cur = self.db.cursor()
        cur.execute(sql)
        results = cur.fetchall()
        return results

    def update_data(self, id, image, update_time, duration, sduration):
        sql = "update videos set image='%s',updateDate='%s',duration=%d,sduration='%s' where id=%d" % (
            image, update_time, duration, sduration, id)
        operation_database(self.db, sql)

    def ask_url(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56'
        }
        response = requests.get(url, headers=headers)
        return response.content

    def vist_51xxx(self):
        self.driver = webdriver.Chrome()
        begin_number = self.get_number()
        for i in range(begin_number, 80000):
            self.driver.get("http://www.147147.net/videoinfo?id="+str(i))
            sleep(1)
            html = self.driver.page_source
            bs = BeautifulSoup(html, "html.parser")
            code = bs.find('div', class_="code")
            if code is not None:
                if code.get_text().strip() == "500":
                    self.driver.quit()
                    return
            try:
                content = bs.find(attrs={'class': 'body'}).get_text(
                ).strip().replace('\n', '').replace('\r', '').replace("'", '"')
                print(content)
            except:
                continue
            url = "http://www.147147.net"+bs.find(
                attrs={'webkitallowfullscreen': 'webkitallowfullscreen'})['src']
            self.driver.get(url)
            html = self.driver.page_source
            try:
                url = "http://www.147147.net" + \
                    re.findall('playurl = "(.+?)";', html)[0]
                print(url)
            except Exception as e:
                print(str(e))
                continue
            try:
                self.add_data(id=i, content=content, url=url)
                self.save_number(i)
            except Exception as e:
                print(str(e))

    def get_detail(self):
        print('开始获取详细信息')
        result_list = self.select_null_data()
        for result in result_list:
            page, flag = 1, 1
            id = int(result[0])
            content = result[1]
            if len(content) > 10:
                content = content[:10]
            while True:
                url = "http://www.147147.net/ajaxvideosearch?keyword=%s&page=%d" % (
                    content, page)
                print("url=", url)
                message = self.ask_url(url).decode('utf-8')
                datas = json.loads(message)
                if datas["code"] == 200:
                    for data in datas["data"]:
                        pprint(data)
                        if data["id"] == id:
                            # pprint(data)
                            image = data["cover_pic"]
                            update_time = data["uploaddate"]
                            duration = data["duration"]
                            sduration = data["sduration"]
                            self.update_data(
                                id, image, update_time, duration, sduration)
                            flag = 0
                            break
                    page += 1
                else:
                    break
                if flag == 0:
                    break

    def get_types(self):
        type_list = ["国产精品", "网红模特", "欧美合集",
                     "日韩合集", "福利大秀", "热门直播", "动漫合集", "国产剧情"]
        max_page = 5
        for type in type_list:
            page = 1
            while True:
                url = "http://www.147147.net/ajaxvideoloadcategory?category=%s&page=%d" % (
                    type, page)
                print("url=", url)
                message = self.ask_url(url).decode('utf-8')
                datas = json.loads(message)
                if datas["code"] == 200 and len(datas["data"]) > 0:
                    for data in datas["data"]:
                        id = data["id"]
                        sql = "update videos set type='%s' where id=%d;" % (
                            type, id)
                        operation_database(self.db, sql)
                    page += 1
                    if page > int(max_page):
                        break
                else:
                    break

    def get_picture_list(self):
        sql = "select id,image from videos where image is NOT NULL order by id;"
        cursor = self.db.cursor()
        cursor.execute(sql)
        result_list = cursor.fetchall()
        # print(result_list)
        return result_list

    def load_picture_number(self):
        if not exists("count_picture.txt"):
            with open("count_picture.txt", 'w') as fp:
                fp.write(str(10))
                fp.close()

        with open("count_picture.txt", 'r') as fp:
            number = int(fp.readline())
            fp.close()
            return number

    def save_picture_number(self, number):
        with open("count_picture.txt", 'w') as fp:
            fp.write(str(number))
            fp.close()

    def save_pictures(self, result_list):
        if not exists("%s/images/videos/covers" % file_path):
            makedirs("%s/images/videos/covers" % file_path)
        number = self.load_picture_number()
        for id, picture in result_list:
            print(id)
            if id < number:
                continue
            print("picture=", picture)
            try:
                content = self.ask_url(picture)
            except Exception as e:
                print(str(e))
                self.save_picture_number(id+1)
                continue
            file_name = picture.split("/")[-1]
            sql = "update videos set image='%s' where image='%s';" % (
                file_name, picture)
            with open("%s/images/videos/covers/%s" % (file_path, file_name), "wb") as fp:
                fp.write(content)
                fp.close()
                operation_database(self.db, sql)
                self.save_picture_number(id+1)

    def get_pictures(self):
        result_list = self.get_picture_list()
        self.save_pictures(result_list)

    def get_m3u8_file(self):
        if not exists("%s/m3u8" % file_path):
            makedirs("%s/m3u8" % file_path)
        if not exists("%s/keys" % file_path):
            makedirs("%s/keys" % file_path)
        number = self.get_m3u8_number()
        sql = "select id,url from videos"
        cursor = self.db.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        for id, url in results:
            print('id=', id)
            if id < number:
                continue
            content = self.ask_url(url)
            file_name = url.split('/')[-1]
            with open('%s/m3u8/%s' % (file_path, file_name), 'wb') as fp:
                fp.write(content)
                fp.close()
            with open('%s/m3u8/%s' % (file_path, file_name), 'r', encoding='utf-8') as fp:
                lines = fp.readlines()
                fp.close()
            with open('%s/m3u8/%s' % (file_path, file_name), 'w', encoding='utf-8') as fp:
                for line in lines:
                    if line.find('URI') != -1:
                        uri_pos = line.find("URI")
                        quotation_mark_pos = line.rfind('"')
                        key_path = line[uri_pos:quotation_mark_pos].split('"')[
                            1]
                        key_url = "http://www.147147.net" + key_path  # 拼出key解密密钥URL
                        print("key_url:", key_url)
                        key_content = self.ask_url(key_url)
                        key_name = key_url.split('/')[-1]
                        with open('%s/keys/%s' % (file_path, key_name), 'wb') as fk:
                            fk.write(key_content)
                            fk.close()
                        line = line.replace('m3u8', 'static/keys')
                    fp.write(line)
            self.save_m3u8_number(id+1)

    def main(self):
        self.vist_51xxx()
        self.get_detail()
        self.get_types()
        self.get_pictures()
        self.get_m3u8_file()


def menu():
    print("0:退出")
    print("1:爬取url")
    print("2:爬取其他属性")
    print("3:爬取类型")
    print("4:下载图片")
    print("5:下载m3u8")
    print("6:全部执行")
    choose = input('选择:')
    return choose


if __name__ == "__main__":
    choose = menu()
    spider = Scrapy51XXX()
    spider_list = [sys.exit, spider.vist_51xxx,
                   spider.get_detail, spider.get_types, spider.get_pictures, spider.get_m3u8_file, spider.main]
    spider_list[int(choose)]()
