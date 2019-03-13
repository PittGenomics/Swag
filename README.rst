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
    $ wget http://www.crc.nd.edu/~awoodard/human_g1k_v37.fasta.gz -O references/human_g1k_v37.fasta.gz
    $ gunzip references/human_g1k_v37.fasta.gz
    $ swag install-env
    $ swag run config.py
