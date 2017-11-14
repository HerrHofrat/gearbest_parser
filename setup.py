from distutils.core import setup
setup(
    name='gearbest_parser',
    packages=['gearbest_parser'],
    install_requires=['beautifulsoup4==4.6.0'],
    python_requires='>=3.3',
    version='1.0.5',
    description='Load an gearbest shop item',
    author='Roman Reibnagel',
    author_email='roman.reibnagel@gmail.com',
    url='https://github.com/herrhofrat/gearbest_parser',
    keywords=['gearbest', 'parser']
)
