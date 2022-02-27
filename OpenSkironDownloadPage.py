import os
from datetime import datetime
from time import sleep
from web_page import WebPage
from selenium.webdriver.common.by import By


class OpenSkironDownloadPage(WebPage):

    def page_loaded(self):
        self.load_condition = (By.XPATH, '//*[@id="jsn-pos-user3"]/div/div/div/div/div/table/tbody/tr[2]/td[1]')
        super().page_loaded()

    def download_zip_files(self,download_path):
        files_list_b4 = os.listdir(download_path)
        files_to_download = ['2','3','4','5']
        for file_id in files_to_download:
            self.wait_and_click(xpath=f'//*[@id="jsn-pos-user3"]/div/div/div/div/div/table/tbody/tr[{file_id}]/td[1]/a')
        files_list_af = os.listdir(download_path)

        # wait until all files were downloaded before moving on
        timeout = 30 #wait max sec for all files to download
        now = datetime.now()
        all_files_were_downloaded = self._wait_for_all_files(download_path, files_list_b4, files_to_download)
        while ((datetime.now() - now).seconds < timeout) and not all_files_were_downloaded:
            sleep(1)
            all_files_were_downloaded = self._wait_for_all_files(download_path, files_list_b4, files_to_download)

    def _wait_for_all_files(self, download_path, files_list_b4, files_to_download):
        files_list_af = [file for file in os.listdir(download_path) if file.endswith(".zip")]
        all_files_were_downloaded = (len(files_to_download) <= (len(files_list_af) - len(files_list_b4)))
        if not all_files_were_downloaded:
            self.logger.debug(f"OpenSkironDownloadPage wait_for_all_files files_list_af:{files_list_af}")
        else:
            self.logger.debug(f"OpenSkironDownloadPage ready to move on :{files_list_af}")
        return all_files_were_downloaded

