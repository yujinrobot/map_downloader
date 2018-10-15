from setuptools import setup

setup(name='map_downloader',
      version='0.13',
      description='Download map files required by gopher_series robot.',
      author='Thomas Kostas',
      url='https://github.com/yotabits/map_downloader',
      author_email='tkostas75@gmail.com',
      license='MIT',
      packages=['map_downloader'],
      scripts=['bin/map_downloader'],
      install_requires=['requests==2.19.1'],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        ],
      zip_safe=False)
