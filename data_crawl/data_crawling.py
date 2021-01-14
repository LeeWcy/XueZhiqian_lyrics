"""
爬取网易云音乐的歌词
Step1：获取歌手专辑id信息
Step2：根据专辑id获取这张专辑中包含的歌曲id
Step3：根据歌曲id爬取歌词
"""

import requests
import lxml.etree as etree
import os
import json
import re


def get_album_links(url, album_headers, f_path):
    """
    获取专辑名称和专辑id，将其存储到文件中，并调用get_lyrics_list()函数
    :param html:
    :return:
    """
    album_ids = []

    # 获取专辑名称数据
    response_albums = requests.get(url, headers=album_headers)
    pattern = re.compile(r'<div class="u-cover u-cover-alb3" title=(.*?)>')
    titles = re.findall(pattern, response_albums.text)

    # 判断是否文件已存在，若存在则删除
    if os.path.exists(f_path + "AlbumInfo.txt"):
        os.remove(f_path + "AlbumInfo.txt")
    if os.path.exists(f_path + "lyricsList.txt"):
        os.remove(f_path + "lyricsList.txt")

    # 获取专辑id并存储数据
    with open(f_path + "AlbumInfo.txt", 'a', encoding='utf8') as f:
        for title in titles:
            # 替换掉双引号，避免对正则化解析出现干扰
            title_handle = title.replace('\"', '')
            id_elem = re.compile(r'<a href="/album\?id=(.*?)" class="tit s-fc0">%s</a>' % title_handle)
            album_id = re.findall(id_elem, response_albums.text)  # 获取专辑id
            if len(album_id) == 1:
                f.write(title + "\t" + str(album_id[0]) + "\n")  # 追加写入文件
                album_ids.append(album_id[0])
            elif len(album_id) == 0:
                print("无对应的id")
            else:
                print("出错错误，一个专辑title对应多个id::", title)
    f.close()
    print("专辑爬取成功")
    return album_ids


def get_lyrics_list(album_ids, lyrics_list_url_current, lyrics_list_headers, f_path):
    """
    通过专辑的id获取每张专辑的歌曲及歌曲id
    :param album_links: 专辑ids
    :param lyricsList_url_row:
    :param lyrics_list_headers:
    :return:
    """
    with open(f_path + "lyricsList.txt", 'a', encoding='utf-8') as f:
        for album_id in album_ids:
            url = lyrics_list_url_current + str(album_id)
            print("url is::", url)
            response_lyrics_list = requests.get(url, headers=lyrics_list_headers)
            html_lyrics_list = etree.HTML(response_lyrics_list.text)
            lyric_list = html_lyrics_list.xpath('//ul[@class="f-hide"]//a')

            for lyric in lyric_list:
                html_data = str(lyric.xpath('string(.)'))
                # 获取歌曲的id
                pattern = re.compile(r'<a href="/song\?id=(\d+?)">%s</a>' % html_data)
                items = re.findall(pattern, response_lyrics_list.text)
                if len(items) == 1:
                    f.write(html_data + "\t" + str(items[0]) + "\n")
                elif len(items) == 0:
                    print("无歌曲id")
                else:
                    print("出现错误，一首歌曲的title对一个多个id::", html_data)
                print("歌曲::%s, 歌曲ID::%s 写入文件成功" % (html_data, items))
    f.close()


def get_lyrics(lyrics_headers, f_path):
    """
    通过歌曲id获取歌词
    :param lyrics_headers: 头文件
    :return:
    """
    # 直接读取所有内容
    with open(f_path + 'lyricsList.txt', 'r', encoding='utf8') as f:
        list_of_line = f.readlines()
    count = 1
    for elem in list_of_line:
        song_name = elem.split('\t')[0]
        song_id = elem.split('\t')[1]
        url = "http://music.163.com/api/song/lyric?" + "id=" + str(song_id) + '&lv=1&kv=1&tv=-1'
        response = requests.get(url, headers=lyrics_headers)   # ,headers=lyrics_headers
        json_content = json.loads(response.text)
        print(json_content)
        # try:
        lyric = json_content['lrc']['lyric']
        pattern = re.compile(r'\[.*\]')
        lrc = str(re.sub(pattern, "", lyric).strip())

        with open(f_path + "歌曲名-" + song_name + ".txt", 'w', encoding='utf-8') as w:
            w.write(lrc)
            w.close()
        count += 1
        # except:
        # print("歌曲有错误，歌名为：%s。" % song_name)
    print("共爬取歌曲数量为：%s" % count)


if __name__ == '__main__':
    # 存储路径
    f_path = "./lyrics_zhiqian_xue/"
    if not os.path.exists(f_path):
        os.mkdir(f_path)

    # 专辑地址和headers
    singer_id = 5781  # 歌手id，可以在网易云音乐网站上搜索自己喜欢歌手的ID
    album_url = "https://music.163.com/artist/album?id=" + str(singer_id) + "&limit=100&offset=0"
    album_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': 'NMTID=00OSfG5gT8dvZVwDEUuu6W7dVMtDhcAAAF1_-_WXQ; _ntes_nnid=6e921bbcccec6f065285525f43cc4f0a,1606316710137; _ntes_nuid=6e921bbcccec6f065285525f43cc4f0a; _iuqxldmzr_=32; JSESSIONID-WYYY=Wf7F%2BVPhF0ytWdV2B95wxMNXtyBIBiSKS80Xs5FExqo17fg9JvVjG161eVGxhCrfFVCqlWThZE%5CZH76I7Ud2%2FpbF4RuTO808mgtzls7ieOuZaFsYpVlKQRxONQpEsUY3QjgrmlPe9RGvc0olV4NF%2BMtSAe1Msm7BCa0hhpnrQW3rbv%2Bk%3A1610283742851; WEVNSM=1.0.0; WNMCID=srrrqp.1610281943362.01.0; WM_NI=vSP7b9OczxC0nKfBQl%2FhUFDiuzlZMn4A4JdKWsSM2U4D5r8j72WKaVhtlYgwh8ad6TiBmC4pUKcGYWLnDKb1kBaqGeCHmiS2pF7B6Y9MoWCkYXjxhodsaBBNj1xltkdxekU%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeb0c170bcedf792f225f59a8ea2c14e879a9babb66ba7a7a9afcc499296bda8c72af0fea7c3b92ab68da0d8e1338dbdb699c23cae95aaa3d468edb89ba7c763b7a6a4bbd066f89ffcabe74195ad9daeb15ff89cfb93bb62f5ee99ace45eacaca4bae67dace8af85b560ab9ea3a4b77c9795ada8dc5d90b28cace13ba99eaf92c66f8198a38ad23ab49af9a3b553fb93a1b8c2619b88a699eb65a8adafa3c146aaefb88df761a8a8ab8cd837e2a3; WM_TID=9l%2F1Tcbiys5FBRVRUBJ%2Fee21dMWQd9TS',
        'Host': 'music.163.com',
        'Referer': 'https://music.163.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    # 获取所有专辑的地址
    album_ids = get_album_links(album_url, album_headers, f_path)

    # 专辑主页，专辑详情页面的headers和专辑list页面的headers一样
    lyrics_list_url_current = "http://music.163.com/album?id="
    get_lyrics_list(album_ids, lyrics_list_url_current, album_headers, f_path)

    # 获取歌词的API的headers
    lyrics_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    get_lyrics(lyrics_headers, f_path)
