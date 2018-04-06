from conans import ConanFile, tools, AutoToolsBuildEnvironment
import platform
import shutil

class LiblqrConan(ConanFile):
    name = 'liblqr'

    source_version = '0.4.2'
    package_version = '4'
    version = '%s-%s' % (source_version, package_version)

    build_requires = 'llvm/3.3-5@vuo/stable'
    requires = 'glib/2.51.1-4@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-liblqr'
    license = 'https://github.com/carlobaldassi/liblqr/blob/master/COPYING.LESSER'
    description = 'A C/C++ API for performing non-uniform resizing of images by the seam-carving technique'
    source_dir = 'liblqr-%s' % source_version
    build_dir = '_build'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def imports(self):
        self.copy('*', self.build_dir, 'lib')

    def source(self):
        tools.get('https://github.com/carlobaldassi/liblqr/archive/v%s.tar.gz' % self.source_version,
                  sha256='1019a2d91f3935f1f817eb204a51ec977a060d39704c6dafa183b110fd6280b0')

        self.run('mv %s/COPYING.LESSER %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)

            # The LLVM/Clang libs get automatically added by the `requires` line,
            # but this package doesn't need to link with them.
            autotools.libs = ['c++abi']

            autotools.flags.append('-Oz')

            if platform.system() == 'Darwin':
                autotools.flags.append('-mmacosx-version-min=10.10')
                autotools.link_flags.append('-Wl,-rpath,@loader_path')
                autotools.link_flags.append('-Wl,-install_name,@rpath/liblqr.dylib')

            env_vars = {
                'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
                'PKG_CONFIG_PATH': self.deps_cpp_info["glib"].rootpath,
            }
            with tools.environment_append(env_vars):
                autotools.configure(configure_dir='../%s' % self.source_dir,
                                    args=['--quiet',
                                          '--prefix=%s/%s' % (self.build_folder, self.build_dir)])

                autotools.make(args=['install'])

            if platform.system() == 'Darwin':
                shutil.move('lqr/.libs/liblqr-1.0.dylib', 'lqr/.libs/liblqr.dylib')
            elif platform.system() == 'Linux':
                shutil.move('lib/liblqr-1.so.0.3.2', 'lib/liblqr.so')
                patchelf = self.deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
                self.run('%s --set-soname liblqr.so lib/liblqr.so' % patchelf)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        self.copy('*.h', src='%s/include/lqr-1' % self.build_dir, dst='include')
        self.copy('liblqr.%s' % libext, src='%s/lqr/.libs' % self.build_dir, dst='lib')
        self.copy('liblqr.%s' % libext, src='%s/lib' % self.build_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['lqr']
