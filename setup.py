from setuptools import setup

setup(
   name='Zero-Carbon-Aviation',
   version='0.1',
   description='A collection of tools that may be used to assess the value propostion of various aviation propulsion system options',
   author='David Tew',
   author_email='davetew@alum.mit.edu',
   url='https://github.com/davetew/Zero-Carbon-Aviation',
   packages=setuptools.find_packages("Zero_Carbon_Aviation"),  #same as name
   install_requires=['numpy', 'matplotlib','pandas','pint','cantera'], #external packages as dependencies
)
