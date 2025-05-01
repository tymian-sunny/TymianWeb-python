from asyncio import threads
from threading import Thread

from controller.SearchController import SearchController
from entity.Mxdm6 import Mxdm6
from util.SearchUtil import SearchUtil
import concurrent.futures

def get_url_thread(episodes):
    """
    多线程获取播放链接
    :param episodes:{'/dongmanplay/7912-1-1.html':'播放凡人修仙传重制版第01集','/dongmanplay/7912-1-1.html':'播放凡人修仙传重制版第10集'...}
    :return:
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for url, name in episodes.items():
            t = executor.submit(util.search_url, url, name, mxdm6)
            to_do.append(t)
        for thread in concurrent.futures.as_completed(to_do):
            yield thread.result()


def get_episode_thread(hrefs):
    """
    多线程获取播放列表
    :param hrefs:
    :return:
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        to_do = []
        for key, value in hrefs.items():

            t =  executor.submit(util.search_episode,key, mxdm6)
            to_do.append(t)
            # t.start()
        for thread in concurrent.futures.as_completed(to_do):
            for key in thread.result():
                for result in get_url_thread(thread.result()[key]):
                    yield result


def get_anime():
    util = SearchUtil()
    mxdm6 = Mxdm6()

    # 获取搜索结果
    hrefs = util.search_entry("凡人", mxdm6)
    for data in get_episode_thread(hrefs):
        yield data

if __name__ == '__main__':
    util = SearchUtil()
    mxdm6 = Mxdm6()

    # 获取搜索结果
    # hrefs = util.search_entry("凡人", mxdm6)
    # for data in get_episode_thread(hrefs):
    #     print(f"返回数据: {data}")

    searchController = SearchController()

    for data in searchController.get_anime():
        print(data)

    # print(searchController.get_anime())