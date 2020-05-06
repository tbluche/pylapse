import os
import cv2
import time
import math
import argparse
from tqdm import tqdm
import time
from datetime import datetime

def run(wc, output, end_time, interval, night_slow=1, do_continue=False):
    if do_continue:
        if not os.path.exists(output):
            os.mkdir(output)
        count = len([fn for fn in os.listdir(output) if fn.endswith(".jpg")])
    else:
        os.mkdir(output)
        count = 0
    webcam = cv2.VideoCapture(wc)
    try:
        for i in range(10):
            check, frame = webcam.read()
        while time.time() < end_time:
            what_time = datetime.now()
            is_night = (what_time.hour > 20) and (what_time.hour < 4)
            check, frame = webcam.read()
            if check:
                filename = os.path.join(output, '_img_{:06d}.jpg'.format(count))
                cv2.imwrite(filename=filename, img=frame)
                print(
                    "Written {}.. {} sec left".format(
                        filename, int(end_time - time.time())
                    )
                )
                count += 1
            factor = night_slow if (is_night and check) else 1
            webcam.release()
            time.sleep(interval * factor - 2)
            webcam = cv2.VideoCapture(wc)
            for i in range(20):
                check, frame = webcam.read()
    finally:
        webcam.release()

def tosec(dur, dtype="sec"):
    if dtype == "sec":
        return dur
    if dtype == "min":
        return dur * 60
    if dtype == "hour":
        return dur * 3600
    if dtype == "day":
        return dur * 24 * 3600
    raise ValueError("Invalid duration type: '{}'".format(dtype))


def main():
    parser = argparse.ArgumentParser(
        description="Launch the recording"
    )
    parser.add_argument(
        "-i", "--itype",
        default="sec",
        choices=["sec", "min", "hour", "day"],
        help="Interval type (default: sec)"
    )
    parser.add_argument(
        "-d", "--dtype",
        default="min",
        choices=["sec", "min", "hour", "day"],
        help="Duration type (default: min)"
    )
    parser.add_argument(
        "-n", "--night",
        type=float,
        default=1,
        help="Decrease factor for takes during night"
    )
    parser.add_argument(
        "-w",
        "--webcam",
        type=int,
        default=0,
        help="Webcam number (default: 1)"
    )
    parser.add_argument(
        "-c", "--continue",
        dest="do_continue",
        action="store_true",
        help="Continue mode (restart where it stopped)"
    )
    parser.add_argument(
        "-O", "--output",
        default="output",
        help="Output folder (default: output)"
    )
    parser.add_argument("duration", type=float, help="Duration")
    parser.add_argument("interval", type=float, help="Interval between takes")
    args = parser.parse_args()
    # Convert everything to seconds
    interval = tosec(args.interval, dtype=args.itype)
    duration = tosec(args.duration, dtype=args.dtype)
    end_time = time.time() + duration
    number = int(math.ceil(duration / interval))
    # Notify
    print("Starting capture for {}{} every {}{} (~{} pics)".format(
        args.duration, args.dtype,
        args.interval, args.itype,
        number
    ))
    # Run
    run(
        args.webcam,
        args.output,
        end_time,
        interval,
        night_slow=args.night,
        do_continue=args.do_continue,
    )

if __name__ == '__main__':
    main()
