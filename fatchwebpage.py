# -*- coding: utf-8 -*-
"""

"""
import urllib
import re
import os
from bs4 import BeautifulSoup
#beautifulsoup方法，第三方库的方法，爬找网页
## 下载网页
_DEBUG = False


def get_html_info(url):
    '''
    @url:需要下载的网址
    下载网址
    '''
    html = urllib.request.urlopen(url)
    html_info = html.read()# .decode('utf-8')  # 转码
    html.close()  # 记得要将打开的网页关闭，否则会出现意想不到的问题
    if(_DEBUG):
        print (type(html_info))
    return html_info


def redirect_html_content(html_info, content):
    '''
    @html_info:已经获取的网页的二进制内容
    调整网页内容，重定向目录
    '''
    info_str = str(html_info, encoding="utf-8")
    for link in content:
        l = link['href']
        l = l[22:]
        info_str = info_str.replace(l, link['link'])

    return bytes(info_str, encoding='utf-8')


def parse_page(html_info):
    '''
    @html_info:已经获取的网页的二进制内容
    利用Soup第三方库实现抓取，生成soup对象
    '''
    soup = BeautifulSoup(html_info, 'html.parser')  # 设置解析器为“lxml”
    return soup


def get_image(folder, soup):
    '''
    @folder:保存图片的文件夹名称
    @soup:soup对象
    利用soup对象提取图片并保存
    '''
    old_src = []
    new_src = []
    patt_and = re.compile(r'&+')
    patt_gif = re.compile(r'gif')

    all_image = soup.find_all('img')
    special_image = soup.find_all('img', height="200")
    normal_image = list(set(all_image) ^ set(special_image))
    
    if(_DEBUG):
        for i in normal_image:
            print(i)
        for i in special_image:
            print(i)

    x = 1
    for image in normal_image:
        print(image)
        old_src.append(image['src'])
        if re.search(patt_gif, image['src']):
            new_src.append("./" + folder + "/normal_%s.gif" % (x))
        else:
            new_src.append("./" + folder + "/normal_%s.jpg" % (x))
        
        urllib.request.urlretrieve(
            'https://www.zentao.net' + old_src[x - 1], new_src[x - 1])
        old_src[x - 1] = re.sub(patt_and, '&amp;', old_src[x - 1])
        x += 1
    y = 1
    for image in special_image:
        print(image)
        old_src.append(image['data-src'])
        if re.search(patt_gif, image['data-src']):
            new_src.append("./" + folder + "/specail_%s.gif" % (y))
        else:
            new_src.append("./" + folder + "/specail_%s.jpg" % (y))
        urllib.request.urlretrieve(
            'https://www.zentao.net' + old_src[x + y - 2], new_src[x + y - 2])
        y += 1

    return old_src, new_src


def redirect_html_image(html_info, source_image, local_image):
    '''
    @html_info:已经获取的网页的二进制内容
    @source_image:原始图片路径
    @local_image:本地图片路径
    调整网页内容，更换图片连接
    '''
    i = 0
    info_str = str(html_info, encoding="utf-8")
    for image in source_image:
        info_str = info_str.replace(image, local_image[i])
        i += 1
    return bytes(info_str, encoding='utf-8')


def save_html(file_name, html_info):
    '''
    @file_name:待写入的文件名称
    @html_info:已经获取的网页的二进制内容
    写入文件，采用二进制格式
    '''
    with open(file_name, "wb") as f:
        f.write(html_info)


def retrieve_output_path(Path):
    '''
    @Path:要保存图片的文件夹路径
    监测输出文件夹是否准备妥当
    '''
    if not os.path.exists(Path):
        os.mkdir(Path)
    return True


def has_class_but_no_id(tag):
    '''
    @tag:标签名称
    标签筛选方法
    '''
    return tag.name == 'dd' and tag.has_attr('class') and not tag.has_attr('id')


def has_id_but_no_class(tag):
    '''
    @tag:标签名称
    标签筛选方法
    '''
    return tag.name == 'dd' and tag.has_attr('id') and not tag.has_attr('class')


def generate_image_folder_name(url):
    '''
    @url:要抓取的网页url地址
    生成图片存储文件夹名称
    '''
    patt = re.compile(r'\W+')
    folder = re.sub(patt, '_', url)
    folder = folder[:-5]
    return folder

def get_content(soup):
    '''
    @soup:soup对象
    获取文章目录及连接
    '''
    content = []
    for tag in soup.find_all(href=re.compile("/book/zentaopmshelp/")):
        tmp = {}
        tmp['href'] = 'https://www.zentao.net' + tag['href']
        output_folder = generate_image_folder_name(tmp['href'])
        tmp['link'] = r'./' + output_folder + '.html'
        tmp['string'] = tag.string
        content.append(tmp)
    return content

def fetch_web_page(url, content, save_image=True):
    '''
    @url:要抓取的网页url地址
    @save_image:是否保存图片
    抓取单页面，并保存
    '''
    output_folder = generate_image_folder_name(url)
    html_file = output_folder + ".html"
    retrieve_output_path(output_folder)

    html_info = redirect_html_content(get_html_info(url), content)
    if save_image:
        soup = parse_page(html_info)
        old_src, new_src = get_image(output_folder, soup)
        info = redirect_html_image(html_info, old_src, new_src)
        save_html(html_file, info)
        
        if(_DEBUG):
            print(info)
            print(old_src)
            print(new_src)
    else:
        save_html(html_file, html_info)


def fetch_all(url_content):
    with open(url_content, "rb") as f:
        info = f.read()
        soup = parse_page(info)
        content = get_content(soup)
        
        for page in content:
            fetch_web_page(page['href'], content, save_image=False)

    
if __name__ == '__main__':
    url = "./content.html"
    fetch_all(url)
