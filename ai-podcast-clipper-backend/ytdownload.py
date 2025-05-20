from pytubefix import YouTube
from pytubefix.cli import on_progress


url1 = 'https://youtu.be/RtWAo00dqfo?si=zcbyNf2oKiDczqcn'
url2 = 'https://youtu.be/KyfUysrNaco?si=Yafbb9u-JJyck03W'

yt = YouTube(url2, on_progress_callback=on_progress)
print(yt.title)

ys = yt.streams.get_highest_resolution()
ys.download()

