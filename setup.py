from setuptools import setup, find_packages

setup(
    name='napari-air-plugin',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'napari[all]>=0.4.16',
        'numpy>=1.20.0',
        'pillow>=8.0.0',
        'qtpy',
        'mypy',
        'types-Pillow',
        'opencv-python',  
        'scikit-image', 
        'scipy',
        'openai',
        'python-dotenv'
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'pytest-dotenv',
            'pytest-qt',
            'pytest-benchmark',
            'setuptools',
            'wheel'
        ]
    },
    entry_points={
        'napari.plugin': [
            'napari-image-filters = src.napari_image_filtering_interface',
        ],
    },
    python_requires='>=3.8',
)
