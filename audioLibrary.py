import os
import sqlite3

from PyQt6.QtCore import QByteArray, QBuffer, QIODevice


class DB:
    def __init__(self, filename, uri=True):
        self._conn = sqlite3.connect(filename, uri=uri)
        self._cursor = self._conn.cursor()

    def __del__(self):
        if hasattr(self, "_conn"):
            self._conn.close()

    def execute(self, sql: str, args: tuple = None, printError: bool = True):
        assert isinstance(sql, str)
        assert args is None or isinstance(args, tuple)

        try:
            if args is None:
                self._cursor.execute(sql)
            else:
                self._cursor.execute(sql, args)
        except sqlite3.Error as error:
            if printError:
                print(error)

        return self._cursor


class AudioLibrary(DB):
    def __init__(self):
        # need this for pyinstaller executable to find audio.db file
        _path = os.path.dirname(__file__)
        _filename = os.path.join(_path, "data/audio.db")
        super(AudioLibrary, self).__init__("file:%s?mode=ro" % _filename)

    def get(self, name) -> QBuffer:
        _cursor = self.execute("select contents from audio where name=?", (name,))

        _data = _cursor.fetchone()

        assert isinstance(_data, tuple)
        assert isinstance(_data[0], bytes)

        self._media = QByteArray(_data[0])
        self._qbuffer = QBuffer(self._media)
        self._qbuffer.open(QIODevice.OpenModeFlag.ReadOnly)

        return self._qbuffer
        # return QBuffer(self._media)


class AudioImport(DB):
    def __init__(self):
        # uri - we want to write to the database
        super(AudioImport, self).__init__("file:data/audio.db", uri=False)

        self._create_table()

    def _create_table(self):
        self.execute("drop table if exists audio;")

        self.execute("""create table audio (
                          name     text,
                          contents blob)""")

        self.execute("""create index audio_ndx on audio(name)""")

    def commit(self):
        self._conn.commit()

    def addContents(self, name, contents):
        assert isinstance(name, str)
        assert isinstance(contents, bytes)

        self.execute("insert into audio values (?,?)", (name, contents))

    def addMP3(self, name, filename):
        _blob = None
        with open(filename, "rb") as _fp:
            _blob = _fp.read(-1)

        if _blob is not None:
            self.addContents(name, _blob)
        else:
            print("Error reading '%s'" % filename)


if __name__ == "__main__":
    import os

    _ai = AudioImport()

    #need to run command to take mp3's from out directory and recompile
    #them into more efficient mp3 files..
    #find out -type f -name '*.mp3' -exec ffmpeg -i {} -q:a 8 out1/{} \;
    #before mp3 size was 15MB, now 10MB

    for _root, _dirs, _files in os.walk("out1"):
        _files.sort()
        for _file in _files:
            if _file.endswith(".mp3"):
                _name = _file.replace(".mp3", "")
                _ai.addMP3(_name, os.path.join("out1", _file))

    _ai.commit()
