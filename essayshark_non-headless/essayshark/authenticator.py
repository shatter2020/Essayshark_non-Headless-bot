# essayshark/authenticator.py

import time
import os
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from essayshark.config import LOGIN_URL, ESSAYSHARK_URL, USERNAME, PASSWORD  # Import login details
from essayshark.bid_handler import BidHandler
from essayshark.file_downloader import FileDownloader
from essayshark.navigation_helper import NavigationHelper


class Authenticator:
    def __init__(self, driver):
        self.driver = driver
        self.bid_handler = BidHandler(driver)
        self.file_downloader = FileDownloader(driver)
        self.navigation = NavigationHelper(driver)
        self.download_dir = os.path.join(os.path.expanduser("~"), "Downloads")

    def login(self):
        print("Logging in...")
        self.driver.get(LOGIN_URL)
        time.sleep(3)  # Allow page to load

        try:
            email_input = self.driver.find_element(By.NAME, "login")
            continue_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            email_input.send_keys(USERNAME)
            continue_button.click()
            time.sleep(3)

            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(PASSWORD)
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            time.sleep(5)

            print("Login successful! Redirecting to orders page...")
            self.driver.get(ESSAYSHARK_URL)
            time.sleep(3)

            while True:
                self.process_orders()
        except Exception as e:
            print("Login failed:", e)

    def process_orders(self):
        try:
            order_table = self.driver.find_elements(By.XPATH,
                                                    "//th[contains(text(), 'Order')]/following::a[contains(@href, '/writer/orders/')]")
            if order_table:
                print("Opening first available order...")
                order_table[0].click()
                time.sleep(3)
                self.handle_order()
                self.driver.get(ESSAYSHARK_URL)
                time.sleep(3)
            else:
                print("No available orders found. Refreshing page...")
                self.driver.refresh()
                time.sleep(5)
        except Exception as e:
            print("Failed to process order:", e)

    def handle_order(self):
        try:
            timer_element = self.driver.find_element(By.ID, "id_read_timeout_msg_container")
            time_text = timer_element.text.strip()
            time_left = self.bid_handler.parse_timer_value(time_text)
            if time_left < 0:
                raise Exception("Invalid timer value")
            print(f"Timer detected: {time_left} seconds remaining.")

            # While timer is running: place initial bid of 3 and download file
            print("Placing initial bid of 3...")
            bid_input = self.driver.find_element(By.ID, "id_bid4")
            bid_input.clear()
            bid_input.send_keys("3")
            time.sleep(1)  # Ensure bid is entered
            print("Downloading one file...")
            self.download_order_file()

            # Wait for timer to reach zero
            print(f"Waiting for timer to reach zero ({time_left} seconds)...")
            while time_left > 0:
                time.sleep(1)
                time_text = self.driver.find_element(By.ID, "id_read_timeout_msg_container").text.strip()
                time_left = self.bid_handler.parse_timer_value(time_text)
                print(f"Time left: {time_left} seconds...")

            # Click Apply Order after timer reaches zero
            print("Timer reached zero. Clicking Apply Order button...")
            apply_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "apply_order"))
            )
            apply_button.click()
            time.sleep(2)  # Wait for error to appear if any

            # Handle bid error
            try:
                error_message = self.driver.find_element(By.ID, "id_bid4-error").text
                if "Minimal bid amount" in error_message:
                    min_bid = self.bid_handler.extract_min_bid(error_message)
                    print(f"Bid error detected. Minimum bid required: {min_bid}")
                    print("Clearing initial bid of 3...")
                    bid_input.clear()
                    print(f"Placing new bid of {min_bid}...")
                    bid_input.send_keys(str(min_bid))
                    time.sleep(1)
                    print("Clicking Apply Order button again...")
                    apply_button.click()
                    time.sleep(2)
                    print("Order successfully placed with minimum bid.")
                else:
                    print("Unexpected error message:", error_message)
            except Exception as e:
                print("No bid error occurred. Order successfully placed with initial bid of 3.")

        except Exception as e:
            print("No timer found or error occurred:", e)
            # Fallback without timer
            print("Placing initial bid of 3...")
            bid_input = self.driver.find_element(By.ID, "id_bid4")
            bid_input.clear()
            bid_input.send_keys("3")
            time.sleep(1)
            print("Downloading one file (if available)...")
            self.download_order_file()

            print("Clicking Apply Order button...")
            apply_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "apply_order"))
            )
            apply_button.click()
            time.sleep(2)

            try:
                error_message = self.driver.find_element(By.ID, "id_bid4-error").text
                if "Minimal bid amount" in error_message:
                    min_bid = self.bid_handler.extract_min_bid(error_message)
                    print(f"Bid error detected. Minimum bid required: {min_bid}")
                    print("Clearing initial bid of 3...")
                    bid_input.clear()
                    print(f"Placing new bid of {min_bid}...")
                    bid_input.send_keys(str(min_bid))
                    time.sleep(1)
                    print("Clicking Apply Order button again...")
                    apply_button.click()
                    time.sleep(2)
                    print("Order successfully placed with minimum bid.")
                else:
                    print("Unexpected error message:", error_message)
            except Exception as e:
                print("No bid error occurred. Order successfully placed with initial bid of 3.")

    def download_order_file(self):
        try:
            file_link = self.driver.find_element(By.XPATH,
                                                 "//a[contains(@href, '/writer/get_additional_material.html')]")
            file_url = file_link.get_attribute("href")
            print(f"Downloading file from: {file_url}")

            before_files = set(os.listdir(self.download_dir))
            file_link.click()

            timeout = 15
            elapsed = 0
            while elapsed < timeout:
                after_files = set(os.listdir(self.download_dir))
                new_files = after_files - before_files
                if new_files:
                    downloaded_file = new_files.pop()
                    print(f"File downloaded: {downloaded_file}")
                    return
                time.sleep(1)
                elapsed += 1
            print("Error: File did not download within 15 seconds.")
        except Exception as e:
            print("No additional files found or download failed:", e)
            print("Proceeding without file.")