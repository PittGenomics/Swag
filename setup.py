from setuptools import setup, find_packages

from swiftseq.core import SwiftSeqStrings

setup(
    name=SwiftSeqStrings.setup_name,
    version=SwiftSeqStrings.setup_version,
    description=SwiftSeqStrings.setup_description,
    license=SwiftSeqStrings.setup_license,
    author=SwiftSeqStrings.setup_author,
    author_email=SwiftSeqStrings.setup_author_email,
    url=SwiftSeqStrings.setup_url,

    packages=find_packages(),
    include_package_data=True,
    package_data={
        'swiftseq': ['util_scripts/*']
    },
    entry_points={
        'console_scripts': ['swiftseq = swiftseq:execute_from_command_line']
    },
    classifiers=[]
)
