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

import copy
import datetime
import unittest.mock

import numpy
import pytest

from conftest import ANNOTATION_FILE_PATH, SURFACE_FILE_PATH
from freesurfer_surface import (
    Annotation,
    LineSegment,
    PolygonalCircuit,
    Surface,
    Triangle,
    Vertex,
    setlocale,
)

# pylint: disable=protected-access


def test_read_triangular():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    assert surface.creator == b"fabianpeter"
    assert surface.creation_datetime == datetime.datetime(2019, 5, 9, 22, 37, 41)
    assert len(surface.vertices) == 155622
    assert len(surface.triangles) == 311240
    assert not surface.using_old_real_ras
    assert surface.volume_geometry_info == (
        b"valid = 1  # volume info valid\n",
        b"filename = ../mri/filled-pretess255.mgz\n",
        b"volume = 256 256 256\n",
        b"voxelsize = 1.000000000000000e+00 1.000000000000000e+00 1.000000000000000e+00\n",
        b"xras   = -1.000000000000000e+00 0.000000000000000e+00 1.862645149230957e-09\n",
        b"yras   = 0.000000000000000e+00 -6.655682227574289e-09 -1.000000000000000e+00\n",
        b"zras   = 0.000000000000000e+00 1.000000000000000e+00 -8.300048648379743e-09\n",
        b"cras   = -2.773597717285156e+00 1.566547393798828e+01 -7.504364013671875e+00\n",
    )
    assert surface.command_lines == [
        b"mris_remove_intersection ../surf/lh.orig ../surf/lh.orig"
        b" ProgramVersion: $Name: stable6 $"
        b"  TimeStamp: 2019/05/09-17:42:36-GMT"
        b"  BuildTimeStamp: Jan 18 2017 16:38:58"
        b"  CVS: $Id: mris_remove_intersection.c,v 1.6 2011/03/02 00:04:32 nicks Exp $"
        b"  User: fabianpeter"
        b"  Machine: host12345"
        b"  Platform: Linux"
        b"  PlatformVersion: 4.15.0-46-generic"
        b"  CompilerName: GCC"
        b"  CompilerVersion: 40400"
        b"  ",
        b"mris_make_surfaces -orig_white white.preaparc -orig_pial white.preaparc"
        b" -aseg ../mri/aseg.presurf -mgz -T1 brain.finalsurfs"
        b" fabian20190509 lh ProgramVersion: $Name:  $"
        b"  TimeStamp: 2019/05/09-20:27:28-GMT"
        b"  BuildTimeStamp: Jan 18 2017 16:38:58"
        b"  CVS: $Id: mris_make_surfaces.c,v 1.164.2.4 2016/12/13 22:26:32 zkaufman Exp $"
        b"  User: fabianpeter"
        b"  Machine: host12345"
        b"  Platform: Linux"
        b"  PlatformVersion: 4.15.0-46-generic"
        b"  CompilerName: GCC"
        b"  CompilerVersion: 40400"
        b"  ",
    ]


def test_read_triangular_locale():
    with setlocale("de_AT.utf8"):
        surface = Surface.read_triangular(SURFACE_FILE_PATH)
    assert surface.creation_datetime == datetime.datetime(2019, 5, 9, 22, 37, 41)


@pytest.mark.parametrize(
    ("creation_datetime", "expected_str"),
    [
        (datetime.datetime(2019, 5, 9, 22, 37, 41), b"Thu May  9 22:37:41 2019"),
        (datetime.datetime(2019, 4, 24, 23, 29, 22), b"Wed Apr 24 23:29:22 2019"),
    ],
)
def test_triangular_strftime(creation_datetime, expected_str):
    # pylint: disable=protected-access
    assert expected_str == Surface._triangular_strftime(creation_datetime)


def test_write_triangular_missing_geometry(tmpdir):
    surface = Surface()
    with pytest.raises(ValueError, match=r"\bvolume_geometry_info\b"):
        surface.write_triangular(tmpdir.join("surface").strpath)


