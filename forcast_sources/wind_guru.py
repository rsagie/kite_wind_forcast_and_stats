import io
import logging
import os
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd

from csv_files import CsvFiles


class WindGuru():

    # https://github.com/jeroentvb/wind-scrape
    # http://micro.windguru.cz/help.php

    def __init__(self, download_path, out_excel_path, archive_timestamp):
        self.logger = logging.getLogger('wind_report')
        self.archive_timestamp = archive_timestamp
        self.url = ""
        self.download_path = download_path
        self.out_excel_path = out_excel_path

    def get_forecast_data(self, conf_path, spots_file, models_file):
        user = os.getenv("WG_USER")
        pwd = os.getenv("WG_PASS")

        # forecast_spots = [{"model_name": "WG WRF-9", "model": "wrfegh", "location": "Naharia wind station",
        #                    "lat": 33.0, "lon": 35.1}]
        forecast_spots = []
        spots_df = pd.read_csv(f'{conf_path}{os.path.sep}{spots_file}', index_col=None)
        models_df = pd.read_csv(f'{conf_path}{os.path.sep}{models_file}', index_col=None)

        for _, model in models_df.iterrows():
            model_code = model['code'].strip()
            model_name = model['name'].strip()
            for __, spot in spots_df.iterrows():
                spot_dict = spot.to_dict()
                #spot_dict.update({"model_name": "WG WRF-9", "model": "wrfegh"})
                spot_dict.update({"model_name": model_name, "model": model_code})
                forecast_spots.append(spot_dict)

        for forecast_params in forecast_spots:
            # if "wind station" not in forecast_params.get("location", ""):
            #     continue
            if forecast_params.get('use', 0) == 0:
                continue
            self.logger.info(
                f'wg: model_name:{forecast_params.get("model_name")} location:{forecast_params.get("location")}')
            model = forecast_params.get("model")
            lat = forecast_params.get("lat")
            lon = forecast_params.get("lon")
            url = f"https://micro.windguru.cz/?lat={lat}&lon={lon}&m={model}&u={user}&p={pwd}&tz=auto"
            try:
                res = requests.get(url)
                df = self._convert_forecast_html_to_df(res.text)
                df = self._update_df_meta_data(df, forecast_params.get("location"), forecast_params.get("model_name"))
                CsvFiles.write_to_out_file(df, self.out_excel_path)
            except Exception as err:
                self.logger.warning(
                    f'wg: Failed to get forecast: forecast_params:{forecast_params} err:{str(err)}')

    def _add_year_month(self, src_date_str):

        if not isinstance(src_date_str, str) or len(src_date_str.split("-")) != 3:
            return src_date_str

        # the init date should be based on the html title rather then the datetime.now(), but this is easier
        month = datetime.now().month
        year = datetime.now().year
        curr_day = datetime.now().day

        date_parts = src_date_str.split("-")
        src_day = int(date_parts[1].replace('.', ''))
        src_hour = int(date_parts[2].replace('h', ''))

        if curr_day > src_day:  # e.g 29 > 1
            month = (month % 12) + 1
            if month == 1:
                year = year + 1

        date_str = f'{year}-{month}-{src_day}-{src_hour}'
        return date_str

    def _update_df_meta_data(self, df, location, model_name):
        df.rename(columns={'Date': 'timestamp', 'WSPD': 'wind', 'GUST': 'gust', 'WDEG': 'direction','TMP':'tmp'},
                  inplace=True)
        df['location'] = location
        df['source'] = model_name
        df['archive_timestamp'] = pd.to_datetime(self.archive_timestamp)
        df['timestamp'] = df.apply(lambda x: self._add_year_month(x['timestamp']), axis=1)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d-%H', errors='coerce')

        df = df[pd.to_numeric(df['wind'], errors='coerce').notnull()]
        return df

    def _convert_forecast_html_to_df(self, html):
        document = BeautifulSoup(html, "lxml")
        pre = document.find('pre')
        text = pre.getText().strip()
        text_lines = text.splitlines()
        text = ""
        for i, line in enumerate(text_lines):
            if i > 5:  # skip the title lines
                if i == 7:  # unit names
                    continue
                while '  ' in line:  # minimize the spaces (to be replaced by ',')
                    line = line.strip()
                    line = line.replace('  ', ' ')
                if i >= 9:  # this is where the actual data starts
                    # The first 3 'words' are the date e.g 'Fri 30. 6h'
                    line = "-".join(line.split()[0:3]) + "," + ",".join(line.split()[3:])
                line = line.replace(' ', ',')
                if len(line) > 0:
                    text = f'{text}{line}\n'
        text = text.replace(' ', ',')
        data = io.StringIO(text)
        df = pd.read_csv(data, sep=",")
        return df

        # with open(file_name) as document_fp
