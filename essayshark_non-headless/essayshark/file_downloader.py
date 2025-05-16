# essayshark/file_downloader.py

import time
from selenium.webdriver.common.by import By

class FileDownloader:
    def __init__(self, driver):
        self.driver = driver

    def download_file(self):
        try:
            file_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'get_additional_material.html')]")
            if file_links:
                print("Downloading first file...")
                file_links[0].click()
                time.sleep(3)  # Wait to ensure file download starts
            else:
                print("No files found for download.")
        except Exception as e:
            print("File download failed:", e)
