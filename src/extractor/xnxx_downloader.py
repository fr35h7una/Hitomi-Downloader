import downloader
from utils import Soup, cut_pair, urljoin, Downloader, LazyUrl, compatstr
import ree as re
import m3u8
from m3u8_tools import M3u8_stream, playlist2stream
from timee import sleep
from fucking_encoding import clean_title
import os
from io import BytesIO as IO



class Video(object):

    def __init__(self, url, url_page, title, url_thumb, format='title'):
        self._url = url
        self.url = LazyUrl(url_page, self.get, self)
        self.id = get_id(url_page)
        ext = '.mp4'
        self.title = title = clean_title(title)
        format = format.replace('title', '###title').replace('id', '###id')
        title = format.replace('###title', title).replace('###id', (u'{}').format(self.id))
        self.filename = (u'{}{}').format(title, ext)
        f = IO()
        self.url_thumb = url_thumb
        downloader.download(url_thumb, buffer=f)
        self.thumb = f

    def get(self, _):
        return self._url


def get_id(url):
    return url.split('xnxx.com/')[1].split('/')[0]


@Downloader.register
class Downloader_xnxx(Downloader):
    type = 'xnxx'
    URLS = ['xnxx.com']
    single = True

    def init(self):
        self.url = self.url.replace('xnxx_', '')

    @property
    def id(self):
        return get_id(self.url)

    def read(self):
        format = compatstr(self.ui_setting.youtubeFormat.currentText()).lower().strip()
        video = get_video(self.url, format)
        self.urls.append(video.url)
        self.setIcon(video.thumb)
        self.title = video.title
        

def get_video(url, format='title'):
    html = downloader.read_html(url)
    soup = Soup(html)

    for script in soup.findAll('script'):
        script = script.text or script.string or ''
        hls = re.find(r'''html5player\.setVideoHLS\(['"](.+?)['"]''', script)
        if hls:
            break
    else:
        raise Exception('No VideoHLS')

    video = playlist2stream(hls)

    title = get_title(soup)

    url_thumb = soup.find('meta', {'property': 'og:image'}).attrs['content'].strip()
    
    video = Video(video, url, title, url_thumb, format)
    return video


def get_title(soup):
    return soup.find('meta', {'property': 'og:title'}).attrs['content'].strip()