def test_write_triangular_empty(tmpdir):
    surface = Surface()
    surface.volume_geometry_info = (
        b"valid = 1  # volume info valid\n",
        b"filename = ../mri/filled-pretess255.mgz\n",
        b"volume = 256 256 256\n",
        b"voxelsize = 1.000000000000000e+00 1.000000000000000e+00 1.000000000000000e+00\n",
        b"xras   = -1.000000000000000e+00 0.000000000000000e+00 1.862645149230957e-09\n",
        b"yras   = 0.000000000000000e+00 -6.655682227574289e-09 -1.000000000000000e+00\n",
        b"zras   = 0.000000000000000e+00 1.000000000000000e+00 -8.300048648379743e-09\n",
        b"cras   = -2.773597717285156e+00 1.566547393798828e+01 -7.504364013671875e+00\n",
    )
    output_path = tmpdir.join("surface").strpath
    surface.write_triangular(
        output_path,
        creation_datetime=datetime.datetime(2021, 5, 22, 7, 52, 53),  # timezone-unaware
    )
    with open(output_path, "rb") as output_file:
        assert (
            output_file.read() == b"\xff\xff\xfe"
            b"created by pypi.org/project/freesurfer-surface/ on Sat May 22 07:52:53 2021\n\n"
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x14"
            b"valid = 1  # volume info valid\n"
            b"filename = ../mri/filled-pretess255.mgz\n"
            b"volume = 256 256 256\n"
            b"voxelsize = 1.000000000000000e+00 1.000000000000000e+00 1.000000000000000e+00\n"
            b"xras   = -1.000000000000000e+00 0.000000000000000e+00 1.862645149230957e-09\n"
            b"yras   = 0.000000000000000e+00 -6.655682227574289e-09 -1.000000000000000e+00\n"
            b"zras   = 0.000000000000000e+00 1.000000000000000e+00 -8.300048648379743e-09\n"
            b"cras   = -2.773597717285156e+00 1.566547393798828e+01 -7.504364013671875e+00\n"
        )


def test_read_write_triangular_same(tmpdir):
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    output_path = tmpdir.join("surface").strpath
    surface.write_triangular(output_path, creation_datetime=surface.creation_datetime)
    with open(output_path, "rb") as output_file:
        with open(SURFACE_FILE_PATH, "rb") as expected_file:
            assert expected_file.read() == output_file.read()


def test_read_write_datetime(tmpdir):
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    original_creation_datetime = surface.creation_datetime
    output_path = tmpdir.join("surface").strpath
    surface.write_triangular(output_path)
    assert original_creation_datetime == surface.creation_datetime
    new_surface = Surface.read_triangular(output_path)
    assert new_surface.creation_datetime > original_creation_datetime
    assert datetime.datetime.now() > new_surface.creation_datetime
    assert (
        datetime.datetime.now() - new_surface.creation_datetime
    ) < datetime.timedelta(seconds=20)


def test_write_read_triangular_same(tmpdir):
    expected_surface = Surface()
    expected_surface.creator = b"pytest"
    expected_surface.creation_datetime = datetime.datetime.now().replace(microsecond=0)
    expected_surface.vertices = [
        Vertex(0.0, 0.0, 0.0),
        Vertex(1.0, 2.0, 3.0),
        Vertex(2.0, 4.0, 6.0),
        Vertex(3.0, 5.0, 7.0),
    ]
    expected_surface.triangles = [
        Triangle((0, 1, 2)),
        Triangle((0, 1, 3)),
        Triangle((3, 2, 1)),
    ]
    expected_surface.using_old_real_ras = False
    expected_surface.volume_geometry_info = tuple(b"?\n" for _ in range(8))
    expected_surface.command_lines = [b"?", b"!"]
    output_path = tmpdir.join("surface").strpath
    expected_surface.write_triangular(
        output_path, creation_datetime=expected_surface.creation_datetime
    )
    resulted_surface = Surface.read_triangular(output_path)
    assert numpy.array_equal(expected_surface.vertices, resulted_surface.vertices)
    expected_surface.vertices = resulted_surface.vertices = []
    assert vars(expected_surface) == vars(resulted_surface)


