import sys
import os
import os.path
import subprocess
import csv

from collections import OrderedDict

MKVMERGE_EXEC = "mkvmerge"
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

# NOTE: mkvmerge uses return code 1 for warnings, but we want to ignore those
def _run_ignore_1(*cmd_parts):
    cmd = " ".join(cmd_parts)
    print("running", " ".join(cmd_parts))
    result = subprocess.run(cmd_parts)
    if result.returncode != 0 and result.returncode != 1:
        _fail("non-zero return code for command {}".format(cmd))


def _quote(message):
    return "\"" + message + "\""


def has_exec(file):
    try:
        subprocess.run(file, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return False
    return True


def has_control_file():
    return os.path.isfile(CONTROL_FILE)


# --split parts-frames:0-1000,2000-2050
# --split parts:00:01:20-00:02:45,00:05:50-00:10:30
def mkvsplit(input_file, output_file, cut_from, cut_to, parts_timecodes=False):
    parts = "parts-frames" if not parts_timecodes else "parts"
    _run(
        MKVMERGE_EXEC,
        "--output", output_file,
        "--split", "{}:{}-{}".format(parts, cut_from, cut_to),
        input_file
    )


# mkvmerge -o full.mkv file1.mkv +file2.mkv
def mkvmerge(output_file, *files):
    append_files = " +".join(files).split()
    _run_ignore_1(
        MKVMERGE_EXEC,
        "--output", output_file,
        *append_files
    )


def _strip_and_clamp(row, target_len):
    if len(row) < target_len:
        return None
    values = []
    for value in row[:target_len]:
        new_value = value.strip()
        if new_value == "":
            return None
        values.append(new_value)
    return values


def target_and_cuts_from_control_file():
    result = OrderedDict()
    last_target = None
    with open(CONTROL_FILE) as fin:
        reader = csv.reader(fin)
        next(reader, None)
        for row in reader:
            values = _strip_and_clamp(row, 4)
            if not values:
                continue
            (source, target, cut_from, cut_to) = values
            last_target = target
            if target in result:
                result[target].append((source, cut_from, cut_to))
            else:
                result[target] = [(source, cut_from, cut_to)]
    return result.items(), last_target


def usage():
    print("""{} [--no-merge] [--parts-timecodes]

    --no-merge        \tskip the merge step and don't delete parts
    --parts-timecodes \tcut_form, cut_to are passed as timecodes "[HH:]MM:SS[.sss]"
    """.format(sys.argv[0]))
    sys.exit(0)


def main():
    no_merge = "--no-merge" in sys.argv
    no_skip = "--no-skip" in sys.argv
    parts_timecodes = "--parts-timecodes" in sys.argv

    if "-h" in sys.argv or "--help" in sys.argv:
        usage()

    if not has_exec(MKVMERGE_EXEC):
        _fail("""{} not found
download latest release mkvtoolnix and put it on your PATH
https://www.fosshub.com/MKVToolNix.html""".format(MKVMERGE_EXEC))

    if not has_control_file():
        _fail("""control file {control_file} not found
create a new control file {control_file} with a content similar to:
source   ,target,cut_from  ,cut_to
input.mkv,a.mkv ,00:01:00.0,00:02:00.0
input.mkv,a.mkv ,00:10:00.0,00:11:00.0
a.mkv    ,b.mkv ,00:01:00.0,00:02:00.0
input.mkv,b.mkv ,00:20:00.0,00:21:00.0
""".format_map({"control_file": CONTROL_FILE}))

    items, last_target = target_and_cuts_from_control_file()
    for target, cuts in items:
        if not no_skip and target != last_target and os.path.isfile(target):
            print("skipping {}".format(target))
            continue
        subtargets = []
        for index, (source, cut_from, cut_to) in enumerate(cuts):
            if not os.path.isfile(source):
                _fail("source {} not found".format(source))
            subtarget = "{}-{}.mkv".format(target[:-4], index + 1)
            mkvsplit(source, subtarget, cut_from, cut_to, parts_timecodes)
            subtargets.append(subtarget)
        if not no_merge:
            mkvmerge(target, *subtargets)
            for subtarget in subtargets:
                os.remove(subtarget)


if __name__ == "__main__":
    main()
