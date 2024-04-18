import numpy as np
import argparse
import csv
import os
import glob
import numpy as np
from numpy import zeros, float32, float64
#from array import array
from ROOT import TFile, TTree
import re

DELIMITER=None # by default space and tabs are DELIMITER
SKIP_N_ROWS=0 # no header by default

class WAVE2ROOT:
    def __init__(self, args):
        self.wave_dir = args.wave_dir
        self.wave_files = self.list_wave_files(args.wave_dir)
        self.groups = self.group_by_prefix(self.wave_files)
        print("total number of wave files to be processed:", self.n_files)
        
    def list_wave_files(self, directory_path):
        files = glob.glob(os.path.join(directory_path, '*_Wave_*.txt'))
        files=sorted(files)
        self.n_files=len(files)
        return files

    def group_by_prefix(self, file_paths):
        """
        prefix XXXX-XXX_XXXXXX is uniquely determined by year-day_HHMMSS
        """
        filenames = [os.path.basename(path) for path in file_paths]
        groups = {}
        for fname in filenames:
            prefix = fname[:15] # XXXX-XXX_XXXXXX 
            if prefix in groups:
                groups[prefix].append(fname)
            else:
                groups[prefix] = [fname]
        return groups

    
    def convert(self):
        for prefix, filenames in self.groups.items():
            root_path='%s/%s_Wave.root' % (self.wave_dir, prefix)
            print("creating", root_path)
            ofile = TFile(root_path, 'RECREATE')
            tree = TTree('tree', 'CAENWaveDemo waveform data')
            for fname in filenames:
                print("processing ", fname)
                matches = re.findall(r'_(\d+)_(\d+)', fname)
                if matches:
                    last_match = matches[-1]
                    boardID, chID = map(int, last_match)
                else:
                    print("ERROR: no boardID and chID are found from file_paths")
                    exit(1)
                fpath = "%s/%s" % (self.wave_dir,fname)
                arr = np.loadtxt(fpath, delimiter=DELIMITER, skiprows=SKIP_N_ROWS, dtype=float64)
                n_samp = int(arr[0][3])
                ch_buffer=zeros(n_samp, dtype=np.int32)
                
                b_names = [] # keep track of new branch names

                # create ADC branch for this boardID chID
                b_name = 'adc_%d_%d' % (int(boardID), int(chID))
                b_type = "%s[%d]/I" % (b_name, n_samp)
                tree.Branch(b_name, ch_buffer, b_type)
                b_names.append(b_name)
                
                # create TTT branch for this boardID chID
                ttt = zeros(1, dtype=np.int64)
                b_name = "ttt_%d_%d" % (int(boardID), int(chID))
                b_type = "%s/I" % (b_name)
                tree.Branch(b_name, ttt, b_type)
                b_names.append(b_name)

                # only turn on branch in this iteration
                tree.SetBranchStatus("*", 0);
                for b in b_names:
                    tree.SetBranchStatus(b, 1);
                for i in range(len(arr)):
                    np.copyto(ch_buffer, arr[i][4:].astype(np.int32))
                    ttt[0]=int(arr[i][0])
                    tree.Fill()
                tree.Write()
            tree.SetBranchStatus("*", 1);
            tree.Write()
            ofile.Close()

def main(args):
    w2r = WAVE2ROOT(args)
    w2r.convert()
    print("------------------------")
    print("          Done          ")
    print("------------------------")

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a CSV file and work with ROOT files.")
    parser.add_argument("--wave-dir", required=True, help="Directory that contains all wave txt files")
    args = parser.parse_args()

    try:
        main(args)
    except Exception as e:
        print(f'An error occurred: {e}')
