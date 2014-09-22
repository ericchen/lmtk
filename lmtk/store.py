#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""lmtk.store - Tools for persisting stuff to disk."""

import os
import sys
import tempfile
import glob
from hashlib import md5
from ConfigParser import SafeConfigParser


class FileStore(object):

    def __init__(self, path=os.path.join(tempfile.gettempdir(), 'uk.ac.cam.phy.sd.lmtk')):
        """Class to store files on disk in a directory.

        Uses a temporary directory unless a custom path is specified.
        """
        self.path = path

    @property
    def path(self):
        """Path to the directory where files are stored."""
        return self._path

    @path.setter
    def path(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)
        self._path = path

    def get(self, fskey):
        f = open(os.path.join(self.path, fskey), 'rb')
        return f

    def get_data(self, fskey):
        f = self.get(fskey)
        data = f.read()
        f.close()
        return data

    def fpath(self, fskey):
        return os.path.join(self.path, fskey)

    def save(self, f):
        data = f.read()
        return self.save_data(data)

    def save_data(self, data):
        fskey = md5(data).hexdigest()
        if not self.exists(fskey):
            f = open(os.path.join(self.path, fskey), 'wb')
            f.write(data)
            f.close()
        return fskey

    def exists(self, fskey):
        return os.path.exists(fskey)

    def delete(self, fskey):
        try:
            os.remove(os.path.join(self.path, fskey))
        except OSError:
            pass

    def clear(self):
        # TODO: Some kind of automated clearing? When does tempdir change?
        for f in glob.glob(os.path.join(self.path, '*')):
                os.remove(f)


class Config(object):
    """Read and write to config file.

    A config object is essentially a key-value store that can be treated like a dictionary:

        c = Config()
        c['foo'] = 'bar'
        print c['foo']

    The default location of the file depends on the operating system:

    - Unix: ~/.config/lmtk/
    - Mac: ~/Library/Application Support/lmtk/
    - Windows: Who knows!

    The default filename within this directory is 'config', but this can be overridden:

        c = Config('extraconfig')
        c['where'] = 'in a different file'

    It is possible to edit the file by hand with a text editor.

    Warning: multiple instances of Config() pointing to the same file will not see each others' changes, and will
    overwrite the entire file when any key is changed.

    """

    # These values will be present in a config object unless they are explicitly defined otherwise in the config file
    default_values = {}

    def __init__(self, filename='config'):
        self.filename = filename
        self.parser = SafeConfigParser()
        self.parser.read(self.path)
        self.data = self.default_values
        if not self.parser.has_section('lmtk'):
            self.parser.add_section('lmtk')
        for k, v in self.parser.items('lmtk'):
            self.data[k] = v

    def save(self):
        """ Save the contents of data to the file on disk """
        for name, value in self.data.items():
            self.parser.set('lmtk', str(name), str(value))
        d = os.path.dirname(self.path)
        if not os.path.isdir(d):
            os.makedirs(d)
        f = open(self.path, 'w')
        self.parser.write(f)
        f.close()

    def __contains__(self, k):
        return self.data.__contains__(k)

    def __getitem__(self, k):
        return self.data.__getitem__(k)

    def __setitem__(self, k, v):
        self.data.__setitem__(k, v)
        self.save()

    def __delitem__(self, k):
        self.data.__delitem__(k)
        self.save()

    def __iter__(self):
        return self.data.__iter__()

    def __len__(self):
        return self.data.__len__()

    def delete(self):
        """ Delete the configuration file from disk """
        os.remove(self.path)
        self.data = {}

    @property
    def path(self):
        """Return the path to the config file.

        This was derived using information from the appdirs package:
        https://github.com/ActiveState/appdirs
        Copyright (c) 2010 ActiveState Software Inc.
        MIT license

        """
        if sys.platform == 'win32':
            try:
                from win32com.shell import shellcon, shell
                cdir = shell.SHGetFolderPath(0, getattr(shellcon, 'CSIDL_LOCAL_APPDATA'), 0, 0)
                try:
                    cdir = unicode(cdir)
                    has_high_char = False
                    for c in dir:
                        if ord(c) > 255:
                            has_high_char = True
                            break
                    if has_high_char:
                        try:
                            import win32api
                            cdir = win32api.GetShortPathName(dir)
                        except ImportError:
                            pass
                except UnicodeError:
                    pass
                path = os.path.normpath(cdir)
            except ImportError:
                try:
                    import ctypes
                    buf = ctypes.create_unicode_buffer(1024)
                    ctypes.windll.shell32.SHGetFolderPathW(None, 28, None, 0, buf)
                    has_high_char = False
                    for c in buf:
                        if ord(c) > 255:
                            has_high_char = True
                            break
                    if has_high_char:
                        buf2 = ctypes.create_unicode_buffer(1024)
                        if ctypes.windll.kernel32.GetShortPathNameW(buf.value, buf2, 1024):
                            buf = buf2
                    path = os.path.normpath(buf.value)
                except ImportError:
                    import _winreg
                    key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                                          r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
                    cdir, ctype = _winreg.QueryValueEx(key, 'Local AppData')
                    path = os.path.normpath(cdir)
            return os.path.join(path, 'lmtk', 'lmtk', self.filename)
        elif sys.platform == 'darwin':
            return os.path.join(os.path.expanduser('~/Library/Application Support/'), 'lmtk', self.filename)
        else:
            return os.path.join(os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config')), 'lmtk', self.filename)


fs = FileStore()
config = Config()

# TODO: MongoDB wrapper
