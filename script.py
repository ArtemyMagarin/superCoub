from os import remove
import random
import string
import datetime
import requests

from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from skimage.filters import gaussian as gaussian_filter


def getFile(url):
    r = requests.get(url)
    blob = bytearray(r.content)

    if url[-1] == "4":
        blob[0] = 0
        blob[1] = 0
    
    return (blob, getName(url[-3:]))


def getName(ext, id=None):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    randStr = ''.join(random.choice(chars) for _ in range(6)) if id==None else id
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

    try:
        videoUrl = data["video"]["high"]["url"] if 'high' in data["video"] else data["video"]["med"]["url"]
        audioUrl = data["audio"]["high"]["url"] if 'high' in data["audio"] else data["audio"]["med"]["url"]
    except KeyError:
        return False

    video, videoName = getFile(videoUrl)
    audio, audioName = getFile(audioUrl)

    saveBinaryFile(videoName, video)
    saveBinaryFile(audioName, audio)

    videoclip = VideoFileClip(videoName)
    audioclip = AudioFileClip(audioName)

    videoclip = normalize(videoclip)
    videoclip = videoclip.set_audio(audioclip.subclip(0, videoclip.duration))

    garbage.append(videoName)
    garbage.append(audioName)

    return videoclip

def _blur(image):
    """ Returns a blurred (radius=2 pixels) version of the image """
    return gaussian_filter(image.astype(float), sigma=8)


def normalize(v):

    w, h = v.size
    
    if w==1280 and h==720:
        return v 

    if not (1280/w==1280//w and 720/h==720//h):
        backVideo = v.copy()
        backVideo = backVideo.fl_image(_blur)

        backVideo = backVideo.resize(width=1280, height=h*1280/w)

        nw = w*(720/h)
        nh = 720

        if nw > 1280:
            nh = 720*1280/nw
            nw = 1280
        v = v.set_pos('center').resize(width=nw, height=nh)

        if h/w >= 1:
            v = CompositeVideoClip([backVideo, v], size=(1280, 720))
        else:
            v = CompositeVideoClip([v,], size=(1280, 720))
    else:
        v = v.set_pos('center').resize(width=w*(720/h), height=h*(720/h))
    return v


def concatAndSaveVideo(idArr):
    videoclips = []
    delNames = []

    for id in idArr:
        video = getVideo(id)
        if video:
            video.write_videofile(getName('mp4', id))
        else:
            print('https://coub.com/view/'+id)


def getPermalinksByCategory(url):
    r = requests.get('https://coub.com/api/v2/timeline/hot/'+url)

    permalinks = []
    for i in r.json()['coubs']:
        permalinks.append(i['permalink'])


    return permalinks


def main():
    r = requests.get('http://localhost:8000/hot/all?period=weekly').json()
    print('>>> I going to work with', r['count'],'videos, duration =', r['duration'],'\n\n' )

    permalinks = r['permalinks']
    concatAndSaveVideo(permalinks)

    

if __name__ == '__main__':
    garbage = []
    main()
    for i in garbage:
        remove(i)

# ffmpeg -f concat -safe 0 -i <(for f in *mp4; do echo "file '$PWD/$f'"; done) -c copy output.mp4
