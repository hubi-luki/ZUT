import scipy.fftpack
import sounddevice as sd
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
from pylab import rcParams


def quantize(_data, _bits):
    assert 2 <= _bits <= 32

    out_val = _data.astype(np.float32)
    _start = 0
    _end = 0

    if np.issubdtype(_data.dtype, np.floating):
        _start = -1
        _end = 1
    else:
        _start = np.iinfo(_data.dtype).min
        _end   = np.iinfo(_data.dtype).max

    _range2 = 2**_bits-1

    out_val = (out_val-_start)/(_end-_start)
    out_val = np.round(out_val*_range2)/_range2
    out_val = ((out_val*(_end-_start))+_start)

    return out_val.astype(_data.dtype)


def quantize2(_data, _bits, _min, _max):
    out_val = _data.astype(np.float32)
    _range = 2 ** _bits - 1

    out_val = (out_val - _min) / (_max - _min)
    out_val = np.round(out_val * _range) / _range
    out_val = ((out_val * (_max - _min)) + _min)
    return out_val.astype(_data.dtype)


def encode_mu_law(_data, u):
    assert _data.min() >= -1 and _data.max() <= 1 and np.issubdtype(_data.dtype, np.floating)
    out_val = np.sign(_data) * (np.log(1+u*np.abs(_data)) / np.log(1+u))
    return out_val


def decode_mu_law(_data, u):
    assert _data.min() >= -1 and _data.max() <= 1 and np.issubdtype(_data.dtype, np.floating)
    out_val = np.sign(_data) * (1/u) * (np.power(1+u, np.abs(_data))-1)
    return out_val


def cycle_mu_law(_data, u, bits):
    out_val = encode_mu_law(_data, u)
    out_val = quantize(out_val, bits)
    out_val = decode_mu_law(out_val, u)
    return out_val


def plot_sound_diff(_data, _data2, _data3, _freq, _time_ms, _title="???"):
    _max = int(_freq*(_time_ms/1000))
    fig, ax = plt.subplots()
    ax.plot(np.arange(0, _max)/_freq, _data[0:_max], label="Original")
    ax.plot(np.arange(0, _max) / _freq, _data2[0:_max], label="mu_law")
    ax.plot(np.arange(0, _max) / _freq, _data3[0:_max], label="DCMP")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)
    plt.title(_title)
    plt.show()


def encode_DPCM(_data, bits):
    out_val = _data.copy()
    E = out_val[0]
    for x in range(1, _data.shape[0]):
        diff = _data[x] - E
        diff = quantize2(diff, bits, _data.min(), _data.max())
        out_val[x] = diff
        E += diff
    return out_val


def decode_DPCM(_data):
    out_val = _data.copy()
    for x in range(1, _data.shape[0]):
        out_val[x] = out_val[x - 1] + _data[x]
    return out_val


def cycle_DPCM(_data, bits):
    out_val = encode_DPCM(_data, bits)
    out_val = decode_DPCM(out_val)
    return out_val


rcParams['figure.figsize'] = 10, 10
data, freq = sf.read('Lab07/sing_medium1.wav', dtype=np.float32)

print(freq, data.shape, np.unique(data).size)
if len(data.shape) > 1:
    data = data[:, 0]

bit = 6
_time_ms = 2000
_max = int(freq*(_time_ms/1000))
data2 = cycle_DPCM(data[0:_max], bit)
data1 = cycle_mu_law(data[0:_max], 255, bit)

plot_sound_diff(data, data1, data2, freq, 5, "Kompresja stratna")

# sd.play(data[0:_max], samplerate=freq, blocking=True)
# sd.play(data1, samplerate=freq, blocking=True)
# sd.play(data2, samplerate=freq, blocking=True)