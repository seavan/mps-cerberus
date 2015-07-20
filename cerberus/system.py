# encoding: utf-8

import os
import pexpect
import subprocess

def run(cmd):
    p = subprocess.Popen(cmd, shell=True, close_fds=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    rc = p.wait()
    return (rc, p.stdout.read(), p.stderr.read())

def run_ffmpeg(cmd, progress_handler=None):

    os.environ['AV_LOG_FORCE_NOCOLOR'] = "true"

    def parse_duration_line(line):
        (hours, minutes, secs) = line.split(":")
        (secs, msecs) = secs.split(".")

        (hours, minutes, secs, msecs) = [int(x) for x in (hours, minutes, secs, msecs)]

        return msecs + (secs * 100) + (minutes * 60 * 100) + (hours * 60 * 60 * 100)

    def parse_progress_line(line):
        (secs, msecs) = [int(x) for x in line.split('.')]

        return msecs + (secs * 100)


    child = pexpect.spawn(cmd)
    patterns = child.compile_pattern_list([
        pexpect.EOF,
        "frame=\ .*time=([0-9.]+)\ ",
        "\ \ Duration:\ ([0-9:.]+),"
    ])

    duration = None
    durations = []

    while True:
        index = child.expect_list(patterns, timeout=None)

        if index == 0:
            break

        elif index == 1:
            progress_line = child.match.group(1)
            progress_time = parse_progress_line(progress_line)

            progress = progress_time * 100 / duration
            if progress_handler:
                progress_handler(progress)

        elif index == 2:
            duration_line = child.match.group(1)
            durations.append(parse_duration_line(duration_line))
            duration = max(durations)
