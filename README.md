# SwiftSeq-Parsl

How to run :

Assuming you are on dev.parallel.works, the user swift has the right set of privileges to access data and executables required for the run.

# Assume user swift
sudo su swift

# Load parsl from github clone
. setup.sh

# Check parsl version, this should return 0.2.2 or above.
python3 -c "import parsl; print(parsl.__version__)"

# Run swift seq
python3 swift_seq.py

# Run swift seq in mock mode
python3 swift_seq.py -m


