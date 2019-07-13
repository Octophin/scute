from setuptools import setup

setup(name='scute',
      version='0.1',
      description='Tool for making hardware user interfaces',
      url='https://github.com/Octophin/scute',
      author='Octophin Digital',
      author_email='hello@octophin.com',
      license='MIT',
      packages=['scute'],
      install_requires=[
          'Flask',
      ],
      zip_safe=False)