def test_write_triangular_same_locale(tmpdir):
    surface = Surface()
    surface.creator = b"pytest"
    surface.volume_geometry_info = tuple(b"?" for _ in range(8))
    creation_datetime = datetime.datetime(2018, 12, 31, 21, 42)
    output_path = tmpdir.join("surface").strpath
    with setlocale("de_AT.utf8"):
        surface.write_triangular(output_path, creation_datetime=creation_datetime)
    resulted_surface = Surface.read_triangular(output_path)
    assert resulted_surface.creation_datetime == creation_datetime
    with open(output_path, "rb") as output_file:
        assert (
            output_file.read()
            .split(b" on ")[1]
            .startswith(b"Mon Dec 31 21:42:00 2018\n")
        )


def test_load_annotation():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    assert not surface.annotation
    surface.load_annotation_file(ANNOTATION_FILE_PATH)
    assert isinstance(surface.annotation, Annotation)
    assert len(surface.annotation.vertex_label_index) == 155622
    assert surface.annotation.vertex_label_index[0] == 5


def test_add_vertex():
    surface = Surface()
    assert not surface.vertices
    assert surface.add_vertex(Vertex(1.0, 1.5, 2.0)) == 0
    assert len(surface.vertices) == 1
    assert surface.vertices[0].anterior == pytest.approx(1.5)
    assert surface.add_vertex(Vertex(-3.0, 0.0, 4.0)) == 1
    assert len(surface.vertices) == 2
    assert surface.vertices[1].right == pytest.approx(-3.0)


@pytest.mark.parametrize(
    "vertices_coords",
    [
        ((0, 0, 0), (2, 4, 0), (2, 4, 3)),
        ((0, 0, 0), (2, 4, 0), (2, 4, 3), (0, 0, 3)),
        ((1, 1, 0), (3, 5, 0), (3, 5, 3), (1, 1, 3)),
        ((1, 1, 7), (3, 5, 7), (3, 5, 3), (1, 1, 3)),
        ((1, 1, 1), (3, 5, 7), (3, 5, 9), (1, 1, 3)),
        ((3, 5, 7), (1, 1, 1), (1, 1, 3)),
        ((3, 5, 7), (1, 1, 1), (1, 1, 3), (3, 5, 9)),
    ],
)
def test_add_rectangle(vertices_coords):
    surface = Surface()
    for vertex_coords in vertices_coords:
        surface.add_vertex(Vertex(*(float(c) for c in vertex_coords)))
    surface.add_rectangle(range(len(vertices_coords)))
    assert len(surface.vertices) == 4
    assert len(surface.triangles) == 2
    assert surface.triangles[0].vertex_indices == (0, 1, 2)
    assert surface.triangles[1].vertex_indices == (2, 3, 0)


@pytest.mark.parametrize(
    ("vertices_coords", "expected_extra_vertex_coords"),
    [
        (((0, 0, 0), (2, 4, 0), (2, 4, 3)), (0, 0, 3)),
        (((1, 1, 0), (3, 5, 0), (3, 5, 3)), (1, 1, 3)),
        (((1, 1, 7), (3, 5, 7), (3, 5, 3)), (1, 1, 3)),
        (((1, 1, 1), (3, 5, 7), (3, 5, 9)), (1, 1, 3)),
        (((3, 5, 7), (1, 1, 1), (1, 1, 3)), (3, 5, 9)),
    ],
)
def test_add_rectangle_3(vertices_coords, expected_extra_vertex_coords):
    surface = Surface()
    for vertex_coords in vertices_coords:
        surface.add_vertex(Vertex(*(float(c) for c in vertex_coords)))
    surface.add_rectangle(range(3))
    assert tuple(surface.vertices[3]) == pytest.approx(expected_extra_vertex_coords)


