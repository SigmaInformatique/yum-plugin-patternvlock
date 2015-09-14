# -----------------------------------------------------------------
# -  Copyright (c) 2015 SIGMA INFORMATIQUE (http://www.sigma.fr)  -
# -     872 803 390 R.C.S. NANTES (France)                        -
# -----------------------------------------------------------------
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# by Erwan Seite <eseite@sigma.fr>
# based on the work from Panu Matilainen <pmatilai@laiskiainen.org>
# and James Antill <james@and.org> for yum-plugin-versionlock
# -----------------------------------------------------------------

from yum.plugins import PluginYumExit
from yum.plugins import TYPE_CORE
from rpmUtils.miscutils import splitFilename
from yum.packageSack import packagesNewestByName

import urlgrabber
import urlgrabber.grabber

import os
import fnmatch
import tempfile
import time

requires_api_version = '2.1'
plugin_type = (TYPE_CORE,)

_pattern_vlock_excluder_n      = set()
_pattern_vlock_excluder_nevr   = set()

_pattern_vlock_excluder_B_nevr = set()

#  In theory we could do full nevra/pkgtup ... but having foo-1.i386 and not
# foo-1.x86_64 would be pretty weird. So just do "archless".
# _pattern_vlock_excluder_pkgtup = set()

fileurl = None
verbosemode = False

def _read_patternlocklist():
    locklist = []
    try:
        llfile = urlgrabber.urlopen(fileurl)
        for line in llfile.readlines():
            if line.startswith('#') or line.strip() == '':
                continue
            locklist.append(line.rstrip())
        llfile.close()
    except urlgrabber.grabber.URLGrabError, e:
        raise PluginYumExit('Unable to read pattern version lock configuration: %s' % e)
    return locklist

class PatternVLockCommand:
    created = 1440572619

    def getNames(self):
        return ["patternvlock"]

    def getUsage(self):
        return '[add|exclude|list|delete|clear] [PACKAGE-wildcard]'

    def getSummary(self):
        return 'Control package version locks with patterns.'

    def doCheck(self, base, basecmd, extcmds):
        pass

    def doCommand(self, base, basecmd, extcmds):
        cmd = 'list'
        if extcmds:
            if extcmds[0] not in ('add',
                                  'exclude', 'add-!', 'add!', 'blacklist',
                                  'list', 'del', 'delete', 'clear','clean','help'):
                cmd = 'help'
            else:
                cmd = {'del'       : 'delete',
                       'add-!'     : 'exclude',
                       'add!'      : 'exclude',
                       'blacklist' : 'exclude',
                       'clean'     : 'clear',
                       }.get(extcmds[0], extcmds[0])
                extcmds = extcmds[1:]

        filename = fileurl
        if fileurl.startswith("file:"):
            filename = fileurl[len("file:"):]

        if not filename.startswith('/') and cmd != 'list':
            print "Error: patternvlock URL isn't local: " + fileurl
            return 1, ["patternvlock %s failed" % (cmd,)]

        if cmd == 'help':
            return 0, ["yum %s %s\n  %s" % (self.getNames()[0],self.getUsage(),self.getSummary())]
 
        if cmd == 'add':
            patternadded = 0
            done = set(_read_patternlocklist())
            fo = open(filename, 'a')
            for pattern in extcmds:
                if (pattern) in done:
                    print "Pattern %s is already present" % (pattern)
                    continue
                done.add(pattern)
                fo.write("\n# Added pattern lock on %s\n" % time.ctime())
                fo.write("%s\n" % (pattern))
                patternadded += 1
            return 0, ['patternvlock: ' + str(patternadded) + ' pattern(s) added']  
        if cmd == 'exclude':
            patternadded = 0
            done = set(_read_patternlocklist())
            fo = open(filename, 'a')
            for pattern in extcmds:
                if ("!" + pattern) in done:
                    print "Exclusion pattern %s is already present" % (pattern)
                    continue
                done.add("!" + pattern)
                fo.write("\n# Added exclusion pattern lock on %s\n" % time.ctime())
                fo.write("!%s\n" % (pattern))
                patternadded += 1
            return 0, ['patternvlock: ' + str(patternadded) + ' exclusion(s) added']
        if cmd == 'clear':
            open(filename, 'w')
            return 0, ['patternvlock cleared']

        if cmd == 'delete':
            dirname = os.path.dirname(filename)
            (out, tmpfilename) = tempfile.mkstemp(dir=dirname, suffix='.tmp')
            out = os.fdopen(out, 'w', -1)
            count = 0
            for ent in _read_patternlocklist():
                found = False
                for match in extcmds:
                    if fnmatch.fnmatch(ent, match):
                        found = True
                        break
                if found:
                    print "Deleting patternvlock for:", ent
                    count += 1
                    continue
                out.write(ent)
                out.write('\n')
            out.close()
            if not count:
                os.unlink(tmpfilename)
                return 1, ['Error: patternvlock delete: no matches']
            os.rename(tmpfilename, filename)
            return 0, ['patternvlock deleted: ' + str(count)]

        assert cmd == 'list'
        for ent in _read_patternlocklist():
            print ent

        return 0, ['patternvlock list done']

    def needTs(self, base, basecmd, extcmds):
        return False

