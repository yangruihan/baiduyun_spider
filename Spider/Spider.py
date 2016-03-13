#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
import requests
import json
import math
import pymongo


class Spider(object):
    ERROR_PAGE_TITLE = ['页面不存在 - 百度云', '百度云 网盘-链接不存在', '百度云升级']

    def __init__(self, max_deep=30, max_item_num=0):
        self.user_count = 0  # 一共获取的用户数
        self.item_count = 0  # 一共获取的资源数
        self.share_every_page_num = 60  # 每页显示的分享数目
        self.follow_every_page_num = 24  # 每页显示的订阅者数目
        self.max_deep = max_deep  # 爬取的最大深度
        self.max_item_num = max_item_num  # 爬取的最大人数
        self.visited_user = []  # 爬取过的人的uk记录list

    def get_info(self, uk, deep):
        if self.max_item_num == 0 and deep > self.max_deep:
            return
        elif self.item_count >= self.max_item_num:
            return

        headers = {
            "Accept": "image/webp,image/*,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "",
            "Host": "pan.baidu.com",
            "Referer": "http://pan.baidu.com/share/home?uk=" + uk + "&view=share",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36",
        }

        info_url = 'http://pan.baidu.com/pcloud/user/getinfo?bdstoken=null&query_uk=' + uk + '&channel=chunlei&clienttype=0&web=1'

        try:
            js = json.loads(requests.get(info_url, headers=headers).text)
            pubshare_count = js['user_info']['pubshare_count']  # 获得分享文件数
            follower_count = js['user_info']['follow_count']  # 获得订阅人数
            fans_count = js['user_info']['fans_count']  # 获得粉丝人数，决定权重

            if uk in self.visited_user:
                return
            else:
                self.visited_user.append(uk)

            # 获得该用户的资源
            self._get_share_info(uk, pubshare_count, fans_count, headers)

            # 遍历该用户的订阅者资源
            self._get_follower_info(uk, follower_count, headers, deep)
        except Exception as e:
            print('[ERROR]获取用户信息错误')
            return

    def _get_follower_info(self, uk, follower_count, headers, deep):
        """
        :param follow_count: 订阅者数量
        :param headers: 请求头
        """
        if int(follower_count) == 0:
            return

        follower_urls = []
        for i in range(int(follower_count) // self.follow_every_page_num):
            follower_url = 'http://pan.baidu.com/pcloud/friend/getfollowlist?' + \
                           'query_uk=' + uk + \
                           '&limit=' + str(self.follow_every_page_num) + \
                           '&start=' + str(i * self.follow_every_page_num) + \
                           '&bdstoken=null&channel=chunlei&clienttype=0&web=1'
            follower_urls.append(follower_url)
        if int(follower_count) % self.follow_every_page_num != 0:
            follower_url = 'http://pan.baidu.com/pcloud/friend/getfollowlist?' + \
                           'query_uk=' + uk + \
                           '&limit=' + str(self.follow_every_page_num) + \
                           '&start=' + str(int(follower_count) // self.follow_every_page_num) + \
                           '&bdstoken=null&channel=chunlei&clienttype=0&web=1'
            follower_urls.append(follower_url)
        for url in follower_urls:
            try:
                js = json.loads(requests.get(url, headers=headers).text)
                follower_list = js['follow_list']
                for follower in follower_list:
                    uk = str(follower['follow_uk'])
                    self.get_info(uk, deep + 1)
            except Exception as e:
                print(e)
                return

    def _get_share_info(self, uk, pubshare_count, fans_count, headers):
        """
        :param uk: 该用户的uk编号
        :param pubshare_count: 分享文件数量
        :param headers: 请求头
        """
        if int(pubshare_count) == 0:
            return

        # 计算该用户资源权重
        resource_weight = int(math.sqrt(int(fans_count)))

        self.user_count += 1  # 获得的用户数+1
        print("正在获得第" + str(self.user_count) + "用户的资源信息(http://pan.baidu.com/share/home?uk=" + str(
            uk) + "&view=share#category/type=0)：")
        get_share_count = 0  # 记录获得的资源的数量

        share_urls = []
        for i in range(1, int(pubshare_count) // self.share_every_page_num + 1):
            share_url = 'http://pan.baidu.com/share/homerecord?uk=%s&page=%s&pagelength=%s' % (
                uk, i, self.share_every_page_num)
            share_urls.append(share_url)
        if int(pubshare_count) % self.share_every_page_num != 0:
            share_url = 'http://pan.baidu.com/share/homerecord?uk=%s&page=%s&pagelength=%s' \
                        % (uk, int(pubshare_count) // self.share_every_page_num + 1, self.share_every_page_num)
            share_urls.append(share_url)

        for url in share_urls:
            try:
                js = json.loads(requests.get(url, headers=headers).text)
                share_list = js['list']
                share_item_info = []
                for i in share_list:
                    if i['shorturl'] == '':
                        get_share_count += 1  # 当前用户资源数加一
                        print("--[ERROR]该用户第" + str(get_share_count) + "个资源信息无效")
                        continue

                    share_item_url = 'http://pan.baidu.com/s/' + i['shorturl']
                    share_item_title = i['typicalPath'].split('/')[-1]
                    # share_item_info.append(share_item_title + "|" + share_item_url)
                    share_item_info.append({'title': share_item_title,
                                            'url': share_item_url,
                                            'score': resource_weight})
                    get_share_count += 1  # 当前用户资源数加一
                    self.item_count += 1  # 获取的资源数加一
                    print("--[SUC]获取总第" + str(self.item_count) + "个资源，该用户第" + str(get_share_count) + "个资源信息：" +
                          share_item_title + "|" + share_item_url + "|" + str(resource_weight))

                # 写如文件
                # with open("item_names", "a") as f:
                #     for name in share_item_info:
                #         f.write(name + "\n")
                #     share_item_info.clear()

                # 写入数据库
                conn = pymongo.MongoClient()
                baiduyun_db = conn.BaiduyunDB2
                collection = baiduyun_db.baiduyun_resource
                for item in share_item_info:
                    collection.insert(item)

            except Exception as e:
                print(e)
                return

        print("-----信息写入完成-----")
