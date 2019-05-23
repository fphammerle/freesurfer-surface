import csv
import io
import subprocess
import typing
import unittest.mock

import numpy

from freesurfer_surface import Surface, Triangle, Vertex
from freesurfer_surface.__main__ import annotation_labels, unite_surfaces

from conftest import ANNOTATION_FILE_PATH, SURFACE_FILE_PATH


def check_rows(csv_rows: typing.List[str]):
    assert len(csv_rows) == 36 + 1
    assert csv_rows[0] == ['index', 'color', 'name']
    assert csv_rows[1] == ['0', '#190519', 'unknown']
    assert csv_rows[23] == ['22', '#dc1414', 'postcentral']
    assert csv_rows[25] == ['24', '#3c14dc', 'precentral']


def test_annotation_labels_function(capsys):
    with unittest.mock.patch('sys.argv', ['', ANNOTATION_FILE_PATH]):
        annotation_labels()
    out, err = capsys.readouterr()
    assert not err
    check_rows(list(csv.reader(io.StringIO(out), delimiter='\t')))


def test_annotation_labels_function_delimiter(capsys):
    with unittest.mock.patch('sys.argv', ['', '--delimiter', ',', ANNOTATION_FILE_PATH]):
        annotation_labels()
    out, err = capsys.readouterr()
    assert not err
    check_rows(list(csv.reader(io.StringIO(out), delimiter=',')))


def test_annotation_labels_script():
    proc_info = subprocess.run(['freesurfer-annotation-labels', ANNOTATION_FILE_PATH],
                               check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert not proc_info.stderr
    check_rows(list(csv.reader(io.StringIO(proc_info.stdout.decode()),
                               delimiter='\t')))


def test_unite_surfaces_function(tmpdir, capsys):
    surface_b = Surface.read_triangular(SURFACE_FILE_PATH)
    surface_b.vertices = []
    for i in range(5):
        surface_b.add_vertex(Vertex(i, i, i))
    surface_b.triangles = [Triangle((0, 1, 3)), Triangle((1, 3, 4))]
    surface_b_path = tmpdir.join('b').strpath
    surface_b.write_triangular(surface_b_path)
    output_path = tmpdir.join('output_path').strpath
    with unittest.mock.patch('sys.argv', ['', '--output', output_path,
                                          SURFACE_FILE_PATH, surface_b_path]):
        unite_surfaces()
    out, err = capsys.readouterr()
    assert not out
    assert not err
    union = Surface.read_triangular(output_path)
    assert len(union.vertices) == 155627
    assert len(union.triangles) == 311242
    assert numpy.allclose(union.vertices[-5:], surface_b.vertices)


def test_unite_surfaces_script(tmpdir):
    surface_b = Surface.read_triangular(SURFACE_FILE_PATH)
    surface_b.vertices = []
    for i in range(5):
        surface_b.add_vertex(Vertex(i, i, i))
    surface_b.triangles = [Triangle((0, 1, 3)), Triangle((1, 3, 4))]
    surface_b_path = tmpdir.join('b').strpath
    surface_b.write_triangular(surface_b_path)
    output_path = tmpdir.join('output_path').strpath
    proc_info = subprocess.run(['unite-freesurfer-surfaces',
                                '--output', output_path,
                                SURFACE_FILE_PATH, surface_b_path,
                                surface_b_path],
                               check=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    assert not proc_info.stdout
    assert not proc_info.stderr
    union = Surface.read_triangular(output_path)
    assert len(union.vertices) == 155622 + (5 * 2)
    assert len(union.triangles) == 311240 + (2 * 2)
