# essayshark/navigation_helper.py

import time
from essayshark.config import ESSAYSHARK_URL

class NavigationHelper:
    def __init__(self, driver):
        self.driver = driver

    def navigate_to_orders(self):
        print("Navigating to Available Orders...")
        self.driver.get(ESSAYSHARK_URL)
        time.sleep(3)  # Allow the page to load
