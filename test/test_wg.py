
from forcast_sources.wind_guru import WindGuru

class TestWindGuru(object):

    def test_convert_forecast_html_to_df_should_return_df(self):
        download_path = "/TODO"  # TODO
        forecast_source_wind_guru = WindGuru(download_path=download_path)
        # forecast_source_wind_guru.get_forecast_data()
        file_name = "./data/wg-wrfegh.html"
        with open(file_name) as html:
            df = forecast_source_wind_guru._convert_forecast_html_to_df(html)
            assert df.shape == (82,12)
