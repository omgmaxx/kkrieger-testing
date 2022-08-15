import argparse
import csv
import datetime
import logging
import os
import re
import statistics
import subprocess
from configparser import ConfigParser
from pathlib import Path
from time import sleep
from typing import Optional
from logging.config import dictConfig

import matplotlib.pyplot as plt
import pyautogui


def setup_logging(folder: Path) -> None:
    """
    Setting up loggers

    :param folder: path for logging
    """
    logging_config = {
        "version": 1,
        'disable_existing_loggers': False,
        "formatters": {
            'standard': {
                'format': '%(asctime)s: [%(levelname)s]  %(message)s'
            }
        },
        "handlers": {
            'default': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': 'INFO',
            },
            'file1': {
                'class': 'logging.FileHandler',
                'filename': 'errors.log',
                'formatter': 'standard',
                'level': 'WARNING',
            },
            'file2': {
                'class': 'logging.FileHandler',
                'filename': folder / 'logging.log',
                'formatter': 'standard',
                'level': 'INFO',
            },
        },
        "loggers": {
            "": {
                'handlers': ['default', 'file1', 'file2'],
                'level': 'INFO'
            },
        }
    }
    dictConfig(logging_config)


def get_config() -> tuple[str, Path, Path, str]:
    """
    Gets settings from config.ini file

    :return: hotkey, path to fraps folder, path to benchmarks folder, game name
    """
    config = ConfigParser()
    config.read('config.ini')

    # Fraps benchmark hotkey
    hotkey = config.get('fraps', 'benchmark_command')
    if hotkey not in pyautogui.KEY_NAMES:
        raise KeyError('hotkey is not a viable key')

    # Fraps folder
    fraps_folder = Path(config.get('fraps', 'fraps_folder'))
    if not fraps_folder.exists():
        raise FileExistsError("fraps folder doesn't exist")

    # Fraps/benchmark folder
    benchmark_folder = config.get('fraps', 'benchmark_folder')
    if not benchmark_folder:
        benchmark_folder = fraps_folder / 'Benchmarks'
    else:
        benchmark_folder = Path(benchmark_folder)
    if not benchmark_folder.exists():
        raise FileExistsError("benchmark folder doesn't exist")

    # game name
    game_name = config.get('game', 'game_name')

    return hotkey, fraps_folder, benchmark_folder, game_name


def get_folder(game_name: str, result_folder: Path = None) -> Path:
    """
    Gets destination folder for results

    Path generates like "/results/{game_name}/{iter_number}/

    :param game_name: game name.exe
    :param result_folder: output folder for results
    :return: path to destination folder
    """
    # if output is not defined
    if not result_folder:
        result_folder = Path.cwd() / 'results'

    date_folder = result_folder / game_name / str(datetime.date.today())
    date_folder.mkdir(parents=True, exist_ok=True)
    list_of_iterations = next(os.walk(date_folder))[1]
    list_of_iterations.sort(key=int)
    try:
        last_iter_folder = list_of_iterations[-1]
    except IndexError:
        last_iter_folder = 0
    new_iter_folder = int(last_iter_folder) + 1

    target_folder = date_folder / str(new_iter_folder)
    target_folder.mkdir(exist_ok=True)

    return target_folder


def get_args() -> tuple[Optional[Path], Optional[Path]]:
    """
    Processes arguments given on initialization of script

    :return: path to game, path to output
    """
    parser = argparse.ArgumentParser(description='Autotest for kkrieger')
    parser.add_argument('-o', '--o', help='output folder')
    parser.add_argument('game_path', nargs='?', help='game folder')

    args = parser.parse_args()
    config = vars(args)

    try:
        game_folder = Path(config['game_path'])
    except TypeError:
        logging.warning('Game path is not specified, using project folder')
        game_folder = None

    try:
        output_folder = Path(config['o'])
    except TypeError:
        logging.warning('Output folder is not specified, using project folder')
        output_folder = None

    return game_folder, output_folder


def sleep_timer(time: [int, float]) -> None:
    """
    time.sleep with percent timer

    :param time: time in seconds
    """
    for tick in range(1, time + 1):
        sleep(1)
        percent = 100 / time * tick
        logging.info(f'{percent}%')


