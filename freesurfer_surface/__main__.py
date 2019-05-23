import argparse
import csv
import sys

from freesurfer_surface import Annotation, Surface


def annotation_labels():
    """
    List Labels Stored in Freesurfer's Annotation File
    (i.e., label/lh.aparc.annot)
    """
    argparser = argparse.ArgumentParser(
        description=annotation_labels.__doc__.strip())
    argparser.add_argument('--delimiter', default='\t',
                           help='default: %(default)r')
    argparser.add_argument('annotation_file_path')
    args = argparser.parse_args()
    annotation = Annotation.read(args.annotation_file_path)
    csv_writer = csv.writer(sys.stdout, delimiter=args.delimiter)
    csv_writer.writerow(('index', 'color', 'name'))
    labels = sorted(annotation.labels.values(), key=lambda l: l.index)
    csv_writer.writerows((l.index, l.hex_color_code, l.name,) for l in labels)


def unite_surfaces():
    """
    Unite Multiple Surfaces in Freesurfer's TriangularSurface Format
    Into a Single TriangularSurface File (i.e., lh.pial, lh.white)
    """
    argparser = argparse.ArgumentParser(
        description=unite_surfaces.__doc__.strip())
    argparser.add_argument('--output',
                           metavar='OUTPUT_PATH',
                           dest='output_path',
                           required=True)
    argparser.add_argument('input_paths',
                           metavar='INPUT_PATH',
                           nargs='+')
    args = argparser.parse_args()
    union = Surface.unite(Surface.read_triangular(p)
                          for p in args.input_paths)
    union.write_triangular(args.output_path)
