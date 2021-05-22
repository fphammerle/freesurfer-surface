# freesurfer-surface - Read and Write Surface Files in Freesurfer’s TriangularSurface Format
#
# Copyright (C) 2020 Fabian Peter Hammerle <fabian@hammerle.me>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
import copy
import datetime
import itertools
import locale
import re
import struct
import typing

import numpy

try:
    from freesurfer_surface.version import __version__
except ModuleNotFoundError:
    # package is not installed
    __version__ = None


class UnsupportedLocaleSettingError(locale.Error):
    pass


@contextlib.contextmanager
def setlocale(temporary_locale):
    primary_locale = locale.setlocale(locale.LC_ALL)
    try:
        yield locale.setlocale(locale.LC_ALL, temporary_locale)
    except locale.Error as exc:
        if str(exc) == "unsupported locale setting":
            raise UnsupportedLocaleSettingError(temporary_locale) from exc
        raise exc  # pragma: no cover
    finally:
        locale.setlocale(locale.LC_ALL, primary_locale)


class Vertex(numpy.ndarray):
    def __new__(cls, right: float, anterior: float, superior: float):
        return numpy.array((right, anterior, superior), dtype=float).view(cls)

    @property
    def right(self) -> float:
        return self[0]

    @property
    def anterior(self) -> float:
        return self[1]

    @property
    def superior(self) -> float:
        return self[2]

    @property
    def __dict__(self) -> typing.Dict[str, typing.Any]:  # type: ignore
        # type hint: https://github.com/python/mypy/issues/6523#issuecomment-470733447
        return {
            "right": self.right,
            "anterior": self.anterior,
            "superior": self.superior,
        }

    def __format_coords(self) -> str:
        return ", ".join(
            "{}={}".format(name, getattr(self, name))
            for name in ["right", "anterior", "superior"]
        )

    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, self.__format_coords())

    def distance_mm(
        self, others: typing.Union["Vertex", typing.Iterable["Vertex"], numpy.ndarray]
    ) -> numpy.ndarray:
        if isinstance(others, Vertex):
            others = others.reshape((1, 3))
        return numpy.linalg.norm(self - others, axis=1)


class PolygonalCircuit:
    def __init__(self, vertex_indices: typing.Iterable[int]):
        self._vertex_indices = tuple(vertex_indices)
        assert all(isinstance(idx, int) for idx in self._vertex_indices)

    @property
    def vertex_indices(self):
        return self._vertex_indices

    def _normalize(self) -> "PolygonalCircuit":
        vertex_indices = collections.deque(self.vertex_indices)
        vertex_indices.rotate(-numpy.argmin(self.vertex_indices))
        if len(vertex_indices) > 2 and vertex_indices[-1] < vertex_indices[1]:
            vertex_indices.reverse()
            vertex_indices.rotate(1)
        return type(self)(vertex_indices)

    def __eq__(self, other: object) -> bool:
        # pylint: disable=protected-access
        return (
            isinstance(other, PolygonalCircuit)
            and self._normalize().vertex_indices == other._normalize().vertex_indices
        )

    def __hash__(self) -> int:
        # pylint: disable=protected-access
        return hash(self._normalize()._vertex_indices)

    def adjacent_vertex_indices(
        self, vertices_num: int = 2
    ) -> typing.Iterable[typing.Tuple[int, ...]]:
        vertex_indices_cycle = list(
            itertools.islice(
                itertools.cycle(self.vertex_indices),
                0,
                len(self.vertex_indices) + vertices_num - 1,
            )
        )
        return zip(
            *(
                itertools.islice(
                    vertex_indices_cycle, offset, len(self.vertex_indices) + offset
                )
                for offset in range(vertices_num)
            )
        )


class LineSegment(PolygonalCircuit):
    def __init__(self, indices: typing.Iterable[int]):
        super().__init__(indices)
        assert len(self.vertex_indices) == 2

    def __repr__(self) -> str:
        return "LineSegment(vertex_indices={})".format(self.vertex_indices)


class Triangle(PolygonalCircuit):
    def __init__(self, indices: typing.Iterable[int]):
        super().__init__(indices)
        assert len(self.vertex_indices) == 3

    def __repr__(self) -> str:
        return "Triangle(vertex_indices={})".format(self.vertex_indices)


class PolygonalChainsNotOverlapingError(ValueError):
    pass


