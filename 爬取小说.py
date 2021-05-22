import time
import requests
import _thread
from bs4 import BeautifulSoup
from urllib import parse

novel = ''
server = ''
_1st_chapter_index = 12
ads_end_index = 0
f = ''
contents = 0
flag = 1
count = 0
total_nums = 1
texts = []

time_old = 0
each_time = 0

NAME = 0
URL = 1


def init():
    global ads_end_index, f, server, novel
    novel = input('请输入要爬取的小说:')
    url_code = parse.quote(novel, encoding='gbk')
    origin_url = 'https://www.qqxsw.la/modules/article/search.php?searchkey=' + url_code
    req = requests.get(origin_url)
    redirect_url = req.url
    if 'search.php?' in redirect_url:
        r = requests.get(redirect_url)
        html = r.text
        bf = BeautifulSoup(html, features="lxml")
        div = bf.find('span', class_="s2")
        if not div:
            print('请稍后再试!')
            exit(0)
        bf = BeautifulSoup(str(div), features="lxml")
        a = bf.find('a')
        server = a.get('href')
    else:
        server = redirect_url
    ads_end_index = len('千千小说网 www.qqxsw.la，最快更新 ！' + novel)
    f = open(novel + '.txt', 'w', encoding='utf-8')


def get_contents(server):
    r = requests.get(server)
    html = r.text
    div_bf = BeautifulSoup(html, features="lxml")
    div = div_bf.find_all('div', id='list')
    a_bf = BeautifulSoup(str(div[0]), features="lxml")
    a = a_bf.find_all('a')
    urls = [(each.string, server + each.get('href')) for each in a[_1st_chapter_index:]]
    return urls


def get_texts(url):
    r = requests.get(url)
    html = r.text
    bf = BeautifulSoup(html, features="lxml")
    texts = bf.find_all('div', id='content')
    texts = texts[0].text.replace('\xa0\xa0\xa0\xa0', '\n\n')
    return texts[ads_end_index:]


def write(title, text):
    f.write('\t' + title + text + '\n\n\n\n')


def crawling():
    global count, total_nums, flag, contents
    contents = get_contents(server)
    total_nums = len(contents)
    urls = [content[URL] for content in contents]

    # 爬取部分
    for url in urls:
        # 计算剩余下载时间
        global each_time, time_old
        t = time.perf_counter()
        each_time = t - time_old
        time_old = t

        texts.append(get_texts(url))
        count += 1
    else:
        flag = 0


def to_time(each):
    if each > 2:
        return '——'
    seconds = each_time * (total_nums - count)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


if __name__ == '__main__':
    init()
    _thread.start_new_thread(crawling, ())
    print('《{}》下载中！'.format(novel))
    j = 0
    while flag:
        while j < count:
            write(contents[j][NAME], texts[j])
            j += 1
        print("\r  已下载:{:.2f}%    剩余时间:{}".format(100 * float(j / total_nums),
              to_time(each_time)), end='')
        time.sleep(1)
    print('《{}》下载完成！'.format(novel))
