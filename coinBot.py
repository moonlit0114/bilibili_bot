import requests
import time
import logging
import random




class BilibiliCoinBot:
    PAGE_API_URL = "https://api.bilibili.com/x/space/wbi/arc/search"
    COIN_API_URL = "https://api.bilibili.com/x/web-interface/coin/add"
    VIDEO_URL_TMPL = "https://www.bilibili.com/video/av{}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Host": "api.bilibili.com",
        "Cache-Control": "no-cache",
        "Proxy-Connection": "keep-alive",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": "https://www.bilibili.com",
    }

    def __init__(self, up_uid: str, cookies: dict) -> None:
        self.up_uid = up_uid
        self.session = requests.Session()
        # self.session.cookies=cookies
        self.session.cookies.update(cookies)
        self.session.headers = self.HEADERS
        self.success_count=0
        self.failed_count=0
        self.coined_count=0

    def clean(self):
        self.success_count=0
        self.failed_count=0
        self.coined_count=0

    def sleep(self):
        sleep_time = random.random() * 5
        logging.info("sleep time: {}s".format(sleep_time))
        time.sleep(sleep_time)

    def coining(self, video_info: dict):
        aid = video_info["aid"]
        headers = {"Referer": self.VIDEO_URL_TMPL.format(aid)}
        data = {
            "aid": aid,
            "multiply": 2,
            "select_like": 1,
            "cross_domain": True,
            "csrf": self.session.cookies["bili_jct"],
            # "eab_x": 2,
            # "ramval": 0,
            # "source": "web_normal",
            # "ga": 1,
        }
        response = self.session.post(
            self.COIN_API_URL,
            headers=headers,
            data=data,
        )
        response.raise_for_status()
        resp_data = response.json()
        
        match  resp_data["code"]:
            case 0:
                self.success_count+=1
            case 34005:
                self.coined_count+=1
            case _:
                self.failed_count+=1

        if resp_data["code"] == 0:
            logging.info("投币成功, aid:{}, title:{} ".format(aid, video_info["title"]))
        else:
            logging.info("投币失败, aid:{}, title:{}, msg: {}".format(aid, video_info["title"],resp_data["message"]))

    def get_video_page(self, page: int) -> list:
        params = {"mid": self.up_uid, "pn": page}
        response = self.session.get(self.PAGE_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data["code"] != 0:
            logging.error(
                "get video page error, code: {}, message: {}".format(
                    data["code"], data["message"]
                )
            )
            return
        logging.info("get video page success, page:{}".format(page))
        page_data=data["data"]["list"]["vlist"]
        page_info=data["data"]["page"]
        for video_info in page_data:
            yield video_info
        
        if page_info["pn"]*page_info["ps"] >= page_info["count"]:
            yield False
        return


    def get_video(self, start_page=1) -> list:
        page = start_page
        while True:
            for video_info in self.get_video_page(page):
                if not video_info:
                    return
                yield video_info
            page += 1
        

    def run(self):
        self.clean()
        try:
            for video_info in self.get_video():
                self.coining(video_info)
                self.sleep()
        except Exception as e:
            logging.exception(e)
        
        logging.info("投币成功:{}次, 投币失败:{}次, 已投币:{}次".format(self.success_count, self.failed_count, self.coined_count))


