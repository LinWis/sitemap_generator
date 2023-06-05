import string
import time
from http.client import RemoteDisconnected
from urllib.error import URLError
from urllib.request import urlopen
from urllib.parse import urlparse, quote, urljoin, urldefrag
from urllib.request import Request
import threading

import lxml
from lxml import cssselect
from lxml.html.soupparser import fromstring


class RunCrawler(threading.Thread):

    def __init__(self, url: str, max_urls=5000):
        super().__init__()
        self.InitialURL = url
        self.url_queue = list()
        self.checked_url = set()
        self.active_urls = set()
        self.checked_url_tree = {}
        self.start_thread_count = len(threading.enumerate())
        self.max_urls = max_urls

        self.run_ini = time.time()
        self.run_end = None
        self.run_dif = None

    def get_dataset(self) -> dict:
        self.check_url(self.InitialURL)
        self.start()
        self.join()
        time.sleep(1)

        return self.checked_url_tree

    def url_queue_generator(self):
        index = 0
        while self.url_queue:
            n = self.url_queue.pop(0)
            yield index, n
            index += 1

    def run(self):
        while threading.active_count() > self.start_thread_count:
            for index, cur_url in self.url_queue_generator():
                if threading.active_count() < 300:
                    Crawler(index, cur_url, self)
                    self.active_urls.add(cur_url)
                    print('Threads: ', len(threading.enumerate()) - self.start_thread_count,
                          ' Queue: ', len(self.url_queue), ' Checked: ', len(self.checked_url))

            print("Waiting pls, some threads are still working")
            time.sleep(2)

            if threading.active_count() == 2 and len(self.url_queue) == 0:
                break
        self.done()

    def add_url_to_tree(self, url: str) -> None:

        url_dict = self.checked_url_tree
        url_parsed = urlparse(url)
        url_parse_arr = [url_parsed.netloc] + url_parsed.path.split('/')[1:]

        key = ""
        for url_piece in url_parse_arr:
            key = key + '/' + url_piece if url_piece != 0 else key + url_piece
            elem = url_dict.get(key)

            if elem is None:
                url_dict[key] = {}

            url_dict = url_dict[key]

    def check_url(self, url: str) -> None:
        if (url not in self.url_queue) and (url not in self.checked_url) and (self.InitialURL in url)\
                and (url not in self.active_urls) and (len(self.url_queue) < self.max_urls // 2)\
                and (len(self.checked_url) < self.max_urls // 2):
            quote_url = quote(url, safe=string.printable).replace(" ", "%20")
            self.url_queue.append(quote_url)
            self.add_url_to_tree(quote_url)

    def process_checked(self, url: str) -> None:
        if url not in self.checked_url:
            self.checked_url.add(url)

    def join_url(self, src: str, url: str) -> str:

        src_new_path = None
        url_new_path = None

        url_info = urlparse(url)
        src_info = urlparse(src)
        initial_url_info = urlparse(self.InitialURL)
        initial_url_base = quote((initial_url_info.scheme + '://' + initial_url_info.netloc + initial_url_info.path),
                                 safe=string.printable).replace(" ", "%20")

        if url_info.netloc == '' or url_info.netloc == initial_url_info.netloc:
            url_path = url_info.path
            src_path = src_info.path

            if url_info.query:
                url_path = url_path + '?' + url_info.query

            src_new_path = urljoin(initial_url_base, src_path)
            url_new_path = urljoin(src_new_path, url_path)

        return urljoin(src_new_path, url_new_path)

    def parse_thread(self, url: str, data: lxml.html) -> None:
        select = cssselect.CSSSelector("a")

        temp_links = [el.get('href') for el in select(data)]
        temp_links = temp_links[:1000]

        for temp_link in temp_links:

            path = self.join_url(url, temp_link)

            if path:
                self.check_url(path)

        try:
            self.active_urls.remove(url)
        except Exception:
            pass

    def get_info(self) -> list:
        return [self.InitialURL, self.run_dif, len(self.checked_url)]

    def done(self) -> None:
        print('Checked: ', len(self.checked_url))

        self.run_end = time.time()
        self.run_dif = self.run_end - self.run_ini

    def __repr__(self) -> str:
        return f"{self.__class__}: {self.InitialURL}"

    def __str__(self) -> str:
        return f"{self.InitialURL}"


class Crawler(threading.Thread):
    def __init__(self, index: int, crawl_url: str, main_crawler: RunCrawler):
        super().__init__()
        self.request_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Connection": "keep-alive"
        }

        self.main_crawler = main_crawler
        self.index = index
        self.crawl_url = crawl_url

        self.start()

    def run(self):

        try:
            print("processing: ", self.crawl_url)
            self.crawl_url, frag = urldefrag(self.crawl_url)
            url = quote(self.crawl_url, safe=string.printable).replace(" ", "%20")
            temp_req = Request(url, headers=self.request_headers)
            temp_res = urlopen(temp_req)

            temp_status = temp_res.getcode()

            if temp_status == 200 and 'text/html' in temp_res.info()["Content-Type"]:
                temp_content = temp_res.read()

                try:
                    temp_data = fromstring(temp_content)
                    temp_thread = threading.Thread(target=self.main_crawler.parse_thread,
                                                   args=(self.crawl_url, temp_data), daemon=True)
                    temp_thread.start()
                    temp_thread.join()
                except (RuntimeError, TypeError, NameError, ValueError):
                    print('Content could not be parsed.')

        except URLError as e:
            print('URLError: ', self.crawl_url, e)

        except RemoteDisconnected:
            print("RemoteDisconnect on this url: ", self.crawl_url)

        except Exception as e:
            print(f"Error on http client: {e}")

        self.main_crawler.process_checked(self.crawl_url)

    def __repr__(self) -> str:
        return f"{self.__class__}, Url: {self.crawl_url}, Index: {self.index}"

    def __str__(self) -> str:
        return f"Url: {self.crawl_url}, Index: {self.index}"


