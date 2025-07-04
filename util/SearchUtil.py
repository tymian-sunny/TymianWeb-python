from __future__ import annotations

import html
import json
import re
import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

# 已知的url匹配值, 用于对破以后的部分乱码做正则匹配还原
known_domains = {
    "-hot.com": "https://vip.dytt-hot.com",
    "eimg.com": "https://p16-va-tiktok.ibyteimg.com",
    "nema.com": "https://vip.dytt-cinema.com"
}

# 破译play.js得到的值, 用于破译getVideoPlay方法中传入的uri
key = b"57A891D97E332A9D"
iv = b"8d312e8d3cde6cbb"

def search_video_url(url):
    """
    获取视频链接
    :return: 视频的完整链接
    """
    # 发送首页请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    r = requests.get("https://danmu.yhdmjx.com/m3u8.php?url=" + url, headers)
    html_text = r.text

    # 使用正则表达式提取 getVideoInfo() 中的字符串参数
    pattern = r'getVideoInfo\("([^"]+)"\)'
    match = re.search(pattern, html_text)

    if match:
        video_info_value = match.group(1)

        ciphertext = base64.b64decode(video_info_value)
        # 创建 AES-CBC 解密器
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # 解密并去除 PKCS7 填充
        decrypted = cipher.decrypt(ciphertext)
        plaintext = unpad(decrypted, AES.block_size)

        # 把Bytes编码为utf-8
        line = plaintext.decode("utf-8", errors="ignore")

        # 对解密出来的字符串做正则匹配和修复
        return parse_decrypted_url(line)

    else:
        return None
        # print("没有找到 getVideoInfo() 的参数")


def parse_decrypted_url(line: str) -> str | None:
    """
    从解密后的单条字符串中提取 完整链接。
    如果匹配不到有效地址，返回 原链接。
    """
    line = trim_before_com(line)

    match = re.search(r'([-a-z]+\.(?:com)/[^\s]+)', line)
    if not match:
        return None

    suffix = match.group(1)

    # 匹配后缀并还原完整 URL
    for key, domain in known_domains.items():
        if suffix.startswith(key):
            return domain + suffix[len(key):]

    return line  # 如果后缀不在已知映射中


def trim_before_com(input_str: str) -> str:
    """
    把解密出来的字符串前面的大量乱码去除, 方便做正则匹配
    :param input_str: 输入的字符串
    :return: 返回去除掉xxxx.com前面所有字符内容的字符串
    """
    idx = input_str.find('.com')
    if idx == -1 or idx < 4:
        return input_str  # 没找到 .com 或无法向前推 4 位，原样返回

    # 向前推 4 个字符的位置
    cut_pos = idx - 4
    return input_str[cut_pos:]


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
        """
        查找视频页链接
        :param episode:
        :param name:
        :param web:
        :return:
        """

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
            # 把拿到的页面地址去解析视频地址
            video_url = search_video_url(player_data.get("url"))

            result = {name: video_url}
            return result
        else:
            return None

