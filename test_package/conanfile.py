from conans import ConanFile

class LiblqrTestConan(ConanFile):
    generators = 'qbs'

    def build(self):
        self.run('qbs -f "%s"' % self.conanfile_directory);

    def imports(self):
        self.copy('*.dylib', dst='bin', src='lib')

    def test(self):
        self.run('qbs run')

        # Ensure we only link to system libraries and to libraries we built.
        self.run('! (otool -L bin/liblqr.dylib | tail +3 | egrep -v "^\s*(/usr/lib/|/System/|@rpath/)")')