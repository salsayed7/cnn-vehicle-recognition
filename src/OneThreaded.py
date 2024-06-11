import sys
import argparse
import cv2
import math
import os
import tqdm

def extractFrames(pathIn, pathOut, every=1):
    """
    Extract frames from a video using OpenCVs VideoCapture
    :param pathIn: path of the video
    :param pathOut: the directory to save the frames
    :param name: name of video file (exported frames name)
    :param every: frame spacing
    """

    capture = cv2.VideoCapture(pathIn)
    fps = capture.get(cv2.CAP_PROP_FPS)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    length = total_frames/fps
    total_count = total_frames
    name = os.path.splitext(os.path.basename(pathIn))[0]
    os.makedirs(os.path.join(pathOut, name), exist_ok=True)
    
    success, image = capture.read()
    success = True

    print("Video frames:", total_frames)
    print("Video fps:", fps)
    print("Video length (seconds):", length)

    frame = 0
    saved = 0
    for i in tqdm.notebook.trange(math.floor(total_count/math.floor(every))):
        capture.set(cv2.CAP_PROP_POS_MSEC,(i*1000))
        success,image = capture.read()
        if not success: continue
        if image is None: continue
        if frame%every==0:
            saved+=1
            cv2.imwrite(pathOut + "\\"+ name + "\\" + name + "_{:06d}.jpg".format(saved), image)
        frame+=1
    capture.release()
    return total_frames/every
