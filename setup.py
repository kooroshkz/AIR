from setuptools import setup, find_packages

setup(
    name='napari-air-plugin',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'napari',
        'numpy',
        'Pillow',
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
        ]
    },
    entry_points={
        'napari.plugin': [
            'napari-image-filters = src.napari_image_filtering_interface',
        ],
    },
    python_requires='>=3.8',
)
