'''
Author: GanJianWen
Date: 2021-02-10 23:05:38
LastEditors: GanJianWen
LastEditTime: 2021-02-12 11:16:10
QQ: 1727949032
Gitee: https://gitee.com/gan_jian_wen_main
'''
import os
import requests
import csv
from Crypto.Cipher import AES
from pprint import pprint
from mysql import create_connect, close_connect
import sys


def wirte_m3u8_csv():
    if not os.path.exists("data"):
        os.mkdir("data")
    header = ['编号', '内容', '链接', '时长']
    db = create_connect("localhost", 'root', '123456', 'sex')
    cursor = db.cursor()
    sql = "select id,content,url,sduration from videos order by id;"
    cursor.execute(sql)
    data_list = cursor.fetchall()
    close_connect(db)
    with open("data/data.csv", "w", encoding='utf-8-sig') as fp:
        csv_fp = csv.writer(fp)
        csv_fp.writerow(header)
        for data in data_list:
            data = list(map(str, data))
            data[3] = "[%s]" % data[3]
            print(data)
            csv_fp.writerow(data)


def download(url, name):
    download_path = os.getcwd() + "\download"
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    # print(download_path)
    all_content = requests.get(url).text
    # print("m3u8:", all_content)
    file_line = all_content.split("\n")

    unknow = True
    key = ""
    total_line = len(file_line)
    for index, line in enumerate(file_line):
        # print("line:", line)
        download_progress = int(index/total_line*100)
        str = '>'*(download_progress//2)+' '*((99-download_progress)//2)
        sys.stdout.write('\r'+str+'[%d%%]' % (download_progress+1))
        sys.stdout.flush()
        if "#EXT-X-KEY" in line:  # 找解密Key
            method_pos = line.find("METHOD")
            comma_pos = line.find(",")
            method = line[method_pos:comma_pos].split('=')[1]
            # print("Decode Method：", method)

            uri_pos = line.find("URI")
            quotation_mark_pos = line.rfind('"')
            key_path = line[uri_pos:quotation_mark_pos].split('"')[1]
            # print("key_path:", key_path)
            key_url = "http://www.147147.net" + key_path  # 拼出key解密密钥URL
            res = requests.get(key_url)
            # print("key_url", key_url)
            key = res.content

        if "EXTINF" in line:  # 找ts地址并下载
            unknow = False
            pd_url = file_line[index + 1]  # 拼出ts片段的URL
            # print(pd_url)

            res = requests.get(pd_url)
            c_fule_name = file_line[index + 1].rsplit("/", 1)[-1]
            if len(key):  # AES 解密
                cryptor = AES.new(key, AES.MODE_CBC, key)
                with open(os.path.join(download_path, "%s.mp4" % name), 'ab') as f:
                    f.write(cryptor.decrypt(res.content))
            else:
                with open(os.path.join(download_path, c_fule_name), 'ab') as f:
                    f.write(res.content)
                    f.flush()
    if unknow:
        raise BaseException("未找到对应的下载链接")
    else:
        print("下载完成")
    os.system('pause')


def main():
    id = input("输入要下载的视频编号(参考data.csv):")
    with open("data/data.csv", "r", encoding='utf-8-sig') as fp:
        reader_csv = csv.reader(fp)
        for line in reader_csv:
            if len(line) <= 0:
                continue
            if str(id) == line[0]:
                download(line[2], line[1])
                return

    print("无该id")


if __name__ == '__main__':
    choose_list = [sys.exit, wirte_m3u8_csv, main]
    while True:
        print('1、获取视频url')
        print('2、下载视频')
        print('0、退出')
        choose = input('选择:')
        choose_list[int(choose)]()