def config_hook(conduit):
    global fileurl
    global verbosemode

    fileurl = conduit.confString('main', 'patternlocklist')
    verbosemode = conduit.confBool('main', 'verbose', False)

    if hasattr(conduit._base, 'registerCommand'):
        conduit.registerCommand(PatternVLockCommand())

def _add_patternvlock_whitelist(conduit):
    if hasattr(conduit, 'registerPackageName'):
        conduit.registerPackageName("yum-plugin-patternvlock")
    ape = conduit._base.pkgSack.addPackageExcluder
    exid = 'yum-utils.patternvlock.W.'
    ape(None, exid + str(1), 'wash.marked')
    ape(None, exid + str(2), 'mark.name.in', _pattern_vlock_excluder_n)
    ape(None, exid + str(3), 'wash.nevr.in', _pattern_vlock_excluder_nevr)
    ape(None, exid + str(4), 'exclude.marked')

def _add_patternvlock_blacklist(conduit):
    if hasattr(conduit, 'registerPackageName'):
        conduit.registerPackageName("yum-plugin-patternvlock")
    ape = conduit._base.pkgSack.addPackageExcluder
    exid = 'yum-utils.patternvlock.B.'
    ape(None, exid + str(1), 'wash.marked')
    ape(None, exid + str(2), 'mark.nevr.in', _pattern_vlock_excluder_B_nevr)
    ape(None, exid + str(3), 'exclude.marked')

def exclude_hook(conduit):
    conduit.info(3, 'Reading pattern version lock configuration')

    if not fileurl:
        raise PluginYumExit('Patternlocklist not set')

    pkgs = {}
    patternlist = []
    patternlistnegate = []
    for ent in _read_patternlocklist():
        if ent and ent[0] == '!':
            patternlistnegate.append(ent[1:])
            continue
        patternlist.append(ent)
 
    if len(patternlist) == 0 and len(patternlistnegate) == 0:
        return 0

    conduit.info(3, 'Applying pattern version lock configuration')

    if len(patternlistnegate) > 0:
        pkglistnegate=set()
        if verbosemode:
            print "Excluding the following(s) pattern(s)"
            for pattern in patternlistnegate:
                print "  - " + pattern
        pkgs = conduit._base.pkgSack.returnPackages(patterns=patternlistnegate)
        for pkg in pkgs:
            #  We ignore arch, so only add one entry for foo-1.i386 and
            # foo-1.x86_64.
            (n, a, e, v, r) = pkg.pkgtup
            a = '*'
            if (n, a, e, v, r) in pkglistnegate:
                continue
            pkglistnegate.add((n, a, e, v, r))
            _pattern_vlock_excluder_B_nevr.add("%s-%s:%s-%s" % (n, e, v, r))

    if len(patternlist) > 0:
        pkglist=set()
        if verbosemode:
            print "Incluing the following(s) pattern(s)"
            for pattern in patternlist:
                print "  - " + pattern
        pkgs = conduit._base.pkgSack.returnPackages(patterns=patternlist)
        for pkg in pkgs:
            #  We ignore arch, so only add one entry for foo-1.i386 and
            # foo-1.x86_64.
            (n, a, e, v, r) = pkg.pkgtup
            a = '*'
            if (n, a, e, v, r) in pkglist:
                continue
            _pattern_vlock_excluder_n.add(n)
            _pattern_vlock_excluder_nevr.add("%s-%s:%s-%s" % (n, e, v, r))

    if (_pattern_vlock_excluder_n and
        conduit.confBool('main', 'follow_obsoletes', default=False)):
        #  If anything obsoletes something that we have patternvlocked ... then
        # remove all traces of that too.
        for (pkgtup, instTup) in conduit._base.up.getObsoletesTuples():
            if instTup[0] not in _pattern_vlock_excluder_n:
                continue
            _pattern_vlock_excluder_n.add(pkgtup[0].lower())

    if _pattern_vlock_excluder_n:
        _add_patternvlock_whitelist(conduit)
    if _pattern_vlock_excluder_B_nevr:
        _add_patternvlock_blacklist(conduit)
