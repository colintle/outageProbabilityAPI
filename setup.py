from setuptools import setup

setup(
    name='Outage Map API',
    version='0.1.0',
    py_modules=['outage_map'],
    install_requires=[
        'Click==8.1.7',
        'affine==2.4.0',
        'aiohttp==3.9.5',
        'aiohttp-client-cache==0.11.0',
        'aiosignal==1.3.1',
        'aiosqlite==0.20.0',
        'async-retriever==0.16.1',
        'async-timeout==4.0.3',
        'attrs==23.2.0',
        'branca==0.7.2',
        'brotli==1.1.0',
        'beautifulsoup4==4.12.3',
        'cattrs==23.2.3',
        'certifi==2024.6.2',
        'cffi==1.16.0',
        'cftime==1.6.4',
        'charset-normalizer==3.3.2',
        'click-plugins==1.1.1',
        'cligj==0.7.2',
        'colorama==0.4.6',
        'contourpy==1.2.1',
        'cycler==0.12.1',
        'cytoolz==0.12.3',
        'defusedxml==0.7.1',
        'dss-python==0.15.7',
        'dss-python-backend==0.14.5',
        'et-xmlfile==1.1.0',
        'exceptiongroup==1.2.1',
        'fiona==1.9.6',
        'folium==0.17.0',
        'fonttools==4.53.0',
        'frozenlist==1.4.1',
        'geopandas==0.14.4',
        'geopy==2.4.1',
        'h5netcdf==1.3.0',
        'h5py==3.11.0',
        'hydrosignatures==0.16.0',
        'idna==3.7',
        'importlib-metadata==7.2.0',
        'importlib-resources==6.4.0',
        'itsdangerous==2.2.0',
        'jinja2==3.1.4',
        'joblib==1.4.2',
        'kiwisolver==1.4.5',
        'lxml==5.2.2',
        'markupsafe==2.1.5',
        'matplotlib==3.9.0',
        'meteostat==1.6.8',
        'multidict==6.0.5',
        'netcdf4==1.7.1',
        'networkx==3.2.1',
        'numpy==1.26.4',
        'opendssdirect-py==0.9.4',
        'openpyxl==3.1.4',
        'owslib==0.31.0',
        'packaging==24.1',
        'pandas==2.2.2',
        'pillow==10.3.0',
        'platformdirs==4.2.2',
        'py3dep==0.16.3',
        'pyarrow==16.1.0',
        'pycparser==2.22',
        'pygeohydro==0.16.5',
        'pygeoogc==0.16.3',
        'pygeoutils==0.16.3',
        'pynhd==0.16.3',
        'pynldas2==0.16.0',
        'pyparsing==3.1.2',
        'pyproj==3.6.1',
        'python-dateutil==2.9.0.post0',
        'pytz==2024.1',
        'pyyaml==6.0.1',
        'rasterio==1.3.10',
        'requests==2.32.3',
        'requests-cache==1.2.1',
        'rioxarray==0.15.0',
        'scipy==1.13.1',
        'shapely==2.0.4',
        'six==1.16.0',
        'snuggs==1.4.7',
        'toolz==0.12.1',
        'typing-extensions==4.12.2',
        'tzdata==2024.1',
        'ujson==5.10.0',
        'url-normalize==1.4.3',
        'urllib3==2.2.2',
        'xarray==2024.6.0',
        'xyzservices==2024.6.0',
        'yarl==1.9.4',
        'zipp==3.19.2',
    ],
    entry_points={
        'console_scripts': [
            'outage-map = outage_map.main:cli',
        ],
    },
)
