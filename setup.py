import os

import setuptools

import freesurfer_surface


LONG_DESCRIPTION = freesurfer_surface.__doc__.strip()

setuptools.setup(
    name='freesurfer-surface',
    use_scm_version={
        'write_to': os.path.join('freesurfer_surface', 'version.py'),
        # `version` triggers pylint C0103
        'write_to_template': "__version__ = '{version}'\n",
    },
    description=LONG_DESCRIPTION.split(sep='\n', maxsplit=1)[0],
    long_description=LONG_DESCRIPTION,
    author='Fabian Peter Hammerle',
    author_email='fabian@hammerle.me',
    url='https://github.com/fphammerle/freesurfer-surface',
    # TODO add license
    keywords=[
        'brain',
        'freesurfer',
        'mesh',
        'neuroimaging',
        'reader',
        'surface',
        'triangle',
        'vertex',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Utilities',
    ],
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'freesurfer-annotation-labels = freesurfer_surface.__main__:annotation_labels',
        ],
    },
    python_requires='>=3.5',
    install_requires=[
        'numpy<2',
    ],
    setup_requires=[
        'setuptools_scm',
    ],
    tests_require=[
        'pylint>=2.3.0,<3',
        'pytest<5',
        'pytest-cov<3,>=2',
    ],
)
