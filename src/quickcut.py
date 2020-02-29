import sys
import os
import subprocess
import csv

FFMPEG_EXEC = "ffmpeg"


def _fail(*args, **kwargs):
    print("error:", *args, file=sys.stderr, **kwargs)
    sys.exit(-1)


def has_ffmpeg():
    try:
        subprocess.run(FFMPEG_EXEC, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return False
    return True


def ffmpeg_cut(input_file, output_file, start_at, end_at):
    cmd_parts = (
        FFMPEG_EXEC,
        "-y",
        "-noaccurate_seek",
        "-ss", start_at,
        "-i", input_file,
        "-to", end_at,
        "-c", "copy",
        output_file
    )
    print("running", " ".join(cmd_parts))
    subprocess.run(cmd_parts)


def get_mkv_csv_pairs():
    occurrence = {}
    for file in os.listdir(os.getcwd()):
        if not file.endswith(".mkv") and not file.endswith(".csv"):
            continue
        basename = file[:-4]
        if basename in occurrence:
            occurrence[basename] += 1
        else:
            occurrence[basename] = 1
    return [(name + ".mkv", name + ".csv", name) for name in occurrence.keys() if occurrence[name] == 2]


def cuts_from_csv(cut_file):
    with open(cut_file) as fin:
        reader = csv.reader(fin)
        next(reader, None)
        return [row for row in reader]


def main():
    if not has_ffmpeg():
        _fail("""ffmpeg not found
Download latest ffmpeg release build with static linking and put it on your PATH
https://ffmpeg.zeranoe.com/builds/""")

    for (movie_file, cut_file, basename) in get_mkv_csv_pairs():
        for (cut_name, cut_from, cut_to) in cuts_from_csv(cut_file):
            output_file = basename + "-" + cut_name + ".mkv"
            ffmpeg_cut(movie_file, output_file, cut_from, cut_to)


if __name__ == "__main__":
    main()
