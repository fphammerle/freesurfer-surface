from freesurfer_surface import Annotation

from conftest import ANNOTATION_FILE_PATH


def test_load_annotation():
    annotation = Annotation.read(ANNOTATION_FILE_PATH)
    assert len(annotation.vertex_label_index) == 155622
    assert annotation.vertex_label_index[64290] == 22
    assert annotation.vertex_label_index[72160] == 22
    assert annotation.vertex_label_index[84028] == 24
    assert annotation.vertex_label_index[97356] == 24
    assert annotation.vertex_label_index[123173] == 27
    assert annotation.vertex_label_index[140727] == 27
    assert annotation.vertex_label_index[93859] == 28
    assert annotation.vertex_label_index[78572] == 0
    assert annotation.vertex_label_index[120377] == 0
    assert annotation.colortable_path == b'/autofs/space/tanha_002/users/greve' \
                                         b'/fsdev.build/average/colortable_desikan_killiany.txt'
    assert len(annotation.labels) == 36
    assert vars(annotation.labels[0]) == {'index': 0, 'name': 'unknown',
                                          'red': 25, 'green': 5, 'blue': 25, 'transparency': 0}
    assert vars(annotation.labels[28]) == {'index': 28, 'name': 'superiorfrontal',
                                           'red': 20, 'green': 220, 'blue': 160, 'transparency': 0}
    precentral, = filter(lambda l: l.name == 'precentral',
                         annotation.labels.values())
    postcentral, = filter(lambda l: l.name == 'postcentral',
                          annotation.labels.values())
    assert vars(precentral) == {'index': 24, 'name': 'precentral',
                                'red': 60, 'green': 20, 'blue': 220, 'transparency': 0}
    assert vars(postcentral) == {'index': 22, 'name': 'postcentral',
                                 'red': 220, 'green': 20, 'blue': 20, 'transparency': 0}
    superiorfrontal, = filter(lambda l: l.color_code == 10542100,
                              annotation.labels.values())
    assert superiorfrontal.name == 'superiorfrontal'
