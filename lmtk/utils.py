#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""lmtk.utils - Miscellaneous utility functions."""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
import functools
import logging
import os
import re
import subprocess

from lmtk.store import config


def floats(s):
    """Convert string to float. Handles more string formats that the standard python conversion."""
    try:
        return float(s)
    except ValueError:
        s = re.sub(ur'(\d)\s*\(\d+(\.\d+)?\)', ur'\1', s)  # Remove bracketed numbers from end
        s = re.sub(ur'(\d)\s*±\s*\d+(\.\d+)?', ur'\1', s)  # Remove uncertainties from end
        s = s.rstrip(u'\'"+-=<>/,.:;!?)]}…∼~≈×*_≥≤')       # Remove trailing punctuation
        s = s.lstrip(u'\'"+=<>/([{∼~≈×*_≥≤')               # Remove leading punctuation
        s = s.replace(u',', u'')                           # Remove commas
        s = u''.join(s.split())                            # Strip whitespace
        s = re.sub(ur'(\d)\s*[×x]\s*10\^?(-?\d)', ur'\1e\2', s)  # Convert scientific notation
        return float(s)


def memoized_property(fget):
    """Decorator to create memoized properties."""
    attr_name = '_{}'.format(fget.__name__)

    @functools.wraps(fget)
    def fget_memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fget(self))
        return getattr(self, attr_name)
    return property(fget_memoized)


def find_file(name=None, env_vars=(), searchpath=(), executable=False):
    """Search for a file.

    :param name: The name or path of the file.
    :param env_vars: A list of environment variables to check.
    :param searchpath: A list of directories to search.
    :param executable: If True, only search for executable files.

    """
    def isfile(path):
        """Check if the path points to a file, and optionally check whether the file is executable."""
        if path and not path in done:
            logging.debug('Checking: %s', path)
            done.add(path)
            if os.path.isfile(path) and (not executable or os.access(path, os.X_OK)):
                logging.debug('Found file: %s', path)
                return True

    done = set()
    name = os.path.expanduser(name)

    # Check for custom path in config
    key = '%s_path' % name
    if key in config:
        path = config[key]
        if isfile(path):
            return path

    # Check if file just exists
    if isfile(name):
        return name

    # Check environment variables
    for env_var in env_vars:
        if env_var in os.environ:
            for env_dir in os.environ[env_var].split(os.pathsep):
                # Check if environment variable a direct path to the file
                if isfile(env_dir):
                    return env_dir
                # Check if environment variable a directory containing the file
                path = os.path.join(env_dir, name)
                if isfile(path):
                    return path

    if name:
        # Check searchpath
        for directory in searchpath:
            path = os.path.join(directory, name)
            if isfile(path):
                return path

        # Try using which command
        if os.name == 'posix':
            try:
                p = subprocess.Popen(['which', name], stdout=subprocess.PIPE)
                stdout, stderr = p.communicate()
                path = stdout.strip()
                if path.endswith(name) and isfile(path):
                    return path
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                pass

    raise LookupError('Unable to find: %s' % name)


def find_binary(name=None, env_vars=(), searchpath=()):
    """Search for an executable file in common bin directories.

    :param name: The name or path of the file.
    :param env_vars: A list of environment variables to check.
    :param searchpath: A list of directories to search.

    """
    if 'rvm' in config:
        rvm = config['rvm']
        searchpath = searchpath + (os.path.expanduser('~/.rvm/gems/%s/bin' % rvm), '/usr/local/rvm/gems/%s/bin' % rvm)
    searchpath = searchpath + ('/opt/local/bin/', '/usr/local/bin/', '/usr/bin/')
    return find_file(name, env_vars=env_vars, searchpath=searchpath, executable=True)


def find_jar(name, env_vars=(), searchpath=()):
    """Search for a jar file.

    The CLASSPATH environment variable is searched automatically.

    :param name: The name or path of the file.
    :param env_vars: A list of environment variables to check.
    :param searchpath: A list of directories to search.

    """
    maven = []
    for directory, _, _ in os.walk(os.path.expanduser('~/.m2/repository')):
        if '.cache' not in directory:
            maven.append(directory)
    env_vars = env_vars + ('CLASSPATH',)
    searchpath = searchpath + ('/usr/local/lib/',) + tuple(maven)
    return find_file(name, env_vars=env_vars, searchpath=searchpath)


def find_data(path):
    """Return the absolute path to a data file

    :param path: relative path of file within the data directory.

    """
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', path)


