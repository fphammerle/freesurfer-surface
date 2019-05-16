freesurfer-surface
==================

.. image:: https://travis-ci.org/fphammerle/freesurfer-surface.svg?branch=master
   :target: https://travis-ci.org/fphammerle/freesurfer-surface
.. image:: https://coveralls.io/repos/github/fphammerle/freesurfer-surface/badge.svg?branch=master
   :target: https://coveralls.io/github/fphammerle/freesurfer-surface?branch=master
.. image:: https://img.shields.io/pypi/v/freesurfer-surface.svg
   :target: https://pypi.org/project/freesurfer-surface/#history
.. image:: https://img.shields.io/pypi/pyversions/freesurfer-surface.svg
   :target: https://pypi.org/project/freesurfer-surface/
.. image:: https://zenodo.org/badge/185943856.svg
   :target: https://zenodo.org/badge/latestdoi/185943856

Python Library to Read and Write Surface Files in Freesurfer’s
TriangularSurface Format

Freesurfer https://surfer.nmr.mgh.harvard.edu/

Install
-------

.. code:: sh

    pip3 install --user freesurfer-surface

Usage
-----

Edit Surface File
~~~~~~~~~~~~~~~~~

.. code:: python

    from freesurfer_surface import Surface, Vertex, Triangle
    surface = Surface.read_triangular('bert/surf/lh.pial'))
    vertex_a = surface.add_vertex(Vertex(0.0, 0.0, 0.0))
    vertex_b = surface.add_vertex(Vertex(1.0, 1.0, 1.0))
    vertex_c = surface.add_vertex(Vertex(2.0, 2.0, 2.0))
    surface.triangles.append(Triangle((vertex_a, vertex_b, vertex_c)))
    surface.write_triangular('somewhere/else/lh.pial')

List Labels in Annotation File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from freesurfer_surface import Annotation

    annotation = Annotation.read('tests/subjects/fabian/label/lh.aparc.annot')
    for label in annotation.labels.values():
        print(label.index, label.hex_color_code, label.name)

or

.. code:: sh

    $ freesurfer-annotation-labels tests/subjects/fabian/label/lh.aparc.annot
    index  color    name
    0      #190519  unknown
    1      #196428  bankssts
    2      #7d64a0  caudalanteriorcingulate
    3      #641900  caudalmiddlefrontal
    ...
    33     #4614aa  temporalpole
    34     #9696c8  transversetemporal
    35     #ffc020  insula

Find Border of Labelled Region
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from freesurfer_surface import Surface
    surface = Surface.read_triangular('bert/surf/lh.pial'))
    surface.load_annotation_file('bert/label/lh.aparc.annot')
    region, = filter(lambda l: l.name == 'precentral',
                     annotation.labels.values())
    print(surface.find_label_border_polygonal_chains(region))

Tests
-----

.. code:: sh

    pip3 install --user pipenv
    git clone https://github.com/fphammerle/freesurfer-surface.git
    cd freesurfer-surface
    pipenv run pylint freesurfer_surface
    pipenv run pytest --cov=freesurfer_surface
