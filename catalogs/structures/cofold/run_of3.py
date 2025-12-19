#!/usr/bin/env python

import os
from glob import glob

for filename in sorted(glob("*.json")):
    cmd = f"run_openfold predict --query_json {filename}"
    os.system(cmd)