def test__triangle_count_by_adjacent_vertex_indices_empty():
    surface = Surface()
    assert surface._triangle_count_by_adjacent_vertex_indices() == {}


def test__triangle_count_by_adjacent_vertex_indices_none():
    surface = Surface()
    surface.vertices.append(Vertex(1, 0, 0))
    surface.vertices.append(Vertex(2, 0, 0))
    surface.vertices.append(Vertex(3, 0, 0))
    assert surface._triangle_count_by_adjacent_vertex_indices() == {0: {}, 1: {}, 2: {}}


def test__triangle_count_by_adjacent_vertex_indices_single():
    surface = Surface()
    surface.triangles.append(
        Triangle([surface.add_vertex(Vertex(i, 0, 0)) for i in range(3)])
    )
    assert surface._triangle_count_by_adjacent_vertex_indices() == {
        0: {1: 1, 2: 1},
        1: {0: 1, 2: 1},
        2: {0: 1, 1: 1},
    }


def test__triangle_count_by_adjacent_vertex_indices_multiple():
    surface = Surface()
    for i in range(5):
        surface.add_vertex(Vertex(i, 0, 0))
    surface.triangles.append(Triangle((0, 1, 2)))
    surface.triangles.append(Triangle((3, 1, 2)))
    assert surface._triangle_count_by_adjacent_vertex_indices() == {
        0: {1: 1, 2: 1},
        1: {0: 1, 2: 2, 3: 1},
        2: {0: 1, 1: 2, 3: 1},
        3: {1: 1, 2: 1},
        4: {},
    }
    surface.triangles.append(Triangle((3, 4, 2)))
    assert surface._triangle_count_by_adjacent_vertex_indices() == {
        0: {1: 1, 2: 1},
        1: {0: 1, 2: 2, 3: 1},
        2: {0: 1, 1: 2, 3: 2, 4: 1},
        3: {1: 1, 2: 2, 4: 1},
        4: {2: 1, 3: 1},
    }
    surface.triangles.append(Triangle((3, 0, 2)))
    assert surface._triangle_count_by_adjacent_vertex_indices() == {
        0: {1: 1, 2: 2, 3: 1},
        1: {0: 1, 2: 2, 3: 1},
        2: {0: 2, 1: 2, 3: 3, 4: 1},
        3: {0: 1, 1: 1, 2: 3, 4: 1},
        4: {2: 1, 3: 1},
    }


def test__triangle_count_by_adjacent_vertex_indices_real():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    counts = surface._triangle_count_by_adjacent_vertex_indices()
    assert len(counts) == len(surface.vertices)
    assert all(counts.values())
    assert all(
        count == 2
        for vertex_counts in counts.values()
        for count in vertex_counts.values()
    )
    assert (
        sum(
            count
            for vertex_counts in counts.values()
            for count in vertex_counts.values()
        )
        == len(surface.triangles) * 6
    )


def test_find_borders_none():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    assert not list(surface.find_borders())


def test_find_borders_single():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    single_index = surface.add_vertex(Vertex(0, 21, 42))
    borders = list(surface.find_borders())
    assert len(borders) == 1
    assert borders[0] == PolygonalCircuit((single_index,))


def test_find_borders_singles():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    single_indices = [surface.add_vertex(Vertex(i, 21, 42)) for i in range(3)]
    borders = set(surface.find_borders())
    assert len(borders) == 3
    assert PolygonalCircuit((single_indices[0],)) in borders
    assert PolygonalCircuit((single_indices[1],)) in borders
    assert PolygonalCircuit((single_indices[2],)) in borders


def test_find_borders_single_triangle_simple():
    surface = Surface()
    vertex_indices = [surface.add_vertex(Vertex(i, 21, 42)) for i in range(3)]
    surface.triangles.append(Triangle(vertex_indices))
    borders = set(surface.find_borders())
    assert len(borders) == 1
    assert PolygonalCircuit(vertex_indices) in borders


