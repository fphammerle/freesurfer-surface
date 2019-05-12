import os

SUBJECTS_DIR = os.path.join(os.path.dirname(__file__), 'subjects')

ANNOTATION_FILE_PATH = os.path.join(SUBJECTS_DIR, 'fabian',
                                    'label', 'lh.aparc.annot')
SURFACE_FILE_PATH = os.path.join(SUBJECTS_DIR, 'fabian', 'surf', 'lh.pial')
