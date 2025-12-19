#!/usr/bin/env python

import os
from glob import glob

for filename in sorted(glob("*.yaml")):
    cmd = f"boltz predict {filename} --diffusion_samples 5 --use_msa_server"
    os.system(cmd)