def test_find_borders_single_triangle_real():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    vertex_indices = [surface.add_vertex(Vertex(i, 21, 42)) for i in range(3)]
    surface.triangles.append(Triangle(vertex_indices))
    borders = set(surface.find_borders())
    assert len(borders) == 1
    assert PolygonalCircuit(vertex_indices) in borders


def test_find_borders_remove_triangle():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    triangle = surface.triangles.pop()
    borders = set(surface.find_borders())
    assert len(borders) == 1
    assert triangle in borders


def test_find_borders_remove_non_adjacent_triangles():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    triangles = [surface.triangles.pop(), surface.triangles.pop()]
    borders = set(surface.find_borders())
    assert len(borders) == 2
    assert triangles[0] in borders
    assert triangles[1] in borders


def test_find_borders_remove_adjacent_triangles():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    triangles = [surface.triangles.pop(), surface.triangles.pop()]
    triangles.append(surface.triangles.pop(270682))
    assert triangles[1] == Triangle((136141, 136142, 137076))
    assert triangles[2] == Triangle((136141, 136142, 135263))
    borders = set(surface.find_borders())
    assert len(borders) == 2
    assert triangles[0] in borders
    assert PolygonalCircuit((137076, 136141, 135263, 136142)) in borders
    surface.triangles.pop(270682)
    borders = set(surface.find_borders())
    assert len(borders) == 2
    assert triangles[0] in borders
    assert PolygonalCircuit((137076, 136141, 135263, 135264, 136142)) in borders
    surface.triangles.pop(274320)
    borders = set(surface.find_borders())
    assert len(borders) == 2
    assert PolygonalCircuit((136143, 138007, 138008, 137078)) in borders
    assert PolygonalCircuit((137076, 136141, 135263, 135264, 136142)) in borders


@pytest.mark.parametrize(
    ("label_name", "expected_border_lens"),
    [
        ("precentral", [416]),
        ("postcentral", [395]),
        ("medialorbitofrontal", [6, 246]),
        # ...--2343      2347
        #          \    /    \
        #           2345      2348
        #          /    \    /
        # ...--2344      2346
        ("posteriorcingulate", [4, 190]),
        ("unknown", [3, 390]),
    ],
)
def test_find_borders_real(label_name, expected_border_lens):
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    surface.load_annotation_file(ANNOTATION_FILE_PATH)
    (label,) = filter(
        lambda l: l.name == label_name, surface.annotation.labels.values()
    )
    surface.triangles = list(
        filter(
            lambda t: all(
                surface.annotation.vertex_label_index[vertex_idx] == label.index
                for vertex_idx in t.vertex_indices
            ),
            surface.triangles,
        )
    )
    surface.remove_unused_vertices()
    borders = list(surface.find_borders())
    border_lens = [len(b.vertex_indices) for b in borders]
    # self-crossing borders may or may not be split into
    # separate polygonal circuits
    assert sorted(border_lens) == expected_border_lens or sum(border_lens) == sum(
        expected_border_lens
    )


def test__get_vertex_label_index():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    surface.load_annotation_file(ANNOTATION_FILE_PATH)
    # pylint: disable=protected-access
    assert surface._get_vertex_label_index(64290) == 22
    assert surface._get_vertex_label_index(72160) == 22
    assert surface._get_vertex_label_index(84028) == 24
    assert surface._get_vertex_label_index(97356) == 24
    assert surface._get_vertex_label_index(123173) == 27
    assert surface._get_vertex_label_index(140727) == 27
    assert surface._get_vertex_label_index(93859) == 28
    assert surface._get_vertex_label_index(78572) == 0
    assert surface._get_vertex_label_index(120377) == 0
    vertex_index = surface.add_vertex(Vertex(0.0, 21.0, 42.0))
    assert surface._get_vertex_label_index(vertex_index) is None
    del surface.annotation.vertex_label_index[140727]
    assert surface._get_vertex_label_index(140727) is None


