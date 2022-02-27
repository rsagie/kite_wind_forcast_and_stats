import logging
from datetime import datetime
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WebPage:

    def __init__(self, driver):
        self.driver = driver
        self.load_condition = None
        self.logger = logging.getLogger('wind_report')


    def page_loaded(self):
        print(f"Waiting for {type(self).__name__}")
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(self.load_condition))
        print(f"{type(self).__name__} was loaded")

    def wait_and_click(self, xpath=None, id=None, timeout=10):
        if xpath != id:
            now = datetime.now()
            while (datetime.now() - now).seconds < timeout:
                try:
                    if xpath is not None:
                        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                        search = self.driver.find_element_by_xpath(xpath)
                    elif id is not None:
                        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.ID, id)))
                        search = self.driver.find_element_by_id(id)
                    return search.click()
                except Exception as err:
                    if (datetime.now() - now).seconds < timeout:
                        print(f"wait_and_click error :{err}")
                        sleep(1)
                        pass
                    else:
                        raise err
        else:
            raise ValueError('Only one of either "xpath" or "id" argument should be provided but not both')