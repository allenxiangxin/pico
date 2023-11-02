import argparse
import csv
import os
import glob
import numpy as np
from numpy import zeros, float32
#from array import array
from ROOT import TFile, TTree

"""
Global config
"""
SKIP_N_ROWS=2 # pico by default uses the first 2 rows as headers
DELIMITER="," # pico by default uses , as delimiter in csv
ACTIVE_CHAN=["A", "B", "C", "D"] # Header is skipped. So this is actually the Branch names.

class CSV2ROOT:
    def __init__(self, args):
        self.root_file = args.root_file
        if self.root_file !=  '.root':
            self.root_file += '.root'
        self.csv_files = self.list_files(args.csv_dir)
        print("total number of files:", self.n_files)

    def list_files(self, directory_path):
        files = glob.glob(os.path.join(directory_path, '*'))
        files=sorted(files)
        self.n_files=len(files)
        return files

    def load_a_trigger(self, file_path):
        """
        Pico save each trigger to a CSV file
        """
        arr = np.loadtxt(file_path, delimiter=DELIMITER, skiprows=SKIP_N_ROWS)
        return arr

    def write(self):
        """
        Create output root file
        Define TTree, where each branch is a channel (you can change the structure if you want)
        """
        ofile = TFile(self.root_file, 'RECREATE')
        tree = TTree('tree', 'picoscope waveform data')

        arr = self.load_a_trigger(self.csv_files[0])
        nrow, ncol = arr.shape
        n_samp = nrow
        n_chan = ncol-1 # the first column is time axis
        if n_chan !=len(ACTIVE_CHAN):
            print("ERROR: your ACTIVE_CHAN defined is not consistent with data")
            exit(1)

        # Define TTree structure
        time_buffer=zeros(n_samp, dtype=float32)
        tree.Branch('time', time_buffer,  "time[%d]/F" % n_samp)
        ch_buffers=[]
        for i in range(n_chan):
            ch_buffers.append(zeros(n_samp, dtype=float32))
            b_type = "%s[%d]/F" % (ACTIVE_CHAN[i], n_samp)
            tree.Branch(ACTIVE_CHAN[i], ch_buffers[i], b_type)

        # Fill, a trigger (file) is an entry
        for f in self.csv_files:
            arr = self.load_a_trigger(f)
            np.copyto(time_buffer, arr.T[0])
            for i in range(n_chan):
                np.copyto(ch_buffers[i], arr.T[i+1])
            tree.Fill()

        tree.Write()
        ofile.Close()


def main(args):
    c2r = CSV2ROOT(args)
    c2r.write()
    print(f"Data from '{args.csv_dir}' are written to a ROOT file '{c2r.root_file}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a CSV file and work with ROOT files.")
    parser.add_argument("--csv-dir", required=True, help="Directory that contains all CSV files")
    parser.add_argument("--root-file", required=True, help="ROOT file names")
    args = parser.parse_args()

    try:
        main(args)
    except Exception as e:
        print(f'An error occurred: {e}')

