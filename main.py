import urllib.parse
from tkinter import *
import pandas as pd

import requests
import json
from bs4 import BeautifulSoup


result = {}


def btn_click(event=None):
    global result, label

    text = entry.get()
    result = scrape_data(text)
    output = dict_to_output(result)
    label.config(text=output)
    label.pack(anchor='w')


def save_click():
    global label

    if len(result) == 0:
        text = "There is nothing to scrape!"
    else:
        file_name = save_data(result)
        text = 'data saved in file "' + file_name + '"!'
    label.config(text=text, justify=LEFT)


def save_data(data: dict):
    file_name = "data_" + data['title']
    for i in ['\\', '/', ':', '*', '"', '<', '>', '|', '+', '?']:
        file_name = file_name.replace(i, "")
    file_name = file_name.strip() + ".xlsx"
    df = pd.DataFrame(list(data.items()), columns=['key', 'value'])
    df.to_excel(file_name)
    return file_name


def scrape_data(request: str):
    video_url = get_video_url(request)
    video_data = get_data(video_url)
    result = get_video_data(video_data)
    return result


def get_data(url):
    request = url
    r = requests.get(request)
    soup = BeautifulSoup(r.content, 'html.parser')
    video_info = soup.find_all('script')[18].text[30:-1]
    video_data = json.loads(video_info)

    # channel_info = soup.find_all('script')[43].text[20:-1]
    # channel_data = json.loads(channel_info)
    return video_data


def get_video_data(video_data):
    info = video_data['videoDetails']

    title = info['title']
    video_id = info['videoId']
    views = video_data['microformat']['playerMicroformatRenderer']['viewCount']
    length = info['lengthSeconds']
    channel_id = info['channelId']
    short_description = info['shortDescription']
    channel_nick = info['author']
    channel_name = video_data['microformat']['playerMicroformatRenderer']['ownerChannelName']

    result = {
        'title': title,
        'video_id': video_id,
        'views': views,
        'length': length + " sec",
        'channel_id': channel_id,
        # 'description': short_description,
        'channel_nick': channel_nick,
        'channel_name': channel_name
    }
    return result


def get_video_url(request: str):
    request = 'https://www.youtube.com/results?search_query=' + urllib.parse.quote(request.encode('utf8')) + \
              '&sp=EgIQAQ%253D%253D'
    r = requests.get(request)
    soup = BeautifulSoup(r.content, 'html.parser')
    script = soup.find_all('script')[33].text[20:-1]
    data = json.loads(script)
    return 'https://www.youtube.com/watch?v=' + \
           data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'] \
               [0]['itemSectionRenderer']['contents'][2]['videoRenderer']['videoId']


def dict_to_output(dictionary: dict):
    output = ''
    for key, item in dictionary.items():
        output += key + ": " + item + '\n'
    return output


if __name__ == '__main__':
    window = Tk(className='Youtube Scraper')
    window.geometry("400x300")

    entry = Entry(width=30)
    entry.pack()

    btn = Button(text='scrape', command=btn_click, height=1, width=15)
    btn.pack()
    window.bind('<Return>', btn_click)

    btn = Button(text='save', command=save_click, height=1, width=15)
    btn.pack()

    label = Label(text="Let's scrape!")
    label.pack()

    window.mainloop()
