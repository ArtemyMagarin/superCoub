from skimage.filter import gaussian_filter
from moviepy.editor import VideoFileClip


clip = VideoFileClip("my_video.mp4")
clip_blurred = clip.fl_image( blur )


class Coub:
    def __init__(self, data):
        self.data = data
        
        d = self.data["file_versions"]["html5"]
        videoUrl = d["video"]["high"]["url"] if 'high' in d["video"] else d["video"]["med"]["url"]
        audioUrl = d["audio"]["high"]["url"] if 'high' in d["audio"] else d["audio"]["med"]["url"]
        
    
    
    def _blur(self, image):
        """ Returns a blurred (radius=2 pixels) version of the image """
        return gaussian_filter(image.astype(float), sigma=2)
    
    def getVideo(self):
        pass

    def doSize(self):
        self.video.resize(height=720)

        backVideo = self.video.copy()
        backVideo = backVideo.fl_image( self._blur ).resize(width=1280)

        self.video = CompositeAudioClip(backVideo, self.video ).margin(3)
    

class Project:
    def __init__(self):
        pass

    def render(self):
        pass
    
    



def getCoubsByCategory(url):
    r = requests.get('https://coub.com/api/v2/timeline/rising/'+url)
    permalinks = []
    for i in r.json()['coubs']:
        permalinks.append(i['permalink'])
    return permalinks