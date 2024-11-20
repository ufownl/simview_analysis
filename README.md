# SimView Analysis

**SimView Analysis** uses the telemetry data from the lap comparison analysis page of [SimView](https://www.overtake.gg/downloads/simview.35249/) to draw a time-difference chart. It is open-source and free to use under [GPLv3](https://www.gnu.org/licenses/gpl-3.0.txt).

## Dependencies

* [Python3](https://www.python.org/)
  * [requests](https://github.com/psf/requests)
  * [numpy](https://github.com/numpy/numpy)
  * [matplotlib](https://github.com/matplotlib/matplotlib)
  * [scipy](https://github.com/scipy/scipy)

Install dependencies:

```bash
$ pip3 install -r requirements.txt
```

## Usage

```bash
$ python3 simview_analysis.py --help
usage: simview_analysis.py [-h] --url URL [--epsilon EPSILON]

Time-diff chart for SimView.

options:
  -h, --help         show this help message and exit
  --url URL          URL of lap comparison analysis page
  --epsilon EPSILON  data alignment accuracy (default: 0.1)
```
