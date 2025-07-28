'''
Author: HencyCHEN
Date: 2025-07-25 16:11:34
LastEditTime: 2025-07-27 18:23:57
LastEditors: HencyCHEN
Description: main function for multi cameras
'''
if __name__ == "__main__":
    import sys
    import os
    import pathlib
    ROOT_DIR = str(pathlib.Path(__file__).parent.parent)
    sys.path.append(ROOT_DIR)
    os.chdir(ROOT_DIR)

from omegaconf import OmegaConf
from utils.multi_camera_driver import main

if __name__ == "__main__":
    # 1. load config from config.yaml
    cfg = OmegaConf.load("scripts/config.yaml")
    # 2. read command line arguments and merge together with cfg
    cli_cfg = OmegaConf.from_cli()
    # print(cli_cfg)
    cfg = OmegaConf.merge(cfg, cli_cfg)
    # print(cfg)
    main(cfg)