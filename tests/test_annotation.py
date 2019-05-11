import os

from freesurfer_surface import Annotation

from conftest import SUBJECTS_DIR


def test_load_annotation():
    annotation = Annotation.read(os.path.join(SUBJECTS_DIR, 'fabian', 'label', 'lh.aparc.annot'))
    assert len(annotation.vertex_values) == 155622
    assert annotation.vertex_values[0] == (((100 << 8) + 20) << 8) + 220
    assert annotation.vertex_values[1] == (((100 << 8) + 20) << 8) + 220
    assert annotation.vertex_values[42] == (((140 << 8) + 30) << 8) + 20
    assert annotation.colortable_path == b'/autofs/space/tanha_002/users/greve' \
                                         b'/fsdev.build/average/colortable_desikan_killiany.txt'
    assert len(annotation.labels) == 36
    assert vars(annotation.labels[0]) == {'index': 0, 'name': 'unknown',
                                          'red': 25, 'blue': 5, 'green': 25, 'transparency': 0}
    assert vars(annotation.labels[35]) == {'index': 35, 'name': 'insula',
                                           'red': 255, 'blue': 192, 'green': 32, 'transparency': 0}
