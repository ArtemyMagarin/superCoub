import requests
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
# from skimage.filter import gaussian_filter
from skimage.filters import gaussian as gaussian_filter

import datetime
import string
import random
from os import remove
import re

def getFile(url):
    r = requests.get(url)
    blob = bytearray(r.content)

    if url[-1] == "4":
        blob[0] = 0
        blob[1] = 0
    
    return (blob, getName(url[-3:]))


def getName(ext):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    randStr = ''.join(random.choice(chars) for _ in range(6))
    res = '{day}_{month}_{year}_{hours}_{minutes}_{name}.{ext}'.format(
        name=randStr,
        day=datetime.datetime.today().day,
        month=datetime.datetime.today().month,
        year=datetime.datetime.today().year,
        hours=datetime.datetime.today().hour,
        minutes=datetime.datetime.today().minute,
        ext=ext
    )

    return res


def saveBinaryFile(name, file):
    with open(name, 'wb') as f:
        f.write(file)


def getVideo(id):
    url="http://coub.com/api/v2/coubs/"+str(id)
    r = requests.get(url)
    data = r.json()["file_versions"]["html5"]

    videoUrl = data["video"]["high"]["url"] if 'high' in data["video"] else data["video"]["med"]["url"]
    audioUrl = data["audio"]["high"]["url"] if 'high' in data["audio"] else data["audio"]["med"]["url"]

    video, videoName = getFile(videoUrl)
    audio, audioName = getFile(audioUrl)

    saveBinaryFile(videoName, video)
    saveBinaryFile(audioName, audio)

    videoclip = VideoFileClip(videoName)
    audioclip = AudioFileClip(audioName)
    
    name = getName('mp4')

    audioclip = audioclip.subclip(0, videoclip.duration)
    videoclip = videoclip.set_audio(audioclip)
    print(videoclip.audio)
    # videoclip.
    return videoclip

    # videoclip.write_videofile(name)

    # remove(videoName)
    # remove(audioName)

    return name

def _blur(image):
    """ Returns a blurred (radius=2 pixels) version of the image """
    return gaussian_filter(image.astype(float), sigma=8)


def normalize(v):


    backVideo = v.copy()
    backVideo = backVideo.fl_image(_blur).resize(width=1280, height=720)

    w, h = v.size


    v = v.set_pos('center').resize(width=w*(720/h), height=h*(720/h))
    v = CompositeVideoClip([backVideo, v], size=(1280, 720))
    return v


def concatAndSaveVideo(idArr):
    videoclips = []
    delNames = []

    for id in idArr[:3]:
        video = getVideo(id)
        # v = VideoFileClip(videoName)
        v = normalize(video)
        videoclips.append(v)

    name = getName('mp4')

    final_clip = concatenate_videoclips(videoclips)
    final_clip.write_videofile(name)

    for i in delNames:
        remove(i)

    return name

def getPermalinksByCategory(url):
    r = requests.get('https://coub.com/api/v2/timeline/rising/'+url)

    permalinks = []
    for i in r.json()['coubs']:
        permalinks.append(i['permalink'])
    return permalinks


def main():
    permalinks = getPermalinksByCategory('animals-pets')

    print(concatAndSaveVideo(permalinks[0:4]))


if __name__ == '__main__':
    main()

# with open('file2.mp4', 'wb') as f:
#     f.write(getVideo('kc0q'))


# clip1 = VideoFileClip("file1.mp4")
# clip2 = VideoFileClip("file2.mp4")

# final_clip = concatenate_videoclips([clip1,clip2])
# final_clip.write_videofile("my_concatenation.mp4")