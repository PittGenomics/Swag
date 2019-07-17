Swag
========
Scalable Workflows for Analyzing Genomes

Quickstart
==========

Create and activate a dedicated Conda environment::

    $ conda create --name swag python=3.7
    $ source activate swag

Install Swag::

    $ git clone https://github.com/PittGenomics/Swag
    $ cd Swag
    $ python3 setup.py install

Run the demo::

    $ cd examples/align
    $ wget http://www.crc.nd.edu/~awoodard/references.tar.gz
    $ tar -xf references.tar.gz
    $ swag install-env
    $ swag run config.py
