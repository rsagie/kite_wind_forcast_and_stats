import io
import json
import logging
import os
from datetime import datetime, date, timedelta

import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame

from csv_files import CsvFiles


class WindGuruStation():

    # https://stations.windguru.cz/json_api_stations.html
    # curl 'https://www.windguru.cz/int/iapi.php?q=station_data&id_station=2050&date_format=Y-m-d%20H%3Ai%3As%20T&from=2021-05-01%2018:11:00' -H 'Referer: https://www.windguru.cz/station/2050'

    def __init__(self, download_path, out_excel_path, archive_timestamp):
        self.logger = logging.getLogger('wind_report')
        self.archive_timestamp = archive_timestamp
        self.url = ""
        self.download_path = download_path
        self.out_excel_path = out_excel_path

    def get_forecast_data(self, conf_path, spots_file):
        # forecast_spots = [{"location": "Naharia wind station", id_station = 2050}]
        stations_spots = []
        spots_df = pd.read_csv(f'{conf_path}{os.path.sep}{spots_file}', index_col=None)
        spots_df = spots_df.dropna(subset=['id_station'])
        for _, station in spots_df.iterrows():
            # if "wind station" not in station.location:
            #     continue
            if station.get('use', 0) == 0:
                continue
            self.logger.info(f'wg: model_name: live station, location:{station.location}')

            id_station = station.id_station
            yesterday = date.today() - timedelta(days=1)
            from_date = "2021-05-01%2018:11:00"
            from_date = yesterday.strftime("%Y-%m-%d %H:%M:%S")
            url = f"https://www.windguru.cz/int/iapi.php?q=station_data&tz=auto&id_station={id_station}&avg_minutes=30&date_format=Y-m-d%20H%3Ai%3As%20T&from={from_date}"

            try:
                res = requests.get(url,headers={'Referer':f"https://www.windguru.cz/station/{id_station}"})
                res_dict = json.loads(res.text)
                df = DataFrame.from_dict(res_dict)

                df = self._update_df_meta_data(df, station.location, model_name="WG live station")
                #archive_timestamps = [self.archive_timestamp]
                archive_timestamps = self._get_archive_timestamp_of_history_forecasts(df['timestamp'])
                for archive_timestamp in archive_timestamps:
                    df['archive_timestamp'] = pd.to_datetime(archive_timestamp)
                    CsvFiles.write_to_out_file(df.copy(), self.out_excel_path)
            except Exception as err:
                self.logger.warning(
                    f'wg: Failed to get station data err:{str(err)}')

    def _get_archive_timestamp_of_history_forecasts(self, live_data_time_stamp):
        min_live_time = live_data_time_stamp.min()
        max_live_time = live_data_time_stamp.max()
        archive_df = pd.read_csv(self.out_excel_path)
        archive_df['timestamp'] = pd.to_datetime(archive_df['timestamp'])
        df = archive_df[(archive_df['timestamp'] >= min_live_time) & (archive_df['timestamp'] <= max_live_time)]
        return pd.unique(df[' archive_timestamp'].values)

    def _update_df_meta_data(self, df, location, model_name):
        #df.rename(columns={'wind_avg': 'wind', 'gustiness': 'gust', 'wind_direction': 'direction'},  inplace=True)
        df.rename(columns={'wind_avg': 'wind', 'wind_max': 'gust', 'wind_direction': 'direction'},  inplace=True)
        df['location'] = location
        df['source'] = model_name
        df['timestamp'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

        df = df[pd.to_numeric(df['wind'], errors='coerce').notnull()]
        return df

