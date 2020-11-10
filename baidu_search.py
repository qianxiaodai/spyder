# -*- coding: utf-8 -*-
import time

import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import re
import pandas as pd
from pandas import ExcelWriter
import os
import socket
from socket import gethostbyname, getaddrinfo
# from json import loads
"""
爬取百度搜索结果
"""

base_url = r'https://www.baidu.com/s?'
MAX_NUM = 76

Headers = {
    # User-Agent:
    # 'Connection': 'Keep-Alive',
    'Connection': 'close',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    # 'Accept-Encoding': 'gzip, deflate',
    'Accept': 'text/html, application/xhtml+xml, */*',
    'User-Agent': 'Mozilla/6.1 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'

}


def get_real_pages(wd, page_no):
    """根据百度搜索的页数的默认最大值获取"""
    pn = str((page_no - 1) * 10)
    params = {
        'wd': wd,
        'pn': pn,
    }
    url = base_url + urlencode(params)

    html = is_visit(url)
    page = '<span class="pc">(\\d+)'
    result = re.findall(page, html)
    max_page = result[-1]  # 获取每个关键词下当前pn的最大值
    return int(max_page)


def is_visit(url):
    # url = base_url + urlencode(params)
    while True:
        try:
            r = requests.get(url, headers=Headers, timeout=20)
            r.encoding = 'utf-8'
            html = r.text
            return html

        except requests.exceptions.ConnectionError as e:
            print("Errors: ", e.args)
            time.sleep(3)


def get_urls(k, pages):
    """获取每个关键词下所有页面的url"""

    for i in range(1, pages+1):
        pn = str((i - 1) * 10)
        params = {
            'wd': k,
            'pn': pn
        }
        url = base_url + urlencode(params)
        yield url


def time_format(s):
    sub_s = re.sub('\\W', '', s)
    return sub_s


def drop_date(s):
    sub_s = re.sub('(\\d{4}年(\\d+[月日]){2}|\\d+天前).*?-\\s+', '', s)
    return sub_s


def is_space(s):
    s = re.sub('\\s', '', s)
    return s


def host_to_ip(url):
    print(url)
    p = re.compile('//(.*?)/')
    host = re.search(p, url).group(1)
    print(host)
    try:
        ip = gethostbyname(host)
        while True:
            try:
                link = base_url + 'wd={}'.format(ip)
                r = requests.get(link, headers=Headers, timeout=20)
                r.encoding = 'utf-8'
                soup = BeautifulSoup(r.text, 'lxml')
                td = soup.find('div', {'class': 'c-span21 c-span-last op-ip-detail'}).td
                text = td.text.replace(td.span.text, '')
                place = is_space(text)
                return ip, place
            except requests.exceptions.ConnectionError as e:
                print("Errors: ", e.args)
                time.sleep(3)
    except:
        print("DNS is invalid!")
        ip = 'unknown'
        place = 'unknown'
        return ip, place


def parse_html(link):
    """解析当前页面， 获取每个文章的链接(新增一列域名)， 原始网页标题， 贴文内容， 发帖时间， 发帖人"""
    html = is_visit(link)

    soup = BeautifulSoup(html, 'lxml')
    titles = soup.find_all('div', {'class': 'result c-container '})
    for title in titles:
        tag1 = title.find('div', {'class': 'c-tools'})
        # print(tag1.get('data-tools'))
        # cur_tool = tag1.get('data-tools')
        # print(cur_tool)
        # if '\\' in cur_tool:
        #   cur_tool = cur_tool.replace('\\', '')
        tools = eval(tag1.get('data-tools'))  # 将json类型转成字典
        url = tools.get('url')  # 帖子链接
        r = requests.get(url, headers=Headers, allow_redirects=False)
        origin_url = r.headers['location']  # 得到网页原始地址
        host, belonged = host_to_ip(origin_url)
        post = tools.get('title')  # 帖子标题
        tag2 = title.find('div', {'class': 'c-abstract'})
        text = drop_date(tag2.text) if tag2 else None
        # print(text)
        tag3 = title.find('span', {'class': ' newTimeFactor_before_abs m'})
        time = time_format(tag3.text) if tag3 else None  # 发帖时间
        yield {
            'URL地址': origin_url,
            '物理IP': host,
            '网站属地': belonged,
            '原始网页标题': post,
            '帖文内容': text,
            '发帖时间': time
        }


def crawl(k, page_no):
    max_pages = get_real_pages(k, page_no)  # 获取每个关键词搜索结果的总页数

    urls = get_urls(k, max_pages)  # 获取每个关键词下的所有的url
    post_info = []

    for i, url in enumerate(urls):
        print("正在获取{0}搜索结果第{1}页内容链接".format(k, i+1))
        results = parse_html(url)
        for result in results:
            post_info.append(result)
    return post_info


def write_to_file(data, name):
    columns = ['URL地址', '物理IP', '网站属地', '原始网页标题', '帖文内容', '发帖时间']
    df = pd.DataFrame(data, columns=columns)
    with ExcelWriter(name, options={'strings_to_urls': False}) as writer:
        df.to_excel(writer, sheet_name='sheet1', index=False)
    # with ExcelWriter(name) as writer:
    #     df.to_excel(writer, sheet_name='sheet1', index=False)


if __name__ == '__main__':
    # search_words = ['梯子翻墙教程', 'VPN教程', 'Shadowsocks教程',
    #                 'goagent教程', 'chrome爬墙', '翻墙代理',
    #                 'SSR教程', '翻墙加速器', '网络加速器',
    #                 'V2Ray', 'WireGuard', '加密代理'
    #                 '网络防火墙', 'Lanten官网', '翻墙教程',
    #                 'IP解封']
    # search_words = ['赛风上网', 'Enterprise VPN', 'VPN 的主'
    #                 '代理服务器', 'ShadowsocksRR', 'ShadowsocksR', 'Global VPN',
    #                 'strong vpn', 'VPN for phone', 'eyeVPN']
    search_words = ['strong vpn']

    post_infos = []
    for search_word in search_words:
        current_posts = crawl(search_word, MAX_NUM)
        post_infos.extend(current_posts)
    # print(post_infos)
    file = '境内推荐信息.xlsx'
    if os.path.exists(file):
        os.remove(file)

    write_to_file(post_infos, file)
