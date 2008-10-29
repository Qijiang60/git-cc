from subprocess import Popen, PIPE
import os, sys
from os.path import join, exists, abspath, dirname
from ConfigParser import SafeConfigParser

CC_TAG = 'clearcase'
CFG_CC = 'clearcase'
CC_DIR = None

def fail(string):
    print string
    sys.exit(2)

def doStash(f, stash):
    if(stash):
        git_exec(['stash'])
    f()
    if(stash):
        git_exec(['stash', 'pop'])

def debug(string):
    if(DEBUG):
        print string

def git_exec(cmd, env=None):
    return popen('git', cmd, GIT_DIR, env=env)

def cc_exec(cmd):
    return popen('cleartool', cmd, CC_DIR)

def popen(exe, cmd, cwd, env=None):
    cmd.insert(0, exe)
    debug(cmd)
    return Popen(cmd, cwd=cwd, stdout=PIPE, env=env).stdout.read()

def tag(id="HEAD"):
    git_exec(['tag', '-f', CC_TAG, id])

def reset(tag=CC_TAG):
    git_exec(['reset', '--hard', tag])

def gitDir():
    def findGitDir(dir):
        abs = abspath(dir)
        if not exists(abs):
            return '.'
        if exists(join(abs, '.git')):
            return abs
        return findGitDir(parent(dir))
    return findGitDir('.')

class GitConfigParser():
    section = 'gitcc'
    def __init__(self):
        self.file = join(GIT_DIR, '.git', 'gitcc')
        self.parser = SafeConfigParser();
        self.parser.add_section(self.section)
    def set(self, name, value):
        self.parser.set(self.section, name, value)
    def read(self):
        self.parser.read(self.file)
    def write(self):
        self.parser.write(open(self.file, 'w'))
    def get(self, name, default=None):
        if not self.parser.has_option(self.section, name):
            return default
        return self.parser.get(self.section, name)
    def getList(self, name, default=None):
        return self.get(name, default).split('|')

def checkPristine():
    if not CC_DIR:
        fail('No .git directory found')
    if(len(git_exec(['ls-files', '--modified']).splitlines()) > 0):
        fail('There are uncommitted files in your git directory')

def write(file, blob):
    f = open(file, 'w')
    f.write(blob)
    f.close()

def parent(file):
    return join(file, '..')

def mkdirs(file):
    dir = dirname(file)
    if not exists(dir):
        os.makedirs(dir)

def removeFile(file):
    if exists(file):
        os.remove(file)

GIT_DIR = gitDir()
cfg = GitConfigParser()
if exists(join(GIT_DIR, '.git')):
    cfg.read()
    CC_DIR = cfg.get(CFG_CC)
DEBUG = cfg.get('debug', True)