class PolygonalChain:
    def __init__(self, vertex_indices: typing.Iterable[int]):
        self.vertex_indices: typing.Deque[int] = collections.deque(vertex_indices)

    def normalized(self) -> "PolygonalChain":
        vertex_indices = list(self.vertex_indices)
        min_index = vertex_indices.index(min(vertex_indices))
        indices_min_first = vertex_indices[min_index:] + vertex_indices[:min_index]
        if indices_min_first[1] < indices_min_first[-1]:
            return PolygonalChain(indices_min_first)
        return PolygonalChain(indices_min_first[0:1] + indices_min_first[-1:0:-1])

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PolygonalChain) and (
            self.vertex_indices == other.vertex_indices
            or self.normalized().vertex_indices == other.normalized().vertex_indices
        )

    def __repr__(self) -> str:
        return "PolygonalChain(vertex_indices={})".format(tuple(self.vertex_indices))

    def connect(self, other: "PolygonalChain") -> None:
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

    def adjacent_vertex_indices(
        self, vertices_num: int = 2
    ) -> typing.Iterator[typing.Tuple[int, ...]]:
        return zip(
            *(
                itertools.islice(self.vertex_indices, offset, len(self.vertex_indices))
                for offset in range(vertices_num)
            )
        )

    def segments(self) -> typing.Iterable[LineSegment]:
        return map(LineSegment, self.adjacent_vertex_indices(2))


class Label:

    # pylint: disable=too-many-arguments
    def __init__(
        self, index: int, name: str, red: int, green: int, blue: int, transparency: int
    ):
        self.index: int = index
        self.name: str = name
        self.red: int = red
        self.green: int = green
        self.blue: int = blue
        self.transparency: int = transparency

    @property
    def color_code(self) -> int:
        if self.index == 0:  # unknown
            return 0
        return int.from_bytes(
            (self.red, self.green, self.blue, self.transparency),
            byteorder="little",
            signed=False,
        )

    @property
    def hex_color_code(self) -> str:
        return "#{:02x}{:02x}{:02x}".format(self.red, self.green, self.blue)

    def __str__(self) -> str:
        return "Label(name={}, index={}, color={})".format(
            self.name, self.index, self.hex_color_code
        )

    def __repr__(self) -> str:
        return str(self)


class Annotation:

    # pylint: disable=too-few-public-methods

    _TAG_OLD_COLORTABLE = b"\0\0\0\x01"

    def __init__(self):
        self.vertex_label_index: typing.Dict[int, int] = {}
        self.colortable_path: typing.Optional[bytes] = None
        self.labels: typing.Dict[int, Label] = {}

    @staticmethod
    def _read_label(stream: typing.BinaryIO) -> Label:
        index, name_length = struct.unpack(">II", stream.read(4 * 2))
        name = stream.read(name_length - 1).decode()
        assert stream.read(1) == b"\0"
        red, green, blue, transparency = struct.unpack(">IIII", stream.read(4 * 4))
        return Label(
            index=index,
            name=name,
            red=red,
            green=green,
            blue=blue,
            transparency=transparency,
        )

    def _read(self, stream: typing.BinaryIO) -> None:
        # https://surfer.nmr.mgh.harvard.edu/fswiki/LabelsClutsAnnotationFiles
        (annotations_num,) = struct.unpack(">I", stream.read(4))
        annotations = [
            struct.unpack(">II", stream.read(4 * 2)) for _ in range(annotations_num)
        ]
        assert stream.read(4) == self._TAG_OLD_COLORTABLE
        colortable_version, _, filename_length = struct.unpack(
            ">III", stream.read(4 * 3)
        )
        assert colortable_version > 0  # new version
        self.colortable_path = stream.read(filename_length - 1)
        assert stream.read(1) == b"\0"
        (labels_num,) = struct.unpack(">I", stream.read(4))
        self.labels = {
            label.index: label
            for label in (self._read_label(stream) for _ in range(labels_num))
        }
        label_index_by_color_code = {
            label.color_code: label.index for label in self.labels.values()
        }
        self.vertex_label_index = {
            vertex_index: label_index_by_color_code[color_code]
            for vertex_index, color_code in annotations
        }
        assert not stream.read(1)

    @classmethod
    def read(cls, annotation_file_path: str) -> "Annotation":
        annotation = cls()
        with open(annotation_file_path, "rb") as annotation_file:
            # pylint: disable=protected-access
            annotation._read(annotation_file)
        return annotation


