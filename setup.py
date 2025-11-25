# setup.py
from setuptools import setup, find_packages

setup(
    name="heating_fuel_analysis",
    version="1.0.0",
    packages=find_packages(),  # Will find 'heating_fuel_analysis' package
    
    # Core dependencies (exclude dev tools)
    install_requires=[
        'pandas>=1.3.0,<3.0',
        'numpy>=1.20.0,<2.0',
        'geopandas>=0.10.0,<1.0',
        'fiona>=1.8.0',
        'shapely>=1.8.0,<3.0',
        'pyproj>=3.0.0',
        'rtree>=1.0.0',
        'matplotlib>=3.4.0',
        'contextily>=1.1.0',
    ],
    
    # Optional dependencies for development
    extras_require={
        'dev': [
            'jupyter',
            'jupyterlab',
            'ipykernel',
            'notebook',
            'seaborn',
        ]
    },
    
    description="Analysis of residential heating fuel usage across US census tracts",
    author="Jordan Joseph",
    author_email="jordanjo@alumni.cmu.edu",
    python_requires=">=3.10,<3.13",
)
