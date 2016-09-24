#!/usr/bin/env python

import subprocess
import os
import signal
import threading
from dbus.mainloop.glib import DBusGMainLoop

class Utility(object):
    """docstring for Utility."""
    def __init__(self):
        super(Utility, self).__init__()

    def link_all(self):
        self.link_music()
        self.link_videos()
        self.link_pictures()

    def unlink_all(self):
        self.unlink_music()
        self.unlink_videos()
        self.unlink_pictures()

    def blacklist_file(self):
        blacklist = []
        blacklist.append('desktop.ini')
        blacklist.append('Thumb.db')
        blacklist.append('Thumbs.db')
        return blacklist

    def link_videos(self):
        dir_src = '/mnt/Hiburan/Danang/Videos/'
        listdir = os.listdir(dir_src)
        dest = '/home/danang/Videos/'
        for fold in listdir:
            if fold not in self.blacklist_file():
                src = dir_src + fold
                dst = dest + fold
                if not os.path.exists(dst):
                    # os.remove(dst)
                    os.symlink(src, dst)

    def link_pictures(self):
        dir_src = '/mnt/Hiburan/Danang/Pictures/'
        listdir = os.listdir(dir_src)
        dest = '/home/danang/Pictures/'
        for fold in listdir:
            if fold not in self.blacklist_file():
                src = dir_src + fold
                dst = dest + fold
                if not os.path.exists(dst):
                    # os.remove(dst)
                    os.symlink(src, dst)

    def link_music(self):
        dir_src = '/mnt/Hiburan/Danang/Music/'
        listdir = os.listdir(dir_src)
        dest = '/home/danang/Music/'
        for fold in listdir:
            if fold not in self.blacklist_file():
                src = dir_src + fold
                dst = dest + fold
                if not os.path.exists(dst):
                    # os.remove(dst)
                    os.symlink(src, dst)

    def unlink_videos(self):
        path = '/home/danang/Videos/'
        fold = os.listdir(path)
        for folder in fold:
            dst = os.path.join(path, folder)
            if not os.path.exists(dst):
                os.unlink(dst)

    def unlink_pictures(self):
        path = '/home/danang/Pictures/'
        fold = os.listdir(path)
        for folder in fold:
            # os.unlink(os.path.join(path, folder))
            dst = os.path.join(path, folder)
            if not os.path.exists(dst):
                os.unlink(dst)

    def unlink_music(self):
        path = '/home/danang/Music/'
        fold = os.listdir(path)
        for folder in fold:
            # os.unlink(os.path.join(path, folder))
            dst = os.path.join(path, folder)
            if not os.path.exists(dst):
                os.unlink(dst)



class Mount(object):
    """docstring for Mount."""
    def __init__(self):
        super(Mount, self).__init__()
        self.util = Utility()
        self.path = []
        self.dev = []
        self.umount = True
        self._count_mounted = len(self.mounted())
        self.was_mounted_dev = [0,1]
        self.was_mounted_path = [0,1]
        self.was_mounted_dev[0] = self.mounted_dev()
        self.was_mounted_dev[1] = self.was_mounted_dev[0]
        self.was_mounted_path[0] = self.mounted_path()
        self.was_mounted_path[1] = self.was_mounted_path[0]

    def count_mounted(self):
        return len(self.mounted())

    def is_change(self):
        if self._count_mounted != self.count_mounted():
            if self._count_mounted > self.count_mounted():
                self.umount = True
            else:
                self.umount = False
            self._count_mounted = self.count_mounted()
            return True

    def get_changed(self):
        self.was_mounted_dev[1] = self.mounted_dev()
        if set(self.was_mounted_dev[0]) == set(self.was_mounted_dev[1]):
            return []
        else:
            diff = []
            if len(self.was_mounted_dev[0]) > len(self.was_mounted_dev[1]):
                for dev in self.was_mounted_dev[0]:
                    if dev not in self.was_mounted_dev[1]:
                        diff.append(dev)
                        self.umount = True
            else:
                for dev in self.was_mounted_dev[1]:
                    if dev not in self.was_mounted_dev[0]:
                        diff.append(dev)
                        self.umount = False

            self.was_mounted_dev[0] = self.was_mounted_dev[1]
            return diff

    def set_path(self, path):
        self.path.append(path)

    def set_dev(self, dev):
        self.dev.append(dev)

    def mounted(self):
        d = {}
        for l in file('/proc/mounts'):
            if l[0] == '/':
                l = l.split()
                d[l[0]] = l[1]
        return d

    def mounted_dev(self):
        mounted_dev = []
        for dev, path in self.mounted().items():
            mounted_dev.append(dev)
        return mounted_dev

    def mounted_path(self):
        mounted_path = []
        for dev, path in self.mounted().items():
            mounted_path.append(path)
        return mounted_path

    def is_dev_mounted(self, dev):
        # self.mounted()
        if dev in self.mounted():
            return True
        else:
            return False

    def is_path_mounted(self, path):
        return os.path.ismount(path)

    def is_mounted(self, path):
        if os.path.ismount(path) or self.is_dev_mounted(path):
            return True
        else:
            return False
        # path = path.rstrip('/')
        # self.mounted()
        # for (dev, pathed) in self.mounted().items():
        #     if path == pathed:
        #         return True
        # return False

    def execute(self):
        self.set_dev('/dev/sda5')
        self.set_path('/mnt/Hiburan')
        if self.is_change():
            changed = self.get_changed()
            if '/dev/sda5' in changed:
                if not self.umount:
                    self.util.link_all()
                else:
                    self.util.unlink_all()
            print changed, not self.umount
        # for dev in self.dev:
        #     if dev in self.mounted_dev():
        #         self.util.link_videos()

    def main(self):
        thread = threading.Timer(1, self.main)
        self.mounted()
        self.execute()
        thread.start()


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    path = __file__
    p1 = subprocess.Popen(["ps", "ax"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["grep", path], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    proc = p2.communicate()[0].split("\n")
    if len(proc) == 4:
        pid = proc[0].split()[0]
        os.kill(int(pid), signal.SIGTERM)
    elif len(proc) > 4:
        for p in proc:
            try:
                pid = p.split()[0]
                os.kill(int(pid), signal.SIGTERM)
            except Exception, e:
                pass

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    mount = Mount()
    mount.main()
