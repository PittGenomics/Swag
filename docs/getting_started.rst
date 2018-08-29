Getting Started
===============

To install with pip:

.. code-block:: text

    $ pip install swag

Once Swag is installed, software dependencies can be installed with `Bioconda <https://bioconda.github.io/>`_::

    $ swag install-env

This will produce an ``executables.config`` file that the user can pass directly into a Swag run.

.. note::

    The above command will only work if the user has Anaconda/Miniconda installed. It's provided as a convenience; if
    the user would rather install software dependencies manually, Swiftseq only needs an ``executables.config`` at
    runtime and is indifferent to where it comes from.

The user can then run Swag::

    swag run --exe-config /path/to/executables.config [options]
