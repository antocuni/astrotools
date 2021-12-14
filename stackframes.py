#!/home/antocuni/pypy/misc/pysiril/venv/bin/python

import sys
import os
import shutil
from pathlib import Path

from pysiril.siril   import Siril
from pysiril.wrapper import *

class Script:

    def __init__(self, workdir):
        self.app = Siril('/home/antocuni/bin/siril', delai_start=1)
        self.workdir  = workdir
        self.cmd = Wrapper(self.app)
        self.app.Open()

        #3. Set preferences
        self.process_dir = os.path.join(self.workdir, 'process')
        Path(self.process_dir).mkdir(exist_ok=True)
        self.cmd.set16bits()
        self.cmd.setext('fit')

    ## def master_bias(bias_dir, process_dir):
    ##     cmd.cd(bias_dir )
    ##     cmd.convert( 'bias', out=process_dir, fitseq=True )
    ##     cmd.cd( process_dir )
    ##     cmd.stack( 'bias', type='rej', sigma_low=3, sigma_high=3, norm='no')

    def import_bias(self, src, dst):
        assert src.endswith('.fit')
        assert dst.endswith('.fit')
        abs_dst = os.path.join(self.process_dir, dst)
        shutil.copy(src, abs_dst)
        print(f'cp {src} {abs_dst}')
        return dst[:-4]

    def master_flat(self, flat_dir, master_bias, *, outname):
        flat_dir = os.path.join(self.workdir, flat_dir)
        self.cmd.cd(flat_dir)
        self.cmd.convertraw(outname, out=self.process_dir, fitseq=True)
        self.cmd.cd(self.process_dir)
        if master_bias is not None:
            self.cmd.preprocess(outname, bias=master_bias)
            outname = 'pp_' + outname
        self.cmd.stack(outname, type='rej', sigma_low=3, sigma_high=3, norm='mul')
        self.cmd.cd(self.workdir)
        return outname + '_stacked'

    def master_dark(self, dark_dir, *, outname):
        dark_dir = os.path.join(self.workdir, dark_dir)
        self.cmd.cd(dark_dir)
        self.cmd.convertraw(outname, out=self.process_dir, fitseq=True)
        self.cmd.cd(self.process_dir)
        self.cmd.stack(outname, type='rej', sigma_low=3, sigma_high=3, norm='no')
        self.cmd.cd(self.workdir)
        return outname + '_stacked'

    def preprocess_lights(self, light_dir, *, outname, master_dark=None, master_flat=None):
        assert master_dark is not None
        assert master_flat is not None
        light_dir = os.path.join(self.workdir, light_dir)
        self.cmd.cd(light_dir)
        self.cmd.convertraw(outname, out=self.process_dir, fitseq=True)
        self.cmd.cd(self.process_dir)
        self.cmd.preprocess(outname,
                            dark=master_dark,
                            flat=master_flat,
                            cfa=True,
                            equalize_cfa=True,
                            debayer=True)
        self.cmd.cd(self.workdir)
        return 'pp_' + outname

    def register_and_stack(self, input_seqname, out):
        self.cmd.cd(self.process_dir)
        self.cmd.register(input_seqname)
        self.cmd.stack('r_' + input_seqname, type='rej', sigma_low=3, sigma_high=3,
                       norm='addscale', output_norm=True, out=out)
        self.cmd.cd(self.workdir)

    def merge(self, input_seqs, outseq):
        self.cmd.cd(self.process_dir)
        self.cmd.merge(input_seqs, outseq)
        self.cmd.cd(self.workdir)
        return outseq


def main():
    s = None
    calib = '/home/antocuni/foto/stars/calibration'
    
    try:
        s = Script("/tmp/M42/")

        # lights/iso1600-30.0s-F8.0/
        bias_1600 = s.import_bias(calib + '/bias-iso1600/master_bias_iso1600.fit', 'bias_1600.fit')
        flat_1600 = s.master_flat(calib + '/flat-canon-300mm-F8/', master_bias=bias_1600, outname='flats_1600')
        dark_30_1600 = s.master_dark('./darks/iso1600-30.0s-F8.0', outname='darks_30_1600')
        lights_30_1600 = s.preprocess_lights(
            './lights/iso1600-30.0s-F8.0',
            outname='lights_30_1600',
            master_dark=dark_30_1600,
            master_flat=flat_1600)

        # lights/iso1600-15.0s-F8.0/
        dark_15_1600 = s.master_dark('./darks/iso1600-15.0s-F4.0', outname='darks_15_1600')
        lights_15_1600 = s.preprocess_lights(
            './lights/iso1600-15.0s-F8.0',
            outname='lights_15_1600',
            master_dark=dark_15_1600,
            master_flat=flat_1600)

        # lights/iso800-15.0s-F8.0/
        flat_800 = s.master_flat(calib + '/flat-canon-300mm-F8/', master_bias=None, outname='flats_800')
        dark_15_800 = s.master_dark('./darks/iso800-15.0s-F8.0', outname='darks_15_800')
        lights_15_800 = s.preprocess_lights(
            './lights/iso800-15.0s-F8.0',
            outname='lights_15_800',
            master_dark=dark_15_800,
            master_flat=flat_800)

        assert lights_30_1600 == 'pp_lights_30_1600'
        assert lights_15_1600 == 'pp_lights_15_1600'
        assert lights_15_800  == 'pp_lights_15_800'

        # we put lights_15_800 first so that the result will be aligned to it
        all_lights = s.merge([lights_15_800, lights_30_1600, lights_15_1600], outseq='all_lights')

        s.register_and_stack(lights_30_1600, out='../result-30-1600')
        s.register_and_stack(lights_15_1600, out='../result-15-1600')
        s.register_and_stack(lights_15_800,  out='../result-15-800')
        s.register_and_stack(all_lights, out='../result-all')

        s.cmd.close() # ???
        
    finally:
        if s:
            s.app.Close()

if __name__ == '__main__':
    main()
