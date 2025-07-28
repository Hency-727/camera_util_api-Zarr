
# camera_util_api-Zarr
this repo includes a demo to collect zarr-format dataset from one camera or multi cameras with timestamps
## what does this repo do?
this repository provides a flexible Python toolkit for capturing one or more camera streams, storing the frames efficiently in Zarr format with configurable compression, and later playing them back. It uses OpenCV for video I/O, Zarr + Blosc for fast, chunked storage, and OmegaConf for easy CLI-based configuration of recording and playback parameters.
## how to install?
```python
pip install opencv-python, zarr, numcodecs, omegaconf
```
## how to use?
```python
git clone https://github.com/Hency-727/camera_util_api-Zarr.git
cd camera_util_api
```
### single camera recording mode
```bash
ls /dev/video* # make sure that your cameras are exiting
```
``` python
# run at camera_util_api directory and record one camera frames, press 'q' to exiting recording
python scripts/main_single.py \
       mode=record \  # mode=record
       camera_mode=is_single # camera_mode=is_multi
```
```bash
# then u should see the zarr file in the directory /data, e.g. gelsight_mini
$ tree data/single_camera/ -L 4
data/single_camera/
└── gelsight_mini
    └── visual
        └── 001.zarr # zarr file from 001 - N
            ├── frames
            └── timestamps
```
### multi cameras recording mode

``` python
# run at camera_util_api directory and record multi-cameras frames, press 'q' to exiting recording
python scripts/main_multi.py \
       mode=record \  # mode=record
       camera_mode=is_multi # camera_mode=is_multi
```
OR
``` python
# run at camera_util_api directory and record multi-cameras frames
python scripts/main_multi.py 
```
```bash
$ tree data/ -L 1
data/
├── multi_cameras
└── single_camera
```
```bash
# then u should see the zarr file in the directory /data, e.g. gelsight_mini and d435i
$ tree data/multi_cameras/ -L 4
data/multi_cameras/
├── d435i
│   └── visual
│       └── 001.zarr
│           ├── frames
│           └── timestamps
└── gelsight_mini
    └── visual
        └── 001.zarr
            ├── frames
            └── timestamps

```
### camera playing mode
``` python
# run at camera_util_api directory and play camera frames
python scripts/main_play.py \
    play_path=${.zarr_path} 
```

### self-defined
```python 
# config file, all u need to do is change sensor name and path
mode: is_multi
camera_mode: record                      # record or play
default_sensor: d435i                    # default sensor name
category_type: "visual"                  # catagory: visual, piezoresistance
camera_index: 0                          # camera indexes, defalut: /dev/video0
camera_index_1: 0
camera_index_2: 2                        
```
```python
# main function
from omegaconf import OmegaConf
from utils.camera_driver import main
# from utils.multi_camera_driver import main # -> multi cameras recording mode
# from utils.camera_driver import play_frame # -> play mode

if __name__ == "__main__":
    # 1. load config from config.yaml
    cfg = OmegaConf.load("scripts/config.yaml")
    # 2. read command line arguments and merge together with cfg
    cli_cfg = OmegaConf.from_cli()
    # print(cli_cfg)
    cfg = OmegaConf.merge(cfg, cli_cfg)
    # print(cfg)
    main(cfg)
    # play_frame(cfg)
```