from setuptools import setup
import os

name = 'Pybot'

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, name, '__init__.py'), 'r', encoding='utf-8') as f:
      exec(f.read(), about)

with open("README.md", 'r', encoding='utf-8') as f:
      readme = f.read()

setup(name=name,
      version=about['__version__'],
      description='Pybot is an automation framework with GUI features thanks to Sikuli',
      long_description=readme,
      url='https://papit.fr',
      author='PapIT',
      author_email='christophe.brun@papit.fr',
      license="No license",
      packages=[name],
      include_package_data=True,
      python_requires=">=3.6",
      zip_safe=False,
      install_requires=['pytest', 'pytest-html', 'doxypypy', 'lackey'],
      )