def test__find_label_border_segments():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    surface.load_annotation_file(ANNOTATION_FILE_PATH)
    (precentral_label,) = filter(
        lambda l: l.name == "precentral", surface.annotation.labels.values()
    )
    # pylint: disable=protected-access
    border_segments = set(surface._find_label_border_segments(precentral_label))
    assert len(border_segments) == 417
    assert LineSegment((33450, 32065)) in border_segments
    assert LineSegment((33454, 33450)) in border_segments
    for border_vertex_index in [33450, 33454, 32065]:
        assert (
            surface.annotation.vertex_label_index[border_vertex_index]
            == precentral_label.index
        )
        for other_vertex_index in [32064, 33449, 33455, 33449, 33455]:
            assert (
                LineSegment((other_vertex_index, border_vertex_index))
                not in border_segments
            )
            assert (
                LineSegment((border_vertex_index, other_vertex_index))
                not in border_segments
            )


def test__find_label_border_segments_incomplete_annotation():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    surface.load_annotation_file(ANNOTATION_FILE_PATH)
    (precentral_label,) = filter(
        lambda l: l.name == "precentral", surface.annotation.labels.values()
    )
    # pylint: disable=protected-access
    assert surface._find_label_border_segments(precentral_label)
    surface.triangles.append(
        Triangle(
            [
                surface.add_vertex(Vertex(0.0, 21.0 * factor, 42.0 * factor))
                for factor in range(3)
            ]
        )
    )
    border_segments = set(surface._find_label_border_segments(precentral_label))
    assert len(border_segments) == 417


def test_find_label_border_polygonal_chains_missing_annotation():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    annotation = Annotation.read(ANNOTATION_FILE_PATH)
    (precentral_label,) = filter(
        lambda l: l.name == "precentral", annotation.labels.values()
    )
    with pytest.raises(RuntimeError, match=r"\bload_annotation_file\b"):
        next(surface.find_label_border_polygonal_chains(precentral_label))


def test_find_label_border_polygonal_chains():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    surface.load_annotation_file(ANNOTATION_FILE_PATH)
    (precentral_label,) = filter(
        lambda l: l.name == "precentral", surface.annotation.labels.values()
    )
    (border_chain,) = surface.find_label_border_polygonal_chains(precentral_label)
    vertex_indices_normalized = list(border_chain.normalized().vertex_indices)
    assert len(vertex_indices_normalized) == 418
    assert vertex_indices_normalized[66:73] == [
        61044,
        62119,
        62118,
        62107,
        62118,
        63255,
        63264,
    ]
    assert vertex_indices_normalized[:4] == [32065, 32072, 32073, 32080]
    assert vertex_indices_normalized[-4:] == [36281, 34870, 33454, 33450]


def test_find_label_border_polygonal_chains_long_leaf():
    surface = Surface()
    with unittest.mock.patch.object(
        surface,
        "_find_label_border_segments",
        return_value=[
            LineSegment((0, 1)),
            LineSegment((1, 2)),
            LineSegment((0, 3)),
            LineSegment((2, 3)),
            LineSegment((2, 4)),
            LineSegment((4, 5)),  # leaf
        ],
    ):
        (border_chain,) = surface.find_label_border_polygonal_chains("dummy")
    assert list(border_chain.normalized().vertex_indices) == [0, 1, 2, 4, 5, 4, 2, 3]


def test__unused_vertices():
    surface = Surface()
    assert not surface._unused_vertices()
    for i in range(4):
        surface.add_vertex(Vertex(i, i, i))
    assert surface._unused_vertices() == {0, 1, 2, 3}
    surface.triangles.append(Triangle((0, 2, 3)))
    assert surface._unused_vertices() == {1}
    surface.triangles.append(Triangle((0, 3, 1)))
    assert not surface._unused_vertices()
    del surface.triangles[0]
    assert surface._unused_vertices() == {2}


