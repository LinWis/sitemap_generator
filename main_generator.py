from datetime import date

from prettytable import PrettyTable

from sitemap import Sitemap
from crawlers import RunCrawler
from db_connect import MyDbPostgreSql
from sitemap_visualizer import VisualizerSitemap

if __name__ == "__main__":
    my_db = MyDbPostgreSql(password="", db_name="postgres")
    my_db.create_table('sitemaps',
                       '(id SERIAL PRIMARY KEY, site_url TEXT,'
                       ' processing_time_ms INT, checked_urls INT,'
                       ' result_filename TEXT, time_created TEXT)')

    urls = ['https://crawler-test.com/']

    info_table = PrettyTable()
    info_table.field_names = ['URL сайта', 'Время обработки', 'Кол-во ссылок', "Имя файла с картой"]

    for InitialURL in urls:

        main_crawler = RunCrawler(InitialURL)
        dataset = main_crawler.get_dataset()
        info = main_crawler.get_info()
        filename = InitialURL.split('/')[2]

        sitemap = Sitemap(data_set=dataset, filename=filename + ".xml")
        sitemap.generate_sitemap()

        info = info + sitemap.get_info()

        info_table.add_row([info[0], info[1], info[2], info[3]])

        my_db.insert('sitemaps', site_url=info[0],
                     processing_time_ms=int(info[1]), checked_urls=info[2],
                     result_filename=info[3], time_created=date.today())

        sitemap_visual = VisualizerSitemap(filename=filename + ".png")
        sitemap_visual.start_visualizer(dataset)

    print(info_table)

