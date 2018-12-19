#!/usr/bin/python

import os
import stat
import errno
import shutil
import fnmatch

from tempfile import mkstemp, mkdtemp
from contextlib import contextmanager


def from_exception(message=None):
    from sys import exc_info
    exc_type, exc_val, exc_tb = exc_info()
    raise exc_type, message if message is not None else exc_val, exc_tb


@contextmanager
def safe_tempfile(filename, copystat=True):
    dirname, basename = os.path.split(filename)
    filedes, tempname = mkstemp(dir=dirname, prefix=basename + '.')

    try:
        st = os.stat(filename)
    except OSError:
        st = None

    try:
        if st and copystat:
            os.utime(tempname, (st.st_atime, st.st_mtime))
            os.chmod(tempname, stat.S_IMODE(st.st_mode))
            os.chown(tempname, st.st_uid, st.st_gid)
        else:
            _umask = os.umask(0)
            os.umask(_umask)
            os.utime(tempname, None)
            os.chmod(tempname, 0666 & ~_umask)

        yield os.fdopen(filedes, 'w')
        os.rename(tempname, filename)
    except BaseException as e:
        os.unlink(tempname)
        raise from_exception(e)


@contextmanager
def safe_tempname(filename):
    dirname, basename = os.path.split(filename)
    temppath = mkdtemp(dir=dirname)
    tempname = os.path.join(temppath, basename)

    try:
        yield tempname
        os.rename(tempname, filename)
    except BaseException as e:
        TryUnlink(tempname)
        raise from_exception(e)
    finally:
        os.rmdir(temppath)


@contextmanager
def safe_tempfifo(fifoname):
    temppath = mkdtemp()
    tempname = os.path.join(temppath, fifoname)

    try:
        os.mkfifo(tempname)
        yield tempname
    except BaseException as e:
        TryUnlink(tempname)
        raise from_exception(e)
    else:
        TryUnlink(tempname)
    finally:
        os.rmdir(temppath)


def IsRoot():
    return not bool(os.geteuid())


def getenv(name, value=''):
    return os.getenv(name, value)


def setenv(name, value=''):
    if not value:
        os.environ.setdefault(name, value)
        del os.environ[name]
        os.unsetenv(name)
    else:
        os.environ.pop(name, None)
        os.environ.setdefault(name, value)
        os.putenv(name, value)


@contextmanager
def environ(**kwargs):
    try:
        for envvar, _value in kwargs.items():
            kwargs[envvar] = getenv(envvar)
            setenv(envvar, _value)

        yield
    finally:
        for envvar, _value in kwargs.items():
            setenv(envvar, _value)


def WhichExec(name):
    for path in getenv("PATH").split(os.pathsep):
        temp = os.path.join(path, name)
        if os.path.isfile(temp) and os.access(temp, os.X_OK):
            return temp
    return None


def match_type(pathname, files=True, dirs=False):
    if files and os.path.isfile(pathname):
        return True
    if dirs and os.path.isdir(pathname):
        return True


def match_name(name, match=None):
    if match is None or match is Ellipsis:
        return True
    elif isinstance(match, basestring):
        return fnmatch.fnmatch(name, match)
    else:
        return any(match_name(name, m) for m in match)


def match_show(name, hidden=False):
    return name[0] != '.' or hidden


def GetFileList(dirpath, match=None, files=True, dirs=False, hidden=False):
    _match_name = lambda name: match_name(name, match)
    _match_type = lambda name: match_type(os.path.join(dirpath, name), files, dirs)
    _match_show = lambda name: match_show(name, hidden)

    _match_file = lambda name: _match_name(name) and _match_type(name) and _match_show(name)

    try:
        return set(name for name in os.listdir(dirpath) if _match_file(name))
    except OSError:
        return set()


def check_dirs(dirpath):
    if dirpath is None:
        raise ValueError
    elif isinstance(dirpath, basestring):
        return os.path.isdir(dirpath)
    else:
        return [_ for _ in dirpath if os.path.isdir(_)]


def find_files(dirlist, match=None, files=True, dirs=False, hidden=False):
    if dirlist is None:
        raise ValueError()
    elif isinstance(dirlist, basestring):
        dirlist = [dirlist]

    results = set()

    for dirpath in dirlist:
        results |= set(GetFileList(dirpath, match, files, dirs, hidden))

    return results


def scan_paths(dirlist, match=None):
    if dirlist is None:
        raise ValueError()
    elif isinstance(dirlist, basestring):
        dirlist = [dirlist]

    results = {}

    for dirpath in dirlist:
        for filename in GetFileList(dirpath, match, dirs=True, files=True):
            filepath = os.path.join(dirpath, filename)
            if os.path.isdir(filepath) == os.path.isfile(filepath):
                continue
            elif os.path.isdir(filepath):
                results[filename] = None
            elif os.path.isfile(filepath):
                results.setdefault(filename, filepath)

    return results


def TryMakeDirs(directory):
    try:
        os.makedirs(directory)
        return True
    except OSError as e:
        if e.errno == errno.EEXIST:
            return True
        else:
            return False
    except Exception:
        return False


def TryRmRfDirs(directory):
    try:
        shutil.rmtree(directory)
        return True
    except OSError as e:
        if e.errno == errno.ENOENT:
            return True
        else:
            return False
    except Exception:
        return False


def TryUnlink(filename):
    try:
        os.unlink(filename)
        return True
    except OSError as e:
        if e.errno == errno.ENOENT:
            return True
        else:
            return False
    except Exception:
        return False


def TryRename(filename, copyname):
    try:
        os.rename(filename, copyname)
        return True
    except Exception:
        return False


def TryCopyFile(filename, copyname):
    try:
        shutil.copy(filename, copyname)
        return True
    except Exception:
        return False


def TrySymlink(filename, linkname):
    try:
        with safe_tempname(linkname) as tempname:
            os.symlink(filename, tempname)
        return True
    except Exception:
        return False


def TrySubmit(filename, lnlist):
    try:
        with safe_tempfile(filename) as tempfile:
            tempfile.writelines(lnlist)
        return True
    except Exception:
        return False


def TouchFile(filename):
    try:
        with open(filename, 'a', 0):
            os.utime(filename, None)
        return True
    except Exception:
        return False


def FileStamp(filename):
    try:
        return os.stat(filename).st_mtime
    except Exception:
        return 0.0


def TrySignal(pid, sig=0):
    try:
        os.kill(pid, sig)
    except OSError as e:
        if e.errno == errno.ESRCH:
            return False
        else:
            raise
    return True
