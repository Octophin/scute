from setuptools import setup

setup(name='scute',
      version='0.6.2',
      entry_points = """
        [babel.extractors]
        scute_schema = scute.translator:extract_schema_translation
        """,
      description='Tool for making hardware user interfaces',
      url='https://github.com/Octophin/scute',
      author='Octophin Digital',
      author_email='hello@octophin.com',
      license='MIT',
      packages=['scute'],
      install_requires=[
          'Flask', 'mistune', 'flask-babel', 'pybabel-json-md'
      ],
      include_package_data=True,
      zip_safe=False)