class Surface:

    # pylint: disable=too-many-instance-attributes

    _MAGIC_NUMBER = b"\xff\xff\xfe"

    _TAG_CMDLINE = b"\x00\x00\x00\x03"
    _TAG_OLD_SURF_GEOM = b"\x00\x00\x00\x14"
    _TAG_OLD_USEREALRAS = b"\x00\x00\x00\x02"

    _DATETIME_FORMAT = "%a %b %d %H:%M:%S %Y"

    def __init__(self):
        self.creator: bytes = b"pypi.org/project/freesurfer-surface/"
        self.creation_datetime: typing.Optional[datetime.datetime] = None
        self.vertices: typing.List[Vertex] = []
        self.triangles: typing.List[Triangle] = []
        self.using_old_real_ras: bool = False
        self.volume_geometry_info: typing.Optional[typing.Tuple[bytes, ...]] = None
        self.command_lines: typing.List[bytes] = []
        self.annotation: typing.Optional[Annotation] = None

    @classmethod
    def _read_cmdlines(cls, stream: typing.BinaryIO) -> typing.Iterator[bytes]:
        while True:
            tag = stream.read(4)
            if not tag:
                return
            assert tag == cls._TAG_CMDLINE  # might be TAG_GROUP_AVG_SURFACE_AREA
            # TAGwrite
            # https://github.com/freesurfer/freesurfer/blob/release_6_0_0/utils/tags.c#L94
            (str_length,) = struct.unpack(">Q", stream.read(8))
            yield stream.read(str_length - 1)
            assert stream.read(1) == b"\x00"

    def _read_triangular(self, stream: typing.BinaryIO):
        assert stream.read(3) == self._MAGIC_NUMBER
        creation_match = re.match(
            rb"^created by (\w+) on (.* \d{4})\n", stream.readline()
        )
        assert creation_match
        self.creator, creation_dt_str = creation_match.groups()
        with setlocale("C"):
            self.creation_datetime = datetime.datetime.strptime(
                creation_dt_str.decode(), self._DATETIME_FORMAT
            )
        assert stream.read(1) == b"\n"
        # fwriteInt
        # https://github.com/freesurfer/freesurfer/blob/release_6_0_0/utils/fio.c#L290
        vertices_num, triangles_num = struct.unpack(">II", stream.read(4 * 2))
        self.vertices = [
            Vertex(*struct.unpack(">fff", stream.read(4 * 3)))
            for _ in range(vertices_num)
        ]
        self.triangles = [
            Triangle(struct.unpack(">III", stream.read(4 * 3)))
            for _ in range(triangles_num)
        ]
        assert all(
            vertex_idx < vertices_num
            for triangle in self.triangles
            for vertex_idx in triangle.vertex_indices
        )
        assert stream.read(4) == self._TAG_OLD_USEREALRAS
        (using_old_real_ras,) = struct.unpack(">I", stream.read(4))
        assert using_old_real_ras in [0, 1], using_old_real_ras
        self.using_old_real_ras = bool(using_old_real_ras)
        assert stream.read(4) == self._TAG_OLD_SURF_GEOM
        # writeVolGeom
        # https://github.com/freesurfer/freesurfer/blob/release_6_0_0/utils/transform.c#L368
        self.volume_geometry_info = tuple(stream.readline() for _ in range(8))
        self.command_lines = list(self._read_cmdlines(stream))

    @classmethod
    def read_triangular(cls, surface_file_path: str) -> "Surface":
        surface = cls()
        with open(surface_file_path, "rb") as surface_file:
            # pylint: disable=protected-access
            surface._read_triangular(surface_file)
        return surface

    @classmethod
    def _triangular_strftime(cls, creation_datetime: datetime.datetime) -> bytes:
        padded_day = "{:>2}".format(creation_datetime.day)
        fmt = cls._DATETIME_FORMAT.replace("%d", padded_day)
        with setlocale("C"):
            return creation_datetime.strftime(fmt).encode()

    def write_triangular(
        self,
        surface_file_path: str,
        creation_datetime: typing.Optional[datetime.datetime] = None,
    ):
        if creation_datetime is None:
            creation_datetime = datetime.datetime.now()
        with open(surface_file_path, "wb") as surface_file:
            surface_file.write(
                self._MAGIC_NUMBER
                + b"created by "
                + self.creator
                + b" on "
                + self._triangular_strftime(creation_datetime)
                + b"\n\n"
                + struct.pack(">II", len(self.vertices), len(self.triangles))
            )
            for vertex in self.vertices:
                surface_file.write(struct.pack(">fff", *vertex))
            for triangle in self.triangles:
                assert all(
                    vertex_index < len(self.vertices)
                    for vertex_index in triangle.vertex_indices
                )
                surface_file.write(struct.pack(">III", *triangle.vertex_indices))
            surface_file.write(
                self._TAG_OLD_USEREALRAS
                + struct.pack(">I", 1 if self.using_old_real_ras else 0)
            )
            if not self.volume_geometry_info:
                raise ValueError(
                    "Missing geometry information (set attribute `volume_geometry_info`)"
                )
            surface_file.write(
                self._TAG_OLD_SURF_GEOM + b"".join(self.volume_geometry_info)
            )
            for command_line in self.command_lines:
                surface_file.write(
                    self._TAG_CMDLINE
                    + struct.pack(">Q", len(command_line) + 1)
                    + command_line
                    + b"\0"
                )

    def load_annotation_file(self, annotation_file_path: str) -> None:
        annotation = Annotation.read(annotation_file_path)
        assert len(annotation.vertex_label_index) <= len(self.vertices)
        assert max(annotation.vertex_label_index.keys()) < len(self.vertices)
        self.annotation = annotation

    def add_vertex(self, vertex: Vertex) -> int:
        self.vertices.append(vertex)
        return len(self.vertices) - 1

    def add_rectangle(self, vertex_indices: typing.Iterable[int]) -> None:
        vertex_indices = list(vertex_indices)
        if len(vertex_indices) == 3:
            vertex_indices.append(
                self.add_vertex(
                    self.vertices[vertex_indices[0]]
                    + self.vertices[vertex_indices[2]]
                    - self.vertices[vertex_indices[1]]
                )
            )
        assert len(vertex_indices) == 4
        self.triangles.append(Triangle(vertex_indices[:3]))
        self.triangles.append(Triangle(vertex_indices[2:] + vertex_indices[:1]))

    def _triangle_count_by_adjacent_vertex_indices(
        self,
    ) -> typing.Dict[int, typing.DefaultDict[int, int]]:
        counts: typing.Dict[int, typing.DefaultDict[int, int]] = {
            vertex_index: collections.defaultdict(lambda: 0)
            for vertex_index in range(len(self.vertices))
        }
        for triangle in self.triangles:
            for vertex_index_pair in triangle.adjacent_vertex_indices(2):
                counts[vertex_index_pair[0]][vertex_index_pair[1]] += 1
                counts[vertex_index_pair[1]][vertex_index_pair[0]] += 1
        return counts

    def find_borders(self) -> typing.Iterator[PolygonalCircuit]:
        border_neighbours = {}
        for (
            vertex_index,
            neighbour_counts,
        ) in self._triangle_count_by_adjacent_vertex_indices().items():
            if not neighbour_counts:
                yield PolygonalCircuit((vertex_index,))
            else:
                neighbours = [
                    neighbour_index
                    for neighbour_index, counts in neighbour_counts.items()
                    if counts != 2
                ]
                if neighbours:
                    assert len(neighbours) % 2 == 0, (vertex_index, neighbour_counts)
                    border_neighbours[vertex_index] = neighbours
        while border_neighbours:
            vertex_index, neighbour_indices = border_neighbours.popitem()
            cycle_indices = [vertex_index]
            border_neighbours[vertex_index] = neighbour_indices[1:]
            vertex_index = neighbour_indices[0]
            while vertex_index != cycle_indices[0]:
                neighbour_indices = border_neighbours.pop(vertex_index)
                neighbour_indices.remove(cycle_indices[-1])
                cycle_indices.append(vertex_index)
                if len(neighbour_indices) > 1:
                    border_neighbours[vertex_index] = neighbour_indices[1:]
                vertex_index = neighbour_indices[0]
            assert vertex_index in border_neighbours, (
                vertex_index,
                cycle_indices,
                border_neighbours,
            )
            final_neighbour_indices = border_neighbours.pop(vertex_index)
            assert final_neighbour_indices == [cycle_indices[-1]], (
                vertex_index,
                final_neighbour_indices,
                cycle_indices,
            )
            yield PolygonalCircuit(cycle_indices)

    def _get_vertex_label_index(self, vertex_index: int) -> typing.Optional[int]:
        if not self.annotation:
            raise RuntimeError(
                "Missing annotation (call method `load_annotation_file` first)."
            )
        return self.annotation.vertex_label_index.get(vertex_index, None)

    def _find_label_border_segments(self, label: Label) -> typing.Iterator[LineSegment]:
        for triangle in self.triangles:
            border_vertex_indices = tuple(
                filter(
                    lambda i: self._get_vertex_label_index(i) == label.index,
                    triangle.vertex_indices,
                )
            )
            if len(border_vertex_indices) == 2:
                yield LineSegment(border_vertex_indices)

    _VertexSubindex = typing.Tuple[int, int]

    @classmethod
    def _duplicate_border(
        cls,
        neighbour_indices: typing.DefaultDict[
            _VertexSubindex, typing.Set[_VertexSubindex]
        ],
        previous_index: _VertexSubindex,
        current_index: _VertexSubindex,
        junction_counter: int,
    ) -> None:
        split_index = (current_index[0], junction_counter)
        neighbour_indices[previous_index].add(split_index)
        neighbour_indices[split_index].add(previous_index)
        next_index, *extra_indices = filter(
            lambda i: i != previous_index, neighbour_indices[current_index]
        )
        if extra_indices:
            neighbour_indices[next_index].add(split_index)
            neighbour_indices[split_index].add(next_index)
            neighbour_indices[next_index].remove(current_index)
            neighbour_indices[current_index].remove(next_index)
            return
        cls._duplicate_border(
            neighbour_indices=neighbour_indices,
            previous_index=split_index,
            current_index=next_index,
            junction_counter=junction_counter,
        )

    def find_label_border_polygonal_chains(
        self, label: Label
    ) -> typing.Iterator[PolygonalChain]:
        neighbour_indices: (  # type: ignore
            typing.DefaultDict[self._VertexSubindex, typing.Set[self._VertexSubindex]]
        ) = collections.defaultdict(set)
        for segment in self._find_label_border_segments(label):
            vertex_indices = [(i, 0) for i in segment.vertex_indices]
            neighbour_indices[vertex_indices[0]].add(vertex_indices[1])
            neighbour_indices[vertex_indices[1]].add(vertex_indices[0])
        junction_counter = 0
        found_leaf = True
        while found_leaf:
            found_leaf = False
            for leaf_index, leaf_neighbour_indices in neighbour_indices.items():
                if len(leaf_neighbour_indices) == 1:
                    found_leaf = True
                    junction_counter += 1
                    self._duplicate_border(
                        neighbour_indices=neighbour_indices,
                        previous_index=leaf_index,
                        # pylint: disable=stop-iteration-return; false positive, has 1 item
                        current_index=next(iter(leaf_neighbour_indices)),
                        junction_counter=junction_counter,
                    )
                    break
        assert all(len(n) == 2 for n in neighbour_indices.values()), neighbour_indices
        while neighbour_indices:
            # pylint: disable=stop-iteration-return; has >= 1 item
            chain = collections.deque([next(iter(neighbour_indices.keys()))])
            chain.append(neighbour_indices[chain[0]].pop())
            neighbour_indices[chain[1]].remove(chain[0])
            while chain[0] != chain[-1]:
                previous_index = chain[-1]
                next_index = neighbour_indices[previous_index].pop()
                neighbour_indices[next_index].remove(previous_index)
                chain.append(next_index)
                assert not neighbour_indices[previous_index], neighbour_indices[
                    previous_index
                ]
                del neighbour_indices[previous_index]
            assert not neighbour_indices[chain[0]], neighbour_indices[chain[0]]
            del neighbour_indices[chain[0]]
            chain.pop()
            yield PolygonalChain(v[0] for v in chain)

    def _unused_vertices(self) -> typing.Set[int]:
        vertex_indices = set(range(len(self.vertices)))
        for triangle in self.triangles:
            for vertex_index in triangle.vertex_indices:
                vertex_indices.discard(vertex_index)
        return vertex_indices

    def remove_unused_vertices(self) -> None:
        vertex_index_conversion = [0] * len(self.vertices)
        for vertex_index in sorted(self._unused_vertices(), reverse=True):
            del self.vertices[vertex_index]
            vertex_index_conversion[vertex_index] -= 1
        vertex_index_conversion = numpy.cumsum(vertex_index_conversion)
        for triangle_index in range(len(self.triangles)):
            self.triangles[triangle_index] = Triangle(
                map(
                    lambda i: i + int(vertex_index_conversion[i]),
                    self.triangles[triangle_index].vertex_indices,
                )
            )

    def select_vertices(
        self, vertex_indices: typing.Iterable[int]
    ) -> typing.List[Vertex]:
        return [self.vertices[idx] for idx in vertex_indices]

    @staticmethod
    def unite(surfaces: typing.Iterable["Surface"]) -> "Surface":
        surfaces_iter = iter(surfaces)
        union = copy.deepcopy(next(surfaces_iter))
        for surface in surfaces_iter:
            vertex_index_offset = len(union.vertices)
            union.vertices.extend(surface.vertices)
            union.triangles.extend(
                Triangle(
                    vertex_idx + vertex_index_offset
                    for vertex_idx in triangle.vertex_indices
                )
                for triangle in surface.triangles
            )
        return union
