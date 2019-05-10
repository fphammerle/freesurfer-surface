"""
Python Library to Read and Write Surface Files in Freesurfer's TriangularSurface Format

compatible with Freesurfer's MRISwriteTriangularSurface()
https://github.com/freesurfer/freesurfer/blob/release_6_0_0/include/mrisurf.h#L1281
https://github.com/freesurfer/freesurfer/blob/release_6_0_0/utils/mrisurf.c
https://raw.githubusercontent.com/freesurfer/freesurfer/release_6_0_0/utils/mrisurf.c

Freesurfer
https://surfer.nmr.mgh.harvard.edu/

>>> from freesurfer_surface import Surface
>>>
>>> surface = Surface.read_triangular('bert/surf/lh.pial'))
"""

import collections
import datetime
import re
import struct
import typing

try:
    from freesurfer_surface.version import __version__
except ImportError:  # pragma: no cover
    __version__ = None

Vertex = collections.namedtuple('Vertex', ['right', 'anterior', 'superior'])


class Surface:

    _MAGIC_NUMBER = b'\xff\xff\xfe'

    _TAG_CMDLINE = b'\x00\x00\x00\x03'
    _TAG_OLD_SURF_GEOM = b'\x00\x00\x00\x14'
    _TAG_OLD_USEREALRAS = b'\x00\x00\x00\x02'

    # TODO set locale
    _DATETIME_FORMAT = '%a %b %d %H:%M:%S %Y'

    def __init__(self):
        self.creator = None
        self.creation_datetime = None
        self.vertices = []
        self.triangles_vertex_indices = []
        # self._triangles = []
        self.using_old_real_ras = False
        self.volume_geometry_info = None
        self.command_lines = []

    @classmethod
    def _read_cmdlines(cls, stream: typing.BinaryIO) -> typing.Iterator[str]:
        while True:
            tag = stream.read(4)
            if not tag:
                return
            assert tag == cls._TAG_CMDLINE  # might be TAG_GROUP_AVG_SURFACE_AREA
            # TAGwrite
            # https://github.com/freesurfer/freesurfer/blob/release_6_0_0/utils/tags.c#L94
            str_length, = struct.unpack('>Q', stream.read(8))
            yield stream.read(str_length - 1)
            assert stream.read(1) == b'\x00'

    def _read_triangular(self, stream: typing.BinaryIO):
        assert stream.read(3) == self._MAGIC_NUMBER
        self.creator, creation_dt_str = re.match(rb'^created by (\w+) on (.* \d{4})\n',
                                                 stream.readline()).groups()
        self.creation_datetime = datetime.datetime.strptime(creation_dt_str.decode(),
                                                            self._DATETIME_FORMAT)
        assert stream.read(1) == b'\n'
        # fwriteInt
        # https://github.com/freesurfer/freesurfer/blob/release_6_0_0/utils/fio.c#L290
        vertices_num, triangles_num = struct.unpack('>II', stream.read(4 * 2))
        self.vertices = [Vertex(*struct.unpack('>fff', stream.read(4 * 3)))
                         for _ in range(vertices_num)]
        self.triangles_vertex_indices = [struct.unpack('>III', stream.read(4 * 3))
                                         for _ in range(triangles_num)]
        assert all(vertex_idx < vertices_num
                   for triangle_vertex_index in self.triangles_vertex_indices
                   for vertex_idx in triangle_vertex_index)
        assert stream.read(4) == self._TAG_OLD_USEREALRAS
        using_old_real_ras, = struct.unpack('>I', stream.read(4))
        assert using_old_real_ras in [0, 1], using_old_real_ras
        self.using_old_real_ras = bool(using_old_real_ras)
        assert stream.read(4) == self._TAG_OLD_SURF_GEOM
        # writeVolGeom
        # https://github.com/freesurfer/freesurfer/blob/release_6_0_0/utils/transform.c#L368
        self.volume_geometry_info = tuple(stream.readline() for _ in range(8))
        self.command_lines = list(self._read_cmdlines(stream))

    @classmethod
    def read_triangular(cls, surface_file_path: str) -> 'Surface':
        surface = cls()
        with open(surface_file_path, 'rb') as surface_file:
            # pylint: disable=protected-access
            surface._read_triangular(surface_file)
        return surface

    def _triangular_creation_datetime_strftime(self) -> bytes:
        fmt = self._DATETIME_FORMAT.replace('%d', '{:>2}'.format(self.creation_datetime.day))
        return self.creation_datetime.strftime(fmt).encode()

    def write_triangular(self, surface_file_path: str,
                         creation_datetime: typing.Optional[datetime.datetime] = None):
        if creation_datetime is None:
            creation_datetime = datetime.datetime.now()
        with open(surface_file_path, 'wb') as surface_file:
            surface_file.write(
                self._MAGIC_NUMBER
                + b'created by ' + self.creator
                + b' on ' + self._triangular_creation_datetime_strftime()
                + b'\n\n'
                + struct.pack('>II', len(self.vertices), len(self.triangles_vertex_indices))
            )
            for vertex in self.vertices:
                surface_file.write(struct.pack('>fff', *vertex))
            for triangle_vertex_indices in self.triangles_vertex_indices:
                surface_file.write(struct.pack('>III', *triangle_vertex_indices))
            surface_file.write(self._TAG_OLD_USEREALRAS
                               + struct.pack('>I', 1 if self.using_old_real_ras else 0))
            surface_file.write(self._TAG_OLD_SURF_GEOM
                               + b''.join(self.volume_geometry_info))
            for command_line in self.command_lines:
                surface_file.write(self._TAG_CMDLINE + struct.pack('>Q', len(command_line) + 1)
                                   + command_line + b'\0')
