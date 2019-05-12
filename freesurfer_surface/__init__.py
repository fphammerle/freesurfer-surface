"""
Python Library to Read and Write Surface Files in Freesurfer's TriangularSurface Format

compatible with Freesurfer's MRISwriteTriangularSurface()
https://github.com/freesurfer/freesurfer/blob/release_6_0_0/include/mrisurf.h#L1281
https://github.com/freesurfer/freesurfer/blob/release_6_0_0/utils/mrisurf.c
https://raw.githubusercontent.com/freesurfer/freesurfer/release_6_0_0/utils/mrisurf.c

Freesurfer
https://surfer.nmr.mgh.harvard.edu/

Edit Surface File
>>> from freesurfer_surface import Surface, Vertex, Triangle
>>>
>>> surface = Surface.read_triangular('bert/surf/lh.pial'))
>>>
>>> vertex_a = surface.add_vertex(Vertex(0.0, 0.0, 0.0))
>>> vertex_b = surface.add_vertex(Vertex(1.0, 1.0, 1.0))
>>> vertex_c = surface.add_vertex(Vertex(2.0, 2.0, 2.0))
>>> surface.triangles.append(Triangle((vertex_a, vertex_b, vertex_c)))
>>>
>>> surface.write_triangular('somewhere/else/lh.pial')

List Labels in Annotation File
>>> from freesurfer_surface import Annotation
>>>
>>> annotation = Annotation.read('bert/label/lh.aparc.annot')
>>> for label in annotation.labels.values():
>>>     print(label.index, label.hex_color_code, label.name)

Find Border of Labelled Region
>>> surface = Surface.read_triangular('bert/surf/lh.pial'))
>>> surface.load_annotation_file('bert/label/lh.aparc.annot')
>>> region, = filter(lambda l: l.name == 'precentral',
>>>                  annotation.labels.values())
>>> print(surface.find_label_border_polygonal_chains(region))
"""

import collections
import contextlib
import datetime
import itertools
import locale
import re
import struct
import typing

import numpy

try:
    from freesurfer_surface.version import __version__
except ImportError:  # pragma: no cover
    __version__ = None


class UnsupportedLocaleSettingError(locale.Error):
    pass


@contextlib.contextmanager
def setlocale(temporary_locale):
    primary_locale = locale.setlocale(locale.LC_ALL)
    try:
        yield locale.setlocale(locale.LC_ALL, temporary_locale)
    except locale.Error as exc:
        if str(exc) == 'unsupported locale setting':
            raise UnsupportedLocaleSettingError(temporary_locale)
        raise exc  # pragma: no cover
    finally:
        locale.setlocale(locale.LC_ALL, primary_locale)


Vertex = collections.namedtuple('Vertex', ['right', 'anterior', 'superior'])


class _PolygonalCircuit:

    _VERTEX_INDICES_TYPE = typing.Tuple[int]

    def __init__(self, vertex_indices: _VERTEX_INDICES_TYPE):
        self.vertex_indices = vertex_indices

    @property
    def vertex_indices(self):
        return self._vertex_indices

    @vertex_indices.setter
    def vertex_indices(self, indices: _VERTEX_INDICES_TYPE):
        # pylint: disable=attribute-defined-outside-init
        self._vertex_indices = tuple(indices)

    def _normalize(self) -> '_PolygonalCircuit':
        min_vertex_index_index = self.vertex_indices.index(min(self.vertex_indices))
        return type(self)(self.vertex_indices[min_vertex_index_index:]
                          + self.vertex_indices[:min_vertex_index_index])

    def __eq__(self, other: '_PolygonalCircuit') -> bool:
        # pylint: disable=protected-access
        return self._normalize().vertex_indices == other._normalize().vertex_indices

    def __hash__(self) -> int:
        # pylint: disable=protected-access
        return hash(self._normalize()._vertex_indices)


class _LineSegment(_PolygonalCircuit):

    # pylint: disable=no-member
    @_PolygonalCircuit.vertex_indices.setter
    def vertex_indices(self, indices: _PolygonalCircuit._VERTEX_INDICES_TYPE):
        assert len(indices) == 2
        # pylint: disable=attribute-defined-outside-init
        self._vertex_indices = tuple(indices)

    def __repr__(self) -> str:
        return '_LineSegment(vertex_indices={})'.format(self.vertex_indices)


class Triangle(_PolygonalCircuit):

    # pylint: disable=no-member
    @_PolygonalCircuit.vertex_indices.setter
    def vertex_indices(self, indices: _PolygonalCircuit._VERTEX_INDICES_TYPE):
        assert len(indices) == 3
        # pylint: disable=attribute-defined-outside-init
        self._vertex_indices = tuple(indices)

    def __repr__(self) -> str:
        return 'Triangle(vertex_indices={})'.format(self.vertex_indices)


class PolygonalChainsNotOverlapingError(ValueError):
    pass


