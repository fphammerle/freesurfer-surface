import os

from freesurfer_surface import Annotation

from conftest import SUBJECTS_DIR


def test_load_annotation():
    annotation = Annotation.read(os.path.join(SUBJECTS_DIR, 'fabian', 'label', 'lh.aparc.annot'))
    assert len(annotation.vertex_values) == 155622
    assert annotation.vertex_values[64290] == 1316060
    assert annotation.vertex_values[72160] == 1316060
    assert annotation.vertex_values[84028] == 14423100
    assert annotation.vertex_values[97356] == 14423100
    assert annotation.vertex_values[123173] == 8204875
    assert annotation.vertex_values[140727] == 8204875
    assert annotation.vertex_values[93859] == 10542100
    assert annotation.vertex_values[78572] == 0
    assert annotation.vertex_values[120377] == 0
    assert annotation.colortable_path == b'/autofs/space/tanha_002/users/greve' \
                                         b'/fsdev.build/average/colortable_desikan_killiany.txt'
    assert len(annotation.labels) == 36
    assert vars(annotation.labels[0]) == {'index': 0, 'name': 'unknown',
                                          'red': 25, 'green': 5, 'blue': 25, 'transparency': 0}
    precentral, = filter(lambda l: l.name == 'precentral', annotation.labels)
    postcentral, = filter(lambda l: l.name == 'postcentral', annotation.labels)
    assert vars(precentral) == {'index': 24, 'name': 'precentral',
                                'red': 60, 'green': 20, 'blue': 220, 'transparency': 0}
    assert vars(postcentral) == {'index': 22, 'name': 'postcentral',
                                 'red': 220, 'green': 20, 'blue': 20, 'transparency': 0}
    superiorfrontal, = filter(lambda l: l.color_code == 10542100, annotation.labels)
    assert superiorfrontal.name == 'superiorfrontal'
