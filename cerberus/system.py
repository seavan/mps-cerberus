# encoding: utf-8

import subprocess

def run(cmd):
    p = subprocess.Popen(cmd, shell=True, close_fds=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    rc = p.wait()
    return (rc, p.stdout.read(), p.stderr.read())
