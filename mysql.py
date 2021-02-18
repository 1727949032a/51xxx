'''
Author: GanJianWen
Date: 2020-12-24 00:51:24
LastEditors: GanJianWen
LastEditTime: 2021-02-08 23:19:12
QQ: 1727949032
Gitee: https://gitee.com/gan_jian_wen_main
'''


from pymysql import connect


def error_log(e, variable_name=None, variable=None):
    print("数据库发生错误,请查看日志")
    if variable is None:
        variable = variable_name = str()
    with open("mysql.log", "a", encoding='utf-8') as fp:
        fp.write("%s=%s, error=%s\n" %
                 (str(variable_name), str(variable), str(e)))
        fp.close()


def create_connect(ip, userName, password, database):
    try:
        db = connect(host=ip,
                     user=userName,
                     password=password,
                     db=database,
                     charset='utf8mb4')
        return db
    except Exception as e:
        error_log(e)
        return None


def close_connect(db):
    try:
        db.close()
    except Exception as e:
        error_log(e)


def operation_database(db, sql, variable_name=None, variable=None):
    print(sql)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        error_log(e, variable_name, variable)
    return db
