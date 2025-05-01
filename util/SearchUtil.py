import html
import json
import re
import requests
from bs4 import BeautifulSoup

class SearchUtil:

    def search_entry(self, name, web):
        """
        通过名字搜索剧集的相对路径，用元组储存？
        :param web:
        :param name:
        :return:
        """
        result = {}
        url = f"{web.search_url}?wd={name}&submit="
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        r = requests.get(url, headers)

        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.find_all(class_="module-search-item")

        for item in items:
            info = item.find(class_="video-info")
            header = info.find(class_="video-info-header")
            link = header.find("a")
            result[link["href"]] = link["title"]

        return result

    def search_episode(self, entry,web):
        """
        这里分两步
        第一步：搜索线路
        第二步：对不同的线路分别获取剧集
        :param entry:
        :param web:
        :return:一个数组，数组内部为不同线路的元组
        """
        # 发送首页请求
        url = web.url+entry
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        r = requests.get(url, headers)
        soup = BeautifulSoup(r.text, "html.parser")
        # print(soup)

        # 获取线路

        ## 获取名称
        names = {}
        tab_items = soup.find_all(class_="module-tab-item")
        i = 0
        for tab_item in tab_items:
            i += 1
            names[i] = tab_item.text
        # print(names)

        ## 获取路径
        arr_id= {}
        for i in range(10):
            temp = soup.find("div", id="sort-item-" + str(i))
            if temp is not None:
                arr_id[names[i]] = i

        # 获取剧集
        result = {}

        ## 遍历每条线路
        for key, value in arr_id.items():
            temp = {}
            items = soup.find_all("div", id="sort-item-"+str(value))

            # 由于获取的items是一个列表，但列表里只有一个元素，所以用foreach取出那个元素
            for item in items:
                # 取出元素后对其查找所有的<a href>
                links =item.find_all("a")

                #将对每一个link存入temp中
                for link in links:
                    temp[link["href"]] = link["title"]
            # 将每一个剧集的数据分类存放
            result[key] = temp

        return result

    def search_url(self, episode, name,web):

        # 发送播放页请求
        player_data = None
        url = web.url + episode
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        r = requests.get(url, headers)
        soup = BeautifulSoup(r.text, "html.parser")
        # print(soup)

        wrapper = soup.find(class_="player-wrapper")
        scripts = wrapper.find_all("script")
        for script in scripts:
            if script.string and 'var player_aaaa' in script.string:
                # 提取 player_aaaa 后面的 JSON 字符串
                match = re.search('{.*?}', script.string, re.DOTALL)
                if match:
                    json_str = match.group(0)  # 提取 JSON 字符串
                    # 解析 JSON 数据
                    player_data = json.loads(json_str)

        if player_data:
            # print("url =", player_data.get("url"))
            result = {name: web.play_url+player_data.get("url")}
            return result
        else:
            return None
            # print("未找到 player_aaaa 数据")
        # url = wrapper["url"]

    # def __init__(self):
    #     # 第一步：搜索条目
    #     self.search_entry("凡人",mxdm6)
    #     # 第二步：搜索剧集
    #     # 第三步：匹配播放链接
