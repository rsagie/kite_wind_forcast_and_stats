import os
import pandas as pd

from csv_files import CsvFiles
from forcast_sources.wind_guru import WindGuru


class TestCsvFiles(object):

    def test_df_to_new_csv(self):
        csv_file = 'test_csv.csv'
        df = self.init(csv_file)
        CsvFiles.write_to_out_file(df, csv_file)
        test_df = pd.read_csv(csv_file)
        assert test_df.shape == (82,6)

    def test_df_append_to_csv(self):
        csv_file = 'test_csv.csv'
        df = self.init(csv_file)
        CsvFiles.write_to_out_file(df, csv_file)
        test_df = pd.read_csv(csv_file)
        assert test_df.shape == (82,6)

        CsvFiles.write_to_out_file(df, csv_file)
        test_df = pd.read_csv(csv_file)
        assert test_df.shape == (82*2,6)

    def create_df(self):
        download_path = "/TODO"  # TODO
        forecast_source_wind_guru = WindGuru(download_path=download_path)
        file_name = "./data/wg-wrfegh.html"
        with open(file_name) as html:
            df = forecast_source_wind_guru._convert_forecast_html_to_df(html)
            forecast_params = {"model_name": "WG WRF-9", "model": "wrfegh", "location": "Naharia wind station",
                               "lat": 29.5,
                               "lon": -40.9}
            df = forecast_source_wind_guru._update_df_meta_data(df, forecast_params.get("location"), forecast_params.get("model_name"))

            return df

    def init(self, csv_file):
        try:
            os.remove(csv_file)
        except Exception:
            pass
        df = self.create_df()
        return df
