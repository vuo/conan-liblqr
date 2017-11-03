from conans import ConanFile, tools, AutoToolsBuildEnvironment
import shutil

class LiblqrConan(ConanFile):
    name = 'liblqr'
    version = '0.4.2'
    requires = 'glib/2.51.1@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-liblqr'
    license = 'https://github.com/carlobaldassi/liblqr/blob/master/COPYING.LESSER'
    description = 'A C/C++ API for performing non-uniform resizing of images by the seam-carving technique'
    source_dir = 'liblqr-%s' % version
    build_dir = '_build'

    def source(self):
        tools.get('https://github.com/carlobaldassi/liblqr/archive/v%s.tar.gz' % self.version,
                  sha256='1019a2d91f3935f1f817eb204a51ec977a060d39704c6dafa183b110fd6280b0')

    def imports(self):
        self.copy('*.dylib', '', 'lib')

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.flags.append('-Oz')
            autotools.flags.append('-mmacosx-version-min=10.8')
            autotools.link_flags.append('-Wl,-rpath,%s' % self.build_folder)
            autotools.link_flags.append('-Wl,-install_name,@rpath/liblqr.dylib')

            env_vars = {'PKG_CONFIG_PATH': self.deps_cpp_info["glib"].rootpath}
            with tools.environment_append(env_vars):
                autotools.configure(configure_dir='../%s' % self.source_dir,
                                    args=['--quiet',
                                          '--prefix=%s/%s' % (self.build_folder, self.build_dir)])

                autotools.make(args=['install'])

            shutil.move('lqr/.libs/liblqr-1.0.dylib', 'lqr/.libs/liblqr.dylib')
 
    def package(self):
        self.copy('*.h', src='%s/include/lqr-1' % self.build_dir, dst='include')
        self.copy('liblqr.dylib', src='%s/lqr/.libs' % self.build_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = ['lqr']
