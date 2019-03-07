from setuptools import setup, find_packages

from swag.core import SwagStrings

setup(
    name=SwagStrings.setup_name,
    version=SwagStrings.setup_version,
    description=SwagStrings.setup_description,
    license=SwagStrings.setup_license,
    author=SwagStrings.setup_author,
    author_email=SwagStrings.setup_author_email,
    url=SwagStrings.setup_url,

    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'six',
        'cerberus',
        'parsl'
    ],
    package_data={
        'swag': ['util_scripts/*']
    },
    entry_points={
        'console_scripts': ['swag = swag:execute_from_command_line']
    },
    classifiers=[]
)