class PolygonalChain:

    def __init__(self, vertex_indices: typing.Iterable[int]):
        self.vertex_indices = collections.deque(vertex_indices) # type: Deque[int]

    def __eq__(self, other: 'PolygonalChain') -> bool:
        return self.vertex_indices == other.vertex_indices

    def __repr__(self) -> str:
        return 'PolygonalChain(vertex_indices={})'.format(tuple(self.vertex_indices))

    def connect(self, other: 'PolygonalChain') -> None:
        if self.vertex_indices[-1] == other.vertex_indices[0]:
            self.vertex_indices.pop()
            self.vertex_indices.extend(other.vertex_indices)
        elif self.vertex_indices[-1] == other.vertex_indices[-1]:
            self.vertex_indices.pop()
            self.vertex_indices.extend(reversed(other.vertex_indices))
        elif self.vertex_indices[0] == other.vertex_indices[0]:
            self.vertex_indices.popleft()
            self.vertex_indices.extendleft(other.vertex_indices)
        elif self.vertex_indices[0] == other.vertex_indices[-1]:
            self.vertex_indices.popleft()
            self.vertex_indices.extendleft(reversed(other.vertex_indices))
        else:
            raise PolygonalChainsNotOverlapingError()

    def segments(self) -> typing.Iterable[_LineSegment]:
        indices = self.vertex_indices
        return map(_LineSegment, zip(indices, itertools.islice(indices, 1, len(indices))))


class Label:

    # pylint: disable=too-many-arguments
    def __init__(self, index: int, name: str, red: int,
                 green: int, blue: int, transparency: int):
        self.index = index  # type: int
        self.name = name  # type: str
        self.red = red  # type: int
        self.green = green  # type: int
        self.blue = blue  # type: int
        self.transparency = transparency  # type: int

    @property
    def color_code(self) -> int:
        if self.index == 0:  # unknown
            return 0
        return int.from_bytes((self.red, self.green, self.blue, self.transparency),
                              byteorder='little', signed=False)

    @property
    def hex_color_code(self) -> str:
        return '#{:02x}{:02x}{:02x}'.format(self.red, self.green, self.blue)

    def __str__(self) -> str:
        return 'Label(name={}, index={}, color={})'.format(
            self.name, self.index, self.hex_color_code)

    def __repr__(self) -> str:
        return str(self)


class Annotation:

    # pylint: disable=too-few-public-methods

    _TAG_OLD_COLORTABLE = b'\0\0\0\x01'

    def __init__(self):
        self.vertex_label_index = {}  # type: Dict[int, int]
        self.colortable_path = None  # type: Optional[bytes]
        self.labels = {}  # type: Dict[int, Label]

    @staticmethod
    def _read_label(stream: typing.BinaryIO) -> Label:
        index, name_length = struct.unpack('>II', stream.read(4 * 2))
        name = stream.read(name_length - 1).decode()
        assert stream.read(1) == b'\0'
        red, green, blue, transparency \
            = struct.unpack('>IIII', stream.read(4 * 4))
        return Label(index=index, name=name, red=red, green=green,
                     blue=blue, transparency=transparency)

    def _read(self, stream: typing.BinaryIO) -> None:
        # https://surfer.nmr.mgh.harvard.edu/fswiki/LabelsClutsAnnotationFiles
        annotations_num, = struct.unpack('>I', stream.read(4))
        annotations = [struct.unpack('>II', stream.read(4 * 2))
                       for _ in range(annotations_num)]
        assert stream.read(4) == self._TAG_OLD_COLORTABLE
        colortable_version, _, filename_length \
            = struct.unpack('>III', stream.read(4 * 3))
        assert colortable_version > 0  # new version
        self.colortable_path = stream.read(filename_length - 1)
        assert stream.read(1) == b'\0'
        labels_num, = struct.unpack('>I', stream.read(4))
        self.labels = {label.index: label for label
                       in (self._read_label(stream) for _ in range(labels_num))}
        label_index_by_color_code = {label.color_code: label.index
                                     for label in self.labels.values()}
        self.vertex_label_index = {vertex_index: label_index_by_color_code[color_code]
                                   for vertex_index, color_code in annotations}
        assert not stream.read(1)

    @classmethod
    def read(cls, annotation_file_path: str) -> 'Annotation':
        annotation = cls()
        with open(annotation_file_path, 'rb') as annotation_file:
            # pylint: disable=protected-access
            annotation._read(annotation_file)
        return annotation


