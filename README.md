# Kkrieger autotester

## Set up

### Environment
Powershell:
```sh
py -m venv venv
.\venv\Scripts\activate.ps1         # you may need to set execution policies
pip install -r .\requirements.txt
```

### Fraps
- Download and install Fraps: https://fraps.com/download.php
- Tick FPS box in FPS/Benchmark Settings

### Kkrieger
- Unpack game to project folder or desirable direction
- [Optional] set win XP compatibility if game won't launch

### Config
- Set Benchmarking Hotkey in config.ini same as it is in Fraps (f11 by default)
- Set absolute path to fraps_folder 
- Set game name (i.e. "pno0001")
- [Optional] set absolute path to benchmark_folder (if path is not default)

## Usage

Don't forget to turn Fraps on

```
usage: kriegTesting.py [-h] [-o O] [game_path] 
```

- [-o] : Path for output folder
- [game_path] : Path to folder containing game executable

### References
```sh
py kriegTesting.py          # Executes game in project folder and places results to proj/results/
py kriegTesting.py c:/kkrieger -o d:/results    # Executes game in c:/kkrieger/ folder and places results to d:/results/
```

## Process
- Reading config
- Getting arguments
- Getting output folder
- Setting logger config
- Launching game (waiting 25 seconds for game to initialize)
- Pressing space to skip to menu
- Taking menu screenshot
- Pressing enter to start scene
- Taking screenshot before benchmark
- Benchmarking
  - press benchmark hotkey
  - walk forward (press 'W') for 5 seconds
  - wait customizable amount of time
  - press hotkey again
- Getting last viable .csv file from Fraps/benchmarks folder
- Processing gotten info
  - write median to txt file
  - create graph
- Taking screenshot after benchmark
- Killing game process

## Output

Output contains set of files:
- fps.png: graph showing framerate by seconds while benchmark was capturing
- logging.log: full log of actions
- median_fps.txt: median framerate of benchmark
- scrn_menu.png: screenshot in menu
- scrn_before.png: screenshot before benchmarking
- scrn_after.png: screenshot after benchmarking