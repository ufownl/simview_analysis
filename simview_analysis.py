#   SimView Analysis - Time-diff chart for SimView
#   Copyright (C) 2024  RangerUFO

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.


import re
import struct
import argparse
import requests
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate


def get_telemetries(url):
    m = re.match("^\\s*(https?://\\S+)/analysis/compare/lap1/([0-9]+)/lap2/([0-9]+)", args.url)
    if m is None:
        raise RuntimeError("Invalid URL of lap comparison analysis page")
    return [requests.get(m[1] + "/api/ac/lap/telemetry/" + lapid).content for lapid in [m[2], m[3]]]


def parse_telemetry_v1(raw):
    version, track_length = struct.unpack_from("<II", buffer=raw)
    if version != 1:
        raise RuntimeError("SimView telemetry version mismatch")
    def parse_data(raw):
        prev_pos = 0
        for i in range(8, len(raw), 17):
            nsp, _, speed, _, _ = struct.unpack_from("<fBfff", buffer=raw, offset=i)
            pos = nsp * track_length
            if pos > prev_pos:
                yield pos, speed
                prev_pos = pos
    return [(pos, speed)  for pos, speed in parse_data(raw)]


def process_data(data, epsilon):
    for line in data:
        x, y = zip(*line)
        f = interpolate.interp1d(np.array(x), np.array(y), kind="slinear")
        x1 = np.linspace(x[0], x[-1], int((x[-1] - x[0]) / epsilon))
        yield x1, f(x1)


def align_data(t, epsilon):
    if abs(t[0][0][0] - t[1][0][0]) < epsilon:
        return t
    i = 1
    if t[0][0][0] < t[1][0][0]:
        while t[0][0][i] < t[1][0][0]:
            i += 1
        return [(t[0][0][i:], t[0][1][i:]), t[1]]
    else:
        while t[1][0][i] < t[0][0][0]:
            i += 1
        return [t[0], (t[1][0][i:], t[1][1][i:])]


def lap_time(x, y):
    t = 0
    z = [t]
    for i in range(1, len(x)):
        v = (y[i - 1] + y[i]) * 0.5 * 1000 / 3600
        d = x[i] - x[i - 1]
        t += d / v
        z.append(t)
    return np.array(z)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Time-diff chart for SimView.")
    parser.add_argument("--url", help="URL of lap comparison analysis page", type=str, required=True)
    parser.add_argument("--epsilon", help="data alignment accuracy (default: 0.1)", type=float, default=0.1)
    args = parser.parse_args()

    get_telemetries(args.url)
    data = tuple((x, y) for x, y in process_data([parse_telemetry_v1(raw) for raw in get_telemetries(args.url)], args.epsilon))
    t = [(x, lap_time(x, y)) for x, y in align_data(data, args.epsilon)]
    n = min(len(x) for x, _ in t)
    fig = plt.figure()
    ax0 = fig.add_subplot(111)
    ax0.set_xlabel("Track Position (m)")
    ax0.set_ylabel("Velocity (km/h)")
    for i, (x, y) in enumerate(data):
        ax0.plot(x[:n], y[:n], ":", label="lap-%d"%(i+1))
    ax0.legend()
    ax1 = ax0.twinx()
    ax1.set_ylabel("Time Diff (s)")
    ax1.plot(t[0][0][:n], t[0][1][:n] - t[1][1][:n], "g", label="time diff")
    ax1.grid(True)
    plt.show()