def test__unused_vertices_real():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    assert not surface._unused_vertices()
    surface.triangles = list(
        filter(lambda t: 42 not in t.vertex_indices, surface.triangles)
    )
    assert surface._unused_vertices() == {42}


def test_remove_unused_vertices_all():
    surface = Surface()
    for i in range(5):
        surface.add_vertex(Vertex(i, i, i))
    assert len(surface.vertices) == 5
    surface.remove_unused_vertices()
    assert not surface.vertices
    surface.remove_unused_vertices()
    assert not surface.vertices


def test_remove_unused_vertices_almost_all():
    surface = Surface()
    for i in range(5):
        surface.add_vertex(Vertex(i, i, i))
    assert len(surface.vertices) == 5
    surface.triangles.append(Triangle((0, 2, 3)))
    surface.remove_unused_vertices()
    assert len(surface.vertices) == 3
    assert surface.vertices[0] == pytest.approx(Vertex(0, 0, 0))
    assert surface.vertices[1] == pytest.approx(Vertex(2, 2, 2))
    assert surface.vertices[2] == pytest.approx(Vertex(3, 3, 3))
    assert len(surface.triangles) == 1
    assert surface.triangles[0] == Triangle((0, 1, 2))
    del surface.triangles[0]
    surface.remove_unused_vertices()
    assert not surface.vertices


def test_remove_unused_vertices_some():
    surface = Surface()
    for i in range(9):
        surface.add_vertex(Vertex(i, i, i))
    surface.triangles.append(Triangle((0, 2, 3)))
    surface.triangles.append(Triangle((3, 4, 5)))
    surface.triangles.append(Triangle((3, 2, 5)))
    surface.triangles.append(Triangle((3, 2, 8)))
    surface.remove_unused_vertices()
    assert len(surface.vertices) == 6
    assert surface.vertices[0] == pytest.approx(Vertex(0, 0, 0))
    assert surface.vertices[1] == pytest.approx(Vertex(2, 2, 2))
    assert surface.vertices[2] == pytest.approx(Vertex(3, 3, 3))
    assert surface.vertices[3] == pytest.approx(Vertex(4, 4, 4))
    assert surface.vertices[4] == pytest.approx(Vertex(5, 5, 5))
    assert surface.vertices[5] == pytest.approx(Vertex(8, 8, 8))
    assert len(surface.triangles) == 4
    assert surface.triangles[0] == Triangle((0, 1, 2))
    assert surface.triangles[1] == Triangle((2, 3, 4))
    assert surface.triangles[2] == Triangle((2, 1, 4))
    assert surface.triangles[3] == Triangle((2, 1, 5))
    surface.remove_unused_vertices()
    assert len(surface.triangles) == 4


def test_remove_unused_vertices_none():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    assert len(surface.vertices) == 155622
    assert len(surface.triangles) == 311240
    surface.remove_unused_vertices()
    assert len(surface.vertices) == 155622
    assert len(surface.triangles) == 311240


def test_remove_unused_vertices_single():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    assert len(surface.vertices) == 155622
    assert len(surface.triangles) == 311240
    assert surface.triangles[-1] == Triangle((136143, 138007, 137078))
    surface.triangles = list(
        filter(lambda t: 42 not in t.vertex_indices, surface.triangles)
    )
    assert surface._unused_vertices() == {42}
    surface.remove_unused_vertices()
    assert len(surface.vertices) == 155622 - 1
    assert len(surface.triangles) == 311240 - 7
    assert surface.triangles[-1] == Triangle((136142, 138006, 137077))
    assert all(
        vertex_index < len(surface.vertices)
        for triangle in surface.triangles
        for vertex_index in triangle.vertex_indices
    )


