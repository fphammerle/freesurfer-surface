# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2021-05-22
### Removed
- compatibility with `python3.5`

## Changed
- added default value for `creator` to fix `TypeError` in `write_triangular` when unset
- `write_triangular`: raise descriptive `ValueError` when missing `volume_geometry_info`
  (instead of `TypeError`)
- `find_label_border_polygonal_chains`: raise descriptive `RuntimeError`
  when annotation was not loaded (instead of `TypeError`)

### Fixed
- fixed type hints

## [1.2.0] - 2021-01-02
### Added
- GPLv3+ license
- method `PolygonalCircuit.normalized()`

### Fixed
- `Surface.find_label_border_polygonal_chains`:
  always include vertices along border with single neighbour
  (previously indeterministic behaviour)
- `PolygonalCircuit`: fix equals operator for circuits
  with different but equivalent vertex orders
- type hints

## [1.1.1] - 2020-10-18
### Fixed
- fix `ModuleNotFoundError` on `import freesurfer_surface.version`
  for developers not installing package
  (https://github.com/fphammerle/freesurfer-surface/issues/22)
- `setlocale`: re-raise original exception
  when the selected locale is not supported

## [1.1.0] - 2019-05-23
### Added
* added static method `Surface.unite(surfaces)`
* added command-line entry point / script `unite-freesurfer-surfaces`

## [1.0.1] - 2019-05-23
### Fixed
- `Surface.find_borders()` failed on self-crossing borders

## [1.0.0] - 2019-05-19
## Added
- method `Surface.find_borders()`
- method `Surface.remove_unused_vertices()`
- method `Surface.select_vertices(vertex_indices)`
- method `Vertex.distance_mm(other_vertices)`
- class `LineSegment`
- class `PolygonalCircuit`

## Changed
* property `Triangle.vertex_indices` is now read-only

## [0.2.2] - 2019-05-19
### Fixed
- fixed comparison & hashing of `Triangle` / `_PolygonalCircuit`
  (`_PolygonalCircuit._normalize` now considers order of indices)

## [0.2.1] - 2019-05-16
### Fixed
- fix formatting of project description on pypi

## [0.2.0] - 2019-05-15
### Added
- added `PolygonalChain.adjacent_vertex_indices()`
- `Surface.add_rectangle`: accept 3 or 4 vertex indices (previously only 3)

### Changed
- dervice `Vertex` from `numpy.ndarray` (previously `collections.namedtuple`)

### Fixed
* `Surface._find_label_border_segments`: failing on incompletely labelled set of vertices

## [0.1.0] - 2019-05-12
tagger Fabian Peter Hammerle <fabian@hammerle.me> 1557674236 +0200

[Unreleased]: https://github.com/fphammerle/freesurfer-stats/compare/2.0.0...HEAD
[2.0.0]: https://github.com/fphammerle/freesurfer-stats/compare/1.2.0...2.0.0
[1.2.0]: https://github.com/fphammerle/freesurfer-stats/compare/1.1.1...1.2.0
[1.1.1]: https://github.com/fphammerle/freesurfer-stats/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/fphammerle/freesurfer-stats/compare/1.0.1...1.1.0
[1.0.1]: https://github.com/fphammerle/freesurfer-stats/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/fphammerle/freesurfer-stats/compare/0.2.2...1.0.0
[0.2.2]: https://github.com/fphammerle/freesurfer-stats/compare/0.2.1...0.2.2
[0.2.1]: https://github.com/fphammerle/freesurfer-stats/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/fphammerle/freesurfer-stats/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/fphammerle/freesurfer-stats/releases/tag/0.1.0
