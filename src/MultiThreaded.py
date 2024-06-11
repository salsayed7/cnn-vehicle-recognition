from concurrent.futures import ProcessPoolExecutor, as_completed
import cv2
import multiprocessing
import os
import sys
import math
import tqdm

def extractChunk(video_path, frames_dir, overwrite=False, every=1, start=-1, end=-1):
    """
    Extract frames from a video using OpenCVs VideoCapture
    :param video_path: path of the video
    :param frames_dir: the directory to save the frames
    :param total: total video frames count
    :param pbar: progress bar object
    :param overwrite: to overwrite frames that already exist?
    :param every: frame spacing
    :param start: start frame
    :param end: end frame
    :return: count of images saved
    """

    video_path = os.path.normpath(video_path)
    frames_dir = os.path.normpath(frames_dir)
    video_dir, video_filename = os.path.split(video_path)
    name = os.path.splitext(os.path.basename(video_filename))[0]
    assert os.path.exists(video_path)
    capture = cv2.VideoCapture(video_path)

    if start<0: start=0
    if end<0: end=int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    capture.set(1, start)
    frame=start
    while_safety=0
    saved_count=0
    
    while frame<end:
        _, image = capture.read()
        if while_safety > 500: break
        if image is None:
            while_safety += 1
            continue

        if (frame+1)%math.floor(every) == 0:
            while_safety=0
            save_path = os.path.join(frames_dir, name, name + "_{:06d}.jpg".format(math.floor((frame+1)/every)))
            if not os.path.exists(save_path) or overwrite:
                cv2.imwrite(save_path, image)
                saved_count += 1

        frame+=1
        
    capture.release()
        
    return saved_count

def extractFrames(video_path, frames_dir, overwrite=False, every=1, chunk_size=1000):
    """
    Extracts the frames from a video using multiprocessing
    :param video_path: path to the video
    :param frames_dir: directory to save the frames
    :param overwrite: overwrite frames if they exist?
    :param every: extract every this many frames
    :param chunk_size: how many frames to split into chunks (one chunk per cpu core process)
    :return: path to the directory where the frames were saved, or None if fails
    """

    multiprocessing.freeze_support()

    video_path = os.path.normpath(video_path)
    frames_dir = os.path.normpath(frames_dir)

    video_dir, video_filename = os.path.split(video_path)

    os.makedirs(os.path.join(frames_dir, os.path.splitext(os.path.basename(video_filename))[0]), exist_ok=True)

    capture = cv2.VideoCapture(video_path)
    total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = capture.get(cv2.CAP_PROP_FPS)
    capture.release()

    if total < 1:
        print("Video has no frames. Check your OpenCV + ffmpeg installation")
        return None

    frame_chunks = [[i, i+chunk_size] for i in range(0, total, chunk_size)]
    frame_chunks[-1][-1] = min(frame_chunks[-1][-1], total-1)

    print("Video frames:", total)
    print("Video chunks:", len(frame_chunks))
    print("Video fps:", fps)
    print("Video length (seconds):", total/fps)

    prefix_str = "Extracting frames from {}".format(video_filename)
    
    pbar = tqdm.notebook.trange(math.floor(total/math.floor(every)))

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = [executor.submit(extractChunk, video_path, frames_dir, overwrite, every, f[0], f[1]) for f in frame_chunks]
        for i, f in enumerate(as_completed(futures)): 
            pbar.update(math.floor((frame_chunks[i][1]-frame_chunks[i][0])/math.floor(every)))
        pbar.update(1)
        pbar.close()

    return os.path.join(frames_dir, os.path.splitext(os.path.basename(video_filename))[0])
