import os
import os.path
import sys
import shutil

DESTPATH = "/usr/local/HDF5-universal"

assert os.path.exists('hdf5-1.8.7.tar.bz2'), "Download hdf5-1.8.7.tar.bz2 into this directory, first"

def system(command):
    assert os.system(command) == 0, "COMMAND FAILED"

system("sudo mkdir -p %s" % DESTPATH)
system("sudo chown %s %s" % (os.getlogin(), DESTPATH))

basedir = os.getcwd()
for arch in 'ppc i386 x86_64'.split():
    print "ARCH", arch
    build_dir = os.path.join(basedir, 'build_%s' % arch)
    if os.path.exists(build_dir):
        continue
        shutil.rmtree(build_dir)
    os.mkdir(build_dir)
    os.chdir(build_dir)
    print "UNPACKING SOURCE"
    system('tar -xjf ../hdf5-1.8.7.tar.bz2')
    os.chdir(os.path.join(build_dir, 'hdf5-1.8.7'))
    os.environ['CFLAGS'] = '-mmacosx-version-min=10.4 -Os -g -isysroot /Developer/SDKs/MacOSX10.4u.sdk -arch %s' % arch
    os.environ['LDFLAGS'] = '-arch %s' % arch
    os.environ['CC'] = 'gcc-4.0'
    os.environ['CXX'] = 'g++-4.0'
    os.environ['CPP'] = 'cpp-4.0'
    print "CONFIGURE"
    system('./configure --prefix=%s --enable-threadsafe  --with-pthread' % DESTPATH)
    print "MAKE"
    system('make')

print "INSTALL"
for arch in 'ppc i386 x86_64'.split():
    continue
    build_dir = os.path.join(basedir, 'build_%s' % arch)
    os.chdir(os.path.join(build_dir, 'hdf5-1.8.7'))
    system('make install')

    # move installed pieces into architecture-specific subdirectories
    for subdir in 'bin lib include'.split():
        os.chdir(os.path.join(DESTPATH, subdir))
        os.mkdir(arch)
        for f in os.listdir('.'):
            if not os.path.isdir(f):
                os.rename(f, os.path.join(arch, f))

print "COMBINE"
def shell_script(f):
    return open(f).read(2) == '#!'
os.chdir(os.path.join(DESTPATH, 'bin'))
for f in os.listdir(os.path.join('.', 'i386')):
    if not shell_script(os.path.join('i386', f)):
        system('lipo -create -output %s */%s' % (f, f))

os.chdir(os.path.join(DESTPATH, 'lib'))
for f in os.listdir(os.path.join('.', 'i386')):
    if f.endswith('.a') or f.endswith('.dylib'):
        system('lipo -create -output %s */%s' % (f, f))


TEMPLATE = '''
#if defined(__ppc__)
#include "ppc/%s"
#elif defined(__i386__)
#include "i386/%s"
#elif defined(__x86_64__)
#include "x86_64/%s"
#else
ERROR!
#endif
'''
def wrap_include(f):
    open(f, 'w').write(TEMPLATE % (f, f, f))


os.chdir(os.path.join(DESTPATH, 'include'))
for f in os.listdir(os.path.join('.', 'i386')):
    wrap_include(f)
