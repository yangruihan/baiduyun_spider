#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import pymongo
import time
import re


def custom_cmp(x, y):
    return cmp(x[1], y[1]) if cmp(x[0], y[0]) == 0 else cmp(x[0], y[0])


if __name__ == '__main__':
    key_word = input("请输入关键词（输入exit退出）：")
    while key_word.lower() != "exit":
        suggestions = []
        pattern = '.*?'.join(key_word)
        regex = re.compile(pattern)
        conn = pymongo.MongoClient()
        db = conn.BaiduyunDB
        time_start = time.time()
        baiduyun_resource = db.baiduyun_resource
        result = baiduyun_resource.find({"title": {"$regex": pattern}}, ["title", "url", "score"]).sort(
            [("score", pymongo.DESCENDING)])
        for r in result:
            match = regex.search(r["title"])
            suggestions.append((len(match.group()), match.start(), r["title"], r["url"], r["score"]))

        final_result = [[x, y, z] for _, _, x, y, z in sorted(suggestions)]
        for r in final_result:
            print(r)
        print("\n共查询到" + str(result.count()) + "条记录")
        print("用时" + str(time.time() - time_start) + "秒")
        key_word = input("请输入关键词（输入Exit退出）：")
