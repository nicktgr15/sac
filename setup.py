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
        'sac.model'
    ],
    version='0.3.3',
    description='Semantic Audio Companion',
    author='Nikolaos Tsipas',
    author_email='nicktgr15@yahoo.com',
    url='https://github.com/nicktgr15/sac',
    download_url='https://github.com/nicktgr15/sac/releases/tag/0.3.3',
    keywords=['semantic', 'audio', 'sox'],
    classifiers=[],
    install_requires=['matplotlib', 'numpy']
)
