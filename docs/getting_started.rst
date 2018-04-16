Getting Started
===============

To install with pip:

.. code-block:: text

    $ pip install swiftseq

Or to get the latest development version::

    $ pip install git+https://github.com/PittGenomics/SwiftSeq@dev

.. caution::

    The development version may not be stable

Once SwiftSeq is install, software dependencies can be installed with `Bioconda <https://bioconda.github.io/>`_::

    $ swiftseq install-env

This will produce an ``executables.config`` file that the user can pass directly into a SwiftSeq run.

.. note::

    The above command will only work if the user has Anaconda/Miniconda installed. It's provided as a convenience; if
    the user would rather install software dependencies manually, Swiftseq only needs an ``executables.config`` at
    runtime and is indifferent to where it comes from.

The user can then run Swiftseq::

    swiftseq run --exe-config /path/to/executables.config [options]
