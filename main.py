import glob
import os
import shutil
import logging
import sys
from datetime import datetime
from distutils.dir_util import copy_tree

from forcast_sources.open_skiron import OpenSkiron
from forcast_sources.wind_guru import WindGuru
from forcast_sources.wind_guru_station import WindGuruStation

def _setup_app_folders(conf_folder,logger):
    if not os.path.isdir(conf_folder):
        try:
            # PyInstaller creates a temp folder and set the path in _MEIPASS
            if os.path.isdir(sys._MEIPASS):
                logger.debug(f"sys._MEIPASS:  {str(sys._MEIPASS)}")
                copy_tree(f"{sys._MEIPASS}{os.path.sep}{conf_folder}", f".{os.path.sep}{conf_folder}")
        except Exception as err:
            logger.debug(f"_setup_app_folders err {str(err)}")

def _get_resource_path():
    try:
        base_path = os.path.abspath(".")
    except Exception:
        base_path = os.path.abspath(".")
    return base_path
    # return os.path.join(base_path, relative_path)


def _reset_download_folder(download_path):
    if os.path.isdir(download_path):
        shutil.rmtree(download_path)
    if not os.path.isdir(download_path):
        os.makedirs(download_path)


def _init_logger(log_file):
    logger = logging.getLogger('wind_report')

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_file)

    logger.setLevel(logging.DEBUG)  # the logger level should be less/equal to its handlers
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.DEBUG)

    c_format = logging.Formatter('%(levelname)s-%(asctime)s: %(message)s')
    f_format = logging.Formatter('%(levelname)s-%(asctime)s: %(message)s')

    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger


if __name__ == '__main__':
    try:
        log_file = "wind_report.log"
        conf_folder = "conf"
        spots_file = "spots.csv"
        models_file = "wg_models.csv"
        download_folder = "downloads"
        out_excel_path = 'data.csv'

        logger = _init_logger(log_file)
        logger.info("Start")

        _setup_app_folders(conf_folder,logger)

        download_path = f'{os.path.dirname(os.path.realpath(__file__))}{os.path.sep}{download_folder}'
        _reset_download_folder(download_path)

        conf_path = f'{_get_resource_path()}{os.path.sep}{conf_folder}'

        archive_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f'Getting forecast from open-skiron start')
        forecast_source_open_skiron = OpenSkiron(download_path=download_path, out_excel_path=out_excel_path,
                                                 archive_timestamp=archive_timestamp)
        forecast_source_open_skiron.get_forecast_data(conf_path, spots_file)
        logger.info(f'Getting forecast from open-skiron end')

        logger.info(f'Getting forecast windguru start')
        forecast_source_wg = WindGuru(download_path=download_path, out_excel_path=out_excel_path,
                                      archive_timestamp=archive_timestamp)
        forecast_source_wg.get_forecast_data(conf_path, spots_file, models_file)
        logger.info(f'Getting forecast windguru end')

        logger.info(f'Getting wind station wg start')
        station_source_wg = WindGuruStation(download_path=download_path, out_excel_path=out_excel_path,
                                      archive_timestamp=archive_timestamp)
        station_source_wg.get_forecast_data(conf_path, spots_file)
        logger.info(f'Getting wind station wg end')

        _reset_download_folder(download_path)

        logger.info("Done")
    except Exception as err:
        logger.exception(f"Error :{err}")
        print(f"Error :{err}")
