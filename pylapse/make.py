import cv2
import glob
import sys
import os
from argparse import ArgumentParser
from tqdm import tqdm

def is_grey(arr):
    avg = arr.mean(axis=-1)
    num = len(avg)
    gprop = sum([1. / num if x < 130 and x > 126 else 0 for x in avg])
    return gprop > 0.8

def make(folder, output, fps=24, fmt="H264", start=0, end=-1):
    fps = int(fps)
    img_array = []
    all_files = sorted([
        os.path.join(folder, filename)
        for filename in os.listdir(folder)
        if filename.endswith(".jpg")
    ])
    if end <= 0:
        end = len(all_files) + end
    all_files = all_files[start:end]
    max_nl_grey = 0
    for filename in tqdm(all_files):
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width, height)
        keep = True

        hist = cv2.calcHist([img],[0],None,[256],[0,256])
        hist = [h[0] for h in hist]
        # Detect the images with too low luminosity (night)
        black = sum(hist[:6]) * 1. / sum(hist)
        keep = keep and black < 0.9
        # Images that failed tend to be almost all grey
        #  --> detect that not to add them
        grey = sum(hist[126:130]) * 1. / sum(hist)
        keep = keep and grey < 0.9

        # Add the image to the list if we want to keep it
        if keep:
            nl_grey = 0
            while is_grey(img[height - nl_grey - 1]):
                nl_grey += 1
            if nl_grey < 32:
                if nl_grey > max_nl_grey:
                    max_nl_grey = nl_grey
                img_array.append((filename, nl_grey))

    # Write video
    fourcc = cv2.VideoWriter_fourcc(*fmt)
    out = cv2.VideoWriter(output, fourcc, fps, (width, height - max_nl_grey))
    for filename, nl_grey in tqdm(img_array):
        img = cv2.imread(filename)
        height, width, layers = img.shape
        out.write(img[max_nl_grey - nl_grey:height - nl_grey,:,:])
    out.release()

if __name__ == '__main__':
    parser = ArgumentParser(description="Create movie from folder")
    parser.add_argument(
        "--fps",
        default=24,
        type=int,
        help="Frames per second (default: 24)"
    )
    parser.add_argument(
        "--format",
        type=str,
        default="H264",
        help="Output format"
    )
    parser.add_argument(
        "--start",
        default=0,
        type=int,
        help="First frame"
    )
    parser.add_argument(
        "--end",
        default=-1,
        type=int,
        help="Last frame"
    )
    parser.add_argument("folder", help="Input folder")
    parser.add_argument("output", help="Output file")
    args = parser.parse_args()
    make(
        args.folder,
        args.output,
        fps=args.fps,
        fmt=args.format,
        start=args.start,
        end=args.end
    )
