# To ROOT

Useful scripts that:
1. converts picoscope files (many CSV) to ROOT
2. converts CAENWaveDemo Wave files (TXT) to ROOT

# Install pyROOT
The following code needs pyROOT.
I think it is easier to install pyROOT on Linux or MacOS via conda. See: https://iscinumpy.gitlab.io/post/root-conda/

# Convert CSV to ROOT
Picoscope is nice, but the saved waveform data is in annoying format. The default .psdata is proprietary to pico. The altertaive is to save many CSV files in a folder (each corresponds to a trigger). 

Usage:
```bash
python csv2root.py --help
```

Be sure to check global config parameters defined at the begining of the script.

# Convert CAENWaveDemo Wave TXT to ROOT

Usage:
```bash
python wave2root.py --help
```
