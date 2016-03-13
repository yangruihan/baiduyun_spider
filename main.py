#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from Spider.Spider import Spider
from email.mime.text import MIMEText
import smtplib
import random

mail_to_list = list()
mail_host = 'smtp.qq.com'  # 设置服务器
mail_user = '770362426'  # 用户名
mail_pass = ''  # 密码
mail_postfix = 'qq.com'  # 发件箱后缀


def send_mail(to_list, sub, content):
    me = '<' + mail_user + "@" + mail_postfix + '>'
    msg = MIMEText(content, _subtype='plain', _charset='utf8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    spider = Spider(max_item_num=100000000)

    while spider.item_count < spider.max_item_num:
        uk = random.randint(1000000000, 9999999999)
        spider.get_info(uk=str(uk), deep=0)

    mail_to_list.append("yangruihan@vip.qq.com")
    content = '-----资源爬取结果-----\n' + \
              '\t成功爬取' + str(spider.item_count) + "个资源\n" + \
              "\t共访问" + str(spider.user_count) + "个用户"
    if send_mail(mail_to_list, '百度云资源爬取', content):
        print(u'\n邮件发送成功')
    else:
        print(u'\n邮件发送失败')
