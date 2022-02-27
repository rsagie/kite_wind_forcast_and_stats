import csv
import glob
import logging
import ntpath
import os
import sys
import time
import zipfile
from pathlib import Path
from datetime import date
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from OpenSkironDownloadPage import OpenSkironDownloadPage
from csv_files import CsvFiles


class OpenSkiron():
    def __init__(self,download_path,out_excel_path,archive_timestamp):
        self.logger = logging.getLogger('wind_report')
        self.archive_timestamp = archive_timestamp
        self.url = "https://openskiron.org/he/%D7%A7%D7%91%D7%A6%D7%99%D7%9D-%D7%9C%D7%94%D7%95%D7%A8%D7%93%D7%94"
        self.download_path = download_path
        self.out_excel_path = out_excel_path
        self.driver = self._new_chrome_browser(headless=False, downloadPath=download_path)

    def get_forecast_data(self,conf_path, spots_file):
        try:
            self.driver.get(self.url)
            self._download_openskiron_zip_files()
            self._extract_zip_files()
            spots_df = pd.read_csv(f'{conf_path}{os.path.sep}{spots_file}', index_col=None)

            main_df = self._export_csv_files_to_unified_data_frame(filter="*.csv",
                                                                   spots_df=spots_df)
            main_df = self._update_df_meta_data(main_df)
            CsvFiles.write_to_out_file(main_df, self.out_excel_path)
        except Exception as err:
            print(f"Error :{err}")
        finally:
            time.sleep(3)
            self.driver.quit()

    def _update_df_meta_data(self, df):
        df.rename(columns={'Date': 'timestamp', 'Wind Speed': 'wind', 'Gusts': 'gust', 'Direction': 'direction'},
                  inplace=True)
        df['archive_timestamp'] = pd.to_datetime(self.archive_timestamp)
        return df

    def _new_chrome_browser(self, headless=True, downloadPath=None):
        """ Helper function that creates a new Selenium browser """
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('headless')
        if downloadPath is not None:
            prefs = {}
            Path(downloadPath).mkdir(parents=True, exist_ok=True)

            prefs["profile.default_content_settings.popups"] = 0
            prefs["download.default_directory"] = downloadPath
            options.add_experimental_option("prefs", prefs)
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        return browser

    def _download_openskiron_zip_files(self):
        open_skiron_download_page = OpenSkironDownloadPage(self.driver)
        open_skiron_download_page.page_loaded()
        open_skiron_download_page.download_zip_files(self.download_path)

    def _extract_zip_files(self):
        files_list = os.listdir(self.download_path)
        self.logger.debug(f'open-skiron: files_list: {files_list}')
        for file in files_list:
            if file.endswith(".zip"):
                file_path = f'{self.download_path}{os.path.sep}{file}'
                self.logger.info(f'open-skiron: extract file_path: file_path: {file_path}')
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    # zip_ref.extractall(download_path+"\\")
                    try:
                        self.logger.debug(f'open-skiron: extract b4 {file_path}')
                        zip_ref.extractall(self.download_path + os.path.sep)
                        self.logger.debug(f'open-skiron: extract af {file_path}')
                    except Exception as err:
                        self.logger.warning(f'open-skiron: fail to extract {file_path} err:{str(err)}')


    def _spot_in_use_spots_list(self,spots_df,spot_file_path):
        use_spots = spots_df[spots_df['use'] == 1].location.to_list()
        for spot in use_spots:
            if spot.replace(" ","_").lower() in spot_file_path.lower():
                return True
        return False

    def _export_csv_files_to_unified_data_frame(self,filter, spots_df):
        files = [f for f in glob.glob(self.download_path + os.path.sep + "**/"+filter, recursive=True) if self._spot_in_use_spots_list(spots_df,f)]

        main_df = pd.DataFrame()
        year_offset = (date.today().year) - 1900
        for f in files:
            df = pd.read_csv(f, skiprows=[0,1])

            #Set timestamp
            df = df.rename(columns={"Date/Time": 'timestamp'})
            #errors='coerce' will convert non dates to NaT
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%m%d-%H%M',errors='coerce') + pd.offsets.DateOffset(years=year_offset)

            #Set location
            fname = ntpath.basename(f)
            #df['location'] = "_".join(fname.split('_')[2:-2]) #e.g fname = '18z_1km_Ako_Hatmarim_wind_station.csv'
            df['location'] = "_".join(fname.split('_')[2:]).replace(".csv","").replace("_"," ") #e.g fname = '18z_1km_Ako_Hatmarim_wind_station.csv'

            #Set source
            with open(f, newline='') as csv_f:
                reader = csv.reader(csv_f)
                df['source'] = next(reader)[0]  # gets the first line

            main_df = pd.concat([main_df, df])
            pass

        return main_df

    # def _create_excel(self,main_df):
    #     writer = pd.ExcelWriter(self.out_excel_path, engine='xlsxwriter')
    #     main_df.to_excel(writer, sheet_name='data',index=False)# remove the index column
    #
    #     #workbook = xlsxwriter.Workbook(excel_file_path)
    #     # Get the xlsxwriter objects from the dataframe writer object.
    #     workbook = writer.book
    #     workbook.close()
    #     #writer.save()