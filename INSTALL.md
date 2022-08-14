# Installation Instructions  

## General Dependencies
Silospin requires Python 3.7 or newer. Python can be installed from the Python webpage (https://www.python.org/downloads/) or through Anaconda (https://www.anaconda.com/products/distribution). The package also requries NumPy (https://numpy.org/), SciPy (https://scipy.org/), and Matplotlib (https://matplotlib.org/). Install these as,

```bash
$ pip install numpy
$ pip install scipy
$ pip install matplotlib   
```
### Zurich Instrument Modules  

Silospin interfaces with physical instruments from Zurich Instruments and therefore requires software used by Zurich including zhinst and zhinst-toolkit. These can be installed as,

```bash
$ pip install zhinst
$ pip install zhinst-toolkit   
```

## Silospin Installation

```bash
$ git clone git@github.com:nimalec/Silospin.git  
$ cd silospin/
$ pip install -e .
```

If an old branch is being used (e.g. branch 'new_branch_6_5')
```bash
$ git switch new_branch_6_5  
```
