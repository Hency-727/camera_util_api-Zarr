'''
Author: HencyCHEN
Date: 2025-07-25 16:11:34
LastEditTime: 2025-07-29 19:22:30
LastEditors: HencyCHEN
Description: main function for one camera
'''
if __name__ == "__main__":
    import sys
    import os
    import pathlib
    ROOT_DIR = str(pathlib.Path(__file__).parent.parent)
    sys.path.append(ROOT_DIR)
    os.chdir(ROOT_DIR)

from omegaconf import OmegaConf
from utils.camera_driver import main

if __name__ == "__main__":
    # using d435i /d455i return 1，or 0
    OmegaConf.register_new_resolver(
                                    "is_realsense",
                                    lambda s: 1 if s in ("d455i", "d435i") else 0
                                    )
    # 1. load config from config.yaml
    cfg = OmegaConf.load("scripts/config.yaml")
    # 2. read command line arguments and merge together with cfg
    cli_cfg = OmegaConf.from_cli()
    # print(cli_cfg)
    cfg = OmegaConf.merge(cfg, cli_cfg)
    # print(cfg)
    print(f"using realsense camera : {bool(cfg.is_multi.record.REALSENSE)}")
    main(cfg)