def test_select_vertices():
    surface = Surface()
    for i in range(4):
        surface.add_vertex(Vertex(i, i, i))
    assert numpy.allclose(
        surface.select_vertices([2, 1]), [surface.vertices[2], surface.vertices[1]]
    )
    assert numpy.allclose(
        surface.select_vertices([3, 2]), [surface.vertices[3], surface.vertices[2]]
    )
    assert numpy.allclose(surface.select_vertices((3, 2)), [[3, 3, 3], [2, 2, 2]])
    assert numpy.allclose(
        surface.select_vertices(filter(lambda i: i % 2 == 1, range(4))),
        [[1, 1, 1], [3, 3, 3]],
    )


def test_unite_2():
    surface_a = Surface()
    for i in range(0, 4):
        surface_a.add_vertex(Vertex(i, i, i))
    surface_a.triangles.append(Triangle((0, 1, 2)))
    surface_a.triangles.append(Triangle((1, 2, 3)))
    surface_b = Surface()
    for i in range(10, 14):
        surface_b.add_vertex(Vertex(i, i, i))
    surface_b.triangles.append(Triangle((0, 1, 3)))
    surface_a_copy = copy.deepcopy(surface_a)
    surface_b_copy = copy.deepcopy(surface_b)
    union = Surface.unite([surface_a, surface_b])
    assert numpy.allclose(surface_a.vertices, surface_a_copy.vertices)
    assert numpy.allclose(surface_b.vertices, surface_b_copy.vertices)
    assert numpy.allclose(union.vertices[:4], surface_a.vertices)
    assert numpy.allclose(union.vertices[4:], surface_b.vertices)
    assert surface_a.triangles == surface_a_copy.triangles
    assert surface_b.triangles == surface_b_copy.triangles
    assert union.triangles[:2] == surface_a.triangles
    assert union.triangles[2:] == [Triangle((4, 5, 7))]


def test_unite_3():
    surface_a = Surface()
    for i in range(0, 4):
        surface_a.add_vertex(Vertex(i, i, i))
    surface_a.triangles.append(Triangle((0, 1, 2)))
    surface_a.triangles.append(Triangle((1, 2, 3)))
    surface_b = Surface()
    for i in range(10, 14):
        surface_b.add_vertex(Vertex(i, i, i))
    surface_b.triangles.append(Triangle((0, 1, 3)))
    surface_c = Surface()
    for i in range(20, 23):
        surface_c.add_vertex(Vertex(i, i, i))
    surface_c.triangles.append(Triangle((0, 1, 2)))
    surface_c.triangles.append(Triangle((0, 1, 2)))
    union = Surface.unite(filter(None, [surface_a, surface_b, surface_c]))
    assert numpy.allclose(union.vertices[:4], surface_a.vertices)
    assert numpy.allclose(union.vertices[4:8], surface_b.vertices)
    assert numpy.allclose(union.vertices[8:], surface_c.vertices)
    assert union.triangles[:2] == surface_a.triangles
    assert union.triangles[2:3] == [Triangle((4, 5, 7))]
    assert union.triangles[3:] == [Triangle((8, 9, 10)), Triangle((8, 9, 10))]


def test_unite_real():
    surface_a = Surface.read_triangular(SURFACE_FILE_PATH)
    surface_b = Surface()
    for i in range(5):
        surface_b.add_vertex(Vertex(i, i, i))
    surface_b.triangles.append(Triangle((0, 1, 3)))
    surface_b.triangles.append(Triangle((1, 3, 4)))
    union = Surface.unite((surface_a, surface_b))
    assert numpy.allclose(union.vertices[:-5], surface_a.vertices)
    assert numpy.allclose(union.vertices[-5:], surface_b.vertices)
    assert union.triangles[:-2] == surface_a.triangles
    assert union.triangles[-2:] == [
        Triangle((155622, 155623, 155625)),
        Triangle((155623, 155625, 155626)),
    ]
    assert union.creator == surface_a.creator
    assert union.creation_datetime == surface_a.creation_datetime
    assert union.using_old_real_ras == surface_a.using_old_real_ras
    assert union.volume_geometry_info == surface_a.volume_geometry_info
    assert union.command_lines == surface_a.command_lines
    assert union.annotation == surface_a.annotation
