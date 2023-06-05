from pprint import pprint
import email.utils as eut
from lxml import etree


class Sitemap:
    def __init__(self, data_set=None, xmnls='https://www.testsitemap.org/schemas/sitemap/1',
                 url_set=None, encoding='utf-8', filename='xml/sitemap.xml'):

        self.url_set = url_set
        self.xmlns = xmnls
        self.encoding = encoding
        self.filename = filename
        self.data_set = data_set

    def generate_sitemap(self) -> None:

        print('Running XML Generator...')

        self.create_xml()
        self.write_xml()

    def create_xml(self) -> None:
        self.url_set = etree.Element('url_set')
        self.url_set.attrib['xmlns'] = self.xmlns
        self.url_set = self.create_url_set(self.data_set, self.url_set)

    def write_xml(self) -> None:
        f = open(self.filename, 'w', encoding='utf-8')

        print(etree.tostring(self.url_set, pretty_print=True, encoding="utf-8", method="xml").decode('utf-8'), file=f)
        f.close()

        print('Sitemap saved in: ', self.filename)

    def get_info(self) -> list:
        return [self.filename]

    @staticmethod
    def format_data(datetime: str) -> str:
        datearr = eut.parsedate(datetime)
        date = None

        try:
            year = str(datearr[0])
            month = str(datearr[1])
            day = str(datearr[2])

            if int(month) < 10:
                month = '0' + month

            if int(day) < 10:
                day = '0' + day

            date = year + '-' + month + '-' + day
        except IndexError:
            pprint(datearr)

        return date

    @staticmethod
    def create_url_set(init_dict: dict, url_set: etree) -> etree:
        for key, val in init_dict.items():
            url = etree.Element('url')
            url.attrib['href'] = key

            url = Sitemap.create_url_set(init_dict[key], url)
            url_set.append(url)

        return url_set

    def __str__(self):
        return f"sitemap: {self.filename}"
