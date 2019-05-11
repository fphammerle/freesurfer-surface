## Usage

### List Labels in Annotation File

```python
from freesurfer_surface import Annotation

annotation = Annotation.read('tests/subjects/fabian/label/lh.aparc.annot')
for label in annotation.labels.values():
    print(label.index, label.hex_color_code, label.name)
```

or

```sh
$ freesurfer-annotation-labels tests/subjects/fabian/label/lh.aparc.annot
index	color	name
0	#190519	unknown
1	#196428	bankssts
2	#7d64a0	caudalanteriorcingulate
3	#641900	caudalmiddlefrontal
...
33	#4614aa	temporalpole
34	#9696c8	transversetemporal
35	#ffc020	insula
```
