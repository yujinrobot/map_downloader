import argparse
from download import Conf_downloader, get_robot_uuid

def pars_args():
    parser = argparse.ArgumentParser(description="A simple tool to download robot configuration", prog='map_downloader',
                                     version='0.13')
    parser.add_argument("--skip_map", action="store_true", default=False, help="Skip map downloading but keep "
                                                                               "downloading semantics, task definition,"
                                                                               "and AR markers data." )
    return parser.parse_args()

def main():
    parsed_args = pars_args()
    dwl = Conf_downloader(get_robot_uuid(), skip_map=parsed_args.skip_map)
    dwl.process()