class Surface:

    # pylint: disable=too-many-instance-attributes

    _MAGIC_NUMBER = b'\xff\xff\xfe'

    _TAG_CMDLINE = b'\x00\x00\x00\x03'
    _TAG_OLD_SURF_GEOM = b'\x00\x00\x00\x14'
    _TAG_OLD_USEREALRAS = b'\x00\x00\x00\x02'

    _DATETIME_FORMAT = '%a %b %d %H:%M:%S %Y'

    def __init__(self):
        self.creator = None  # type: Optional[bytes]
        self.creation_datetime = None  # type: Optional[datetime.datetime]
        self.vertices = []  # type: List[Vertex]
        self.triangles = []  # type: List[Triangle]
        self.using_old_real_ras = False  # type: bool
        self.volume_geometry_info = None  # type: Optional[Tuple[bytes]]
        self.command_lines = []  # type: List[bytes]
        self.annotation = None  # type: Optional[Annotation]

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
        with setlocale('C'):
            self.creation_datetime = datetime.datetime.strptime(creation_dt_str.decode(),
                                                                self._DATETIME_FORMAT)
        assert stream.read(1) == b'\n'
        # fwriteInt
        # https://github.com/freesurfer/freesurfer/blob/release_6_0_0/utils/fio.c#L290
        vertices_num, triangles_num = struct.unpack('>II', stream.read(4 * 2))
        self.vertices = [Vertex(*struct.unpack('>fff', stream.read(4 * 3)))
                         for _ in range(vertices_num)]
        self.triangles = [Triangle(struct.unpack('>III', stream.read(4 * 3)))
                          for _ in range(triangles_num)]
        assert all(vertex_idx < vertices_num
                   for triangle in self.triangles
                   for vertex_idx in triangle.vertex_indices)
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

    @classmethod
    def _triangular_strftime(cls, creation_datetime: datetime.datetime) -> bytes:
        padded_day = '{:>2}'.format(creation_datetime.day)
        fmt = cls._DATETIME_FORMAT.replace('%d', padded_day)
        with setlocale('C'):
            return creation_datetime.strftime(fmt).encode()

    def write_triangular(self, surface_file_path: str,
                         creation_datetime: typing.Optional[datetime.datetime] = None):
        if creation_datetime is None:
            creation_datetime = datetime.datetime.now()
        with open(surface_file_path, 'wb') as surface_file:
            surface_file.write(
                self._MAGIC_NUMBER
                + b'created by ' + self.creator
                + b' on ' + self._triangular_strftime(creation_datetime)
                + b'\n\n'
                + struct.pack('>II', len(self.vertices), len(self.triangles))
            )
            for vertex in self.vertices:
                surface_file.write(struct.pack('>fff', *vertex))
            for triangle in self.triangles:
                assert all(vertex_index < len(self.vertices)
                           for vertex_index in triangle.vertex_indices)
                surface_file.write(struct.pack('>III',
                                               *triangle.vertex_indices))
            surface_file.write(self._TAG_OLD_USEREALRAS
                               + struct.pack('>I', 1 if self.using_old_real_ras else 0))
            surface_file.write(self._TAG_OLD_SURF_GEOM
                               + b''.join(self.volume_geometry_info))
            for command_line in self.command_lines:
                surface_file.write(self._TAG_CMDLINE + struct.pack('>Q', len(command_line) + 1)
                                   + command_line + b'\0')

    def load_annotation_file(self, annotation_file_path: str) -> None:
        annotation = Annotation.read(annotation_file_path)
        assert len(annotation.vertex_label_index) <= len(self.vertices)
        assert max(annotation.vertex_label_index.keys()) < len(self.vertices)
        self.annotation = annotation

    def add_vertex(self, vertex: Vertex) -> int:
        self.vertices.append(vertex)
        return len(self.vertices) - 1

    def add_rectangle(self, vertex_indices: typing.Iterable[int]) -> typing.Iterable[int]:
        vertex_indices = list(vertex_indices)
        assert len(vertex_indices) == 3
        vertex_coords = [numpy.array(self.vertices[vertex_index])
                         for vertex_index in vertex_indices]
        vertex_coords.append(vertex_coords[0]
                             + vertex_coords[2] - vertex_coords[1])
        vertex_indices.append(self.add_vertex(Vertex(*vertex_coords[3])))
        self.triangles.append(Triangle(vertex_indices[:3]))
        self.triangles.append(Triangle(vertex_indices[2:]
                                       + vertex_indices[:1]))

    def _find_label_border_segments(self, label: Label) -> typing.Iterator[_LineSegment]:
        for triangle in self.triangles:
            border_vertex_indices = tuple(filter(
                lambda i: self.annotation.vertex_label_index[i] == label.index,
                triangle.vertex_indices,
            ))
            if len(border_vertex_indices) == 2:
                yield _LineSegment(border_vertex_indices)

    def find_label_border_polygonal_chains(self, label: Label) -> typing.Iterator[PolygonalChain]:
        segments = set(self._find_label_border_segments(label))
        available_chains = collections.deque(PolygonalChain(segment.vertex_indices)
                                             for segment in segments)
        # irrespective of its poor performance,
        # we keep this approach since it's easy to read and fast enough
        while available_chains:
            chain = available_chains.pop()
            last_chains_len = None
            while last_chains_len != len(available_chains):
                last_chains_len = len(available_chains)
                checked_chains = collections.deque()
                while available_chains:
                    potential_neighbour = available_chains.pop()
                    try:
                        chain.connect(potential_neighbour)
                    except PolygonalChainsNotOverlapingError:
                        checked_chains.append(potential_neighbour)
                available_chains = checked_chains
            assert all((segment in segments) for segment in chain.segments())
            yield chain
