from setuptools import setup

setup(
    entry_points={
        'console_scripts': [
            'sac = sac:main'
        ]
    },
    name='sac',
    packages=[
        'sac',
        'sac.cli',
        'sac.util'
    ],
    version='0.1',
    description='Semantic Audio Companion',
    author='Nikolaos Tsipas',
    author_email='nicktgr15@yahoo.com',
    url='https://github.com/nicktgr15/sac',
    download_url='https://github.com/nicktgr15/sac/archive/0.1.tar.gz',
    keywords=[],
    classifiers=[]
)