def use_key(key: str, interval: [int, float] = 0.1) -> None:
    """
    Alternative wrapper for keyDown and keyUp with custom interval

    (Press doesn't work)

    :param key: hotkey set in Fraps for Benchmarking
    :param interval: interval between keyDown and keyUp
    """
    pyautogui.keyDown(key)
    sleep(interval)
    pyautogui.keyUp(key)
    logging.info(f'pressed {key}')
    sleep(1)


def launch_game(game_name: str, game_folder: Path = None) -> subprocess.Popen:
    """
    Launches game

    :param game_name: game name.exe
    :param game_folder: path to game folder
    :return: game process
    """
    if game_folder:
        game_path = game_folder / game_name
    else:
        game_path = game_name
    logging.info(f'Launching game at {game_path}')
    process = subprocess.Popen([game_path, '-f'])
    logging.info('Waiting for game to initialize')
    sleep_timer(25)
    logging.info('Game initialized')
    return process


def take_screenshot(folder: Path, name: str) -> None:
    """
    Takes screenshot with {name} name

    :param folder: destination folder for results
    :param name: resulted screenshot name
    """
    scr_menu = pyautogui.screenshot()
    path = folder / name
    scr_menu.save(path)
    logging.info(f'taken screenshot at {path}')
    sleep(2)


def benchmarking(hotkey: str, time: int) -> None:
    """
    Making benchmarking using Fraps

    Presses hotkey for {time} seconds

    :param hotkey: hotkey set in Fraps for Benchmarking
    :param time: time in seconds to snap fps in game
    """
    use_key(hotkey)
    logging.info('starting benchmarking')

    use_key('w', interval=5)

    sleep(time)
    logging.info(f'benchmarked for {time} seconds')

    use_key(hotkey)
    logging.info('ending benchmarking')


def get_benchmark(benchmark_folder: Path, game_name: str) -> Path:
    """
    Looks for last .csv file in Fraps/Benchmarks folder with game_name and "fps" in name

    :param benchmark_folder: benchmarks folder
    :param game_name: game name
    :return: path to latest ***fps.csv
    """
    files = benchmark_folder.glob('*.csv')
    files = [str(x) for x in files]
    game_files = filter(lambda x: re.match(rf'.*{game_name}.*', x), files)
    game_files = filter(lambda x: re.match(r'.*fps.*', x), game_files)
    max_file = max(game_files, key=os.path.getctime)
    return Path(max_file)


def process_statistics(stat_csv: Path, folder: Path) -> None:
    """
    Processes statistics made by fraps

    Saves median fps to median_fps.txt and graph to fps.png

    :param stat_csv: .csv file made by Fraps
    :param folder: destination folder for results
    """
    fps_stats = list()
    with open(stat_csv, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            try:
                row = (int(row[0]))
            except ValueError:
                continue
            fps_stats.append(row)
    median_fps = statistics.median(fps_stats)
    file_path = folder / 'median_fps.txt'
    with file_path.open('w') as file:
        file.write(str(median_fps))
    logging.info(f'Median fps written to {file_path}')

    plt.plot(fps_stats)
    plt.xlabel('x - seconds')
    plt.ylabel('y - fps')
    plt.savefig(folder / 'fps.png')


def kill_process(process: subprocess.Popen) -> None:
    """
    Kills game process

    :param process: Process
    """
    logging.info('killing process')
    process.kill()
    sleep(2)


def main() -> None:
    # deserializing config
    hotkey, fraps_folder, benchmark_folder, game_name = get_config()

    # getting args
    game_folder, output_folder = get_args()

    # getting folder
    folder = get_folder(game_name=game_name, result_folder=output_folder)

    # preparing logger
    setup_logging(folder)

    # launching game
    process = launch_game(game_folder=game_folder, game_name=game_name)

    # press space to move to menu
    use_key('space')

    # menu screenshot
    take_screenshot(folder, 'scrn_menu.png')

    # launch game
    use_key('enter')

    # game screenshot before benchmark
    take_screenshot(folder, 'scrn_before.png')

    # benchmarking
    benchmarking(hotkey=hotkey, time=2)
    stat_csv = get_benchmark(benchmark_folder=benchmark_folder, game_name=game_name)
    process_statistics(stat_csv, folder)

    # game screenshot after benchmark
    take_screenshot(folder, 'scrn_after.png')

    # kill game
    kill_process(process)


if __name__ == "__main__":
    main()
