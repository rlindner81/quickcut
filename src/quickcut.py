import sys
import os
import subprocess
import csv

from collections import OrderedDict

FFMPEG_EXEC = "ffmpeg"
CONTROL_FILE = "quickcut.csv"


def _fail(*args, **kwargs):
    print("error:", *args, file=sys.stderr, **kwargs)
    sys.exit(-1)


def _run(*cmd_parts):
    cmd = " ".join(cmd_parts)
    print("running", " ".join(cmd_parts))
    result = subprocess.run(cmd_parts)
    if result.returncode != 0:
        _fail("non-zero return code for command {}".format(cmd))


def _quote(message):
    return "\"" + message + "\""


def has_ffmpeg():
    try:
        subprocess.run(FFMPEG_EXEC, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return False
    return True


def has_control_file():
    return os.path.isfile(CONTROL_FILE)


def ffmpeg_cut(input_file, output_file, start_at, end_at):
    _run(
        FFMPEG_EXEC,
        "-y",  # OVERWRITE
        "-noaccurate_seek",
        "-ss", _quote(start_at),
        "-i", _quote(input_file),
        "-to", _quote(end_at),
        "-c", "copy",
        _quote(output_file)
    )


def ffmpeg_concat(output_file, *subtargets):
    _run(
        FFMPEG_EXEC,
        "-y",  # OVERWRITE
        "-i", _quote("concat:" + "|".join(subtargets)),
        "-c", "copy",
        _quote(output_file)
    )


def target_and_cuts_from_control_file():
    result = OrderedDict()
    with open(CONTROL_FILE) as fin:
        reader = csv.reader(fin)
        next(reader, None)
        for row in reader:
            (source, target, cut_from, cut_to) = (value.strip() for value in row)
            if target in result:
                result[target].append((source, cut_from, cut_to))
            else:
                result[target] = [(source, cut_from, cut_to)]
    return result.items()


def main():
    if not has_ffmpeg():
        _fail("""{} not found
download latest ffmpeg release build with static linking and put it on your PATH
https://ffmpeg.zeranoe.com/builds/""".format(FFMPEG_EXEC))

    if not has_control_file():
        _fail("""control file {control_file} not found
create a new control file {control_file} with a content similar to:
source,target,cut_from,cut_to
2019-11-02 16-42-01.mkv,a.mkv,00:00:20.00000,00:00:40.00000
2019-11-02 16-42-01.mkv,a.mkv,00:00:30.00000,00:00:50.00000
2019-11-02 16-42-01-part2.mkv,a.mkv,00:00:00.00000,00:01:00.00000
2019-11-02 16-42-01.mkv,b.mkv,00:00:20.00000,00:00:40.00000
2019-11-02 16-42-01.mkv,b.mkv,00:00:20.00000,00:00:40.00000
""".format_map({"control_file": CONTROL_FILE}))

    for target, cuts in target_and_cuts_from_control_file():
        subtargets = []
        for index, (source, cut_from, cut_to) in enumerate(cuts):
            if not os.path.isfile(source):
                _fail("source {} not found".format(source))
            subtarget = "{}-{}.mkv".format(target[:-4], index + 1)
            ffmpeg_cut(source, subtarget, cut_from, cut_to)
            subtargets.append(subtarget)
        ffmpeg_concat(target, *subtargets)
        for subtarget in subtargets:
            os.remove(subtarget)


if __name__ == "__main__":
    main()
