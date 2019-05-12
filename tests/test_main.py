import csv
import io
import subprocess
import typing
import unittest.mock

from freesurfer_surface.__main__ import annotation_labels

from conftest import ANNOTATION_FILE_PATH


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
