import json
from asyncio import threads
from threading import Thread
from entity.Mxdm6 import Mxdm6
from util.SearchUtil import SearchUtil
import concurrent.futures

class SearchController:

    def __init__(self):
        self.util = SearchUtil()
        self.mxdm6 = Mxdm6()

    def get_url_thread(self,episodes):
        """
        多线程获取播放链接
        :param episodes:{'/dongmanplay/7912-1-1.html':'播放凡人修仙传重制版第01集','/dongmanplay/7912-1-1.html':'播放凡人修仙传重制版第10集'...}
        :return:
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for url, name in episodes.items():
                t = executor.submit(self.util.search_url, url, name, self.mxdm6)
                to_do.append(t)
            for thread in concurrent.futures.as_completed(to_do):
                yield thread.result()


    def get_episode_thread(self,hrefs):
        """
        多线程获取播放列表
        :param hrefs:
        :return:
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            to_do = []
            for key, value in hrefs.items():

                t =  executor.submit(self.util.search_episode,key, self.mxdm6)
                to_do.append(t)
                # t.start()
            for thread in concurrent.futures.as_completed(to_do):
                for key in thread.result():
                    for result in self.get_url_thread(thread.result()[key]):
                        yield {key:result}


    def get_anime(self, name):
        util = SearchUtil()
        mxdm6 = Mxdm6()

        # 获取搜索结果
        hrefs = util.search_entry(name, mxdm6)
        for data in self.get_episode_thread(hrefs):
            json_str = json.dumps(data, ensure_ascii=False)
            yield f"data: {json_str}\n\n"
            # yield data
