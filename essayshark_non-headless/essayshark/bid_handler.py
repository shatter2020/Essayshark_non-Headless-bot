# essayshark/bid_handler.py

import time
import re
from selenium.webdriver.common.by import By
from essayshark.config import INITIAL_BID_AMOUNT, MAX_RETRIES

class BidHandler:
    def __init__(self, driver):
        self.driver = driver

    def place_bid(self, retry_count=0):
        print("Attempting to place bid...")

        # Step 1: Wait for the timer to reach zero before bidding
        if not self.wait_for_timer():
            print("Timer did not reach zero. Skipping bid attempt.")
            return

        try:
            bid_input = self.driver.find_element(By.ID, "id_bid4")
            bid_button = self.driver.find_element(By.ID, "apply_order")

            if not bid_input or not bid_button:
                print("Bid input or button not found. Retrying...")
                if retry_count < MAX_RETRIES:
                    time.sleep(2)
                    self.place_bid(retry_count + 1)
                return

            bid_input.clear()
            bid_input.send_keys(str(INITIAL_BID_AMOUNT))
            time.sleep(1)
            bid_button.click()
            time.sleep(2)

            # Check if error appears
            try:
                error_msg = self.driver.find_element(By.ID, "id_bid4-error").text
                if "Minimal bid amount" in error_msg:
                    min_bid = self.extract_min_bid(error_msg)
                    bid_input.clear()
                    bid_input.send_keys(str(min_bid))
                    time.sleep(1)
                    bid_button.click()
                    time.sleep(2)
                    print("Bid placed successfully!")
                else:
                    print("Bid placed successfully!")
            except:
                print("No error message found. Assuming bid placed successfully!")

        except Exception as e:
            print("Bid placement failed:", e)
            if retry_count < MAX_RETRIES:
                time.sleep(2)
                self.place_bid(retry_count + 1)
            else:
                print("Max retries reached. Skipping...")

    def wait_for_timer(self, max_wait=60):
        """Waits for the timer to reach zero before proceeding."""
        print("Waiting for the countdown timer...")
        for _ in range(max_wait):
            try:
                timer_element = self.driver.find_element(By.ID, "id_read_timeout_msg_container")
                time_text = timer_element.text.strip()
                time_left = self.parse_timer_value(time_text)

                if time_left == 0:
                    print("Timer reached zero. Proceeding to bid.")
                    return True
                else:
                    print(f"Time left: {time_left} seconds. Waiting...")
                    time.sleep(1)
            except Exception:
                print("Timer not found. Proceeding with bid.")
                return True
        print("Max wait time exceeded. Skipping bid attempt.")
        return False

    def parse_timer_value(self, time_text):
        """Parses the countdown timer from text."""
        if not time_text:
            return -1

        # Check for "X sec" format
        sec_match = re.search(r"(\d+)\s*sec", time_text)
        if sec_match:
            return int(sec_match.group(1))

        # Check for "HH:MM:SS" format
        time_match = re.search(r"(\d{2}):(\d{2}):(\d{2})", time_text)
        if time_match:
            hours, minutes, seconds = map(int, time_match.groups())
            return hours * 3600 + minutes * 60 + seconds

        return -1

    def extract_min_bid(self, error_text):
        match = re.search(r"Minimal bid amount is \$(\d+\.?\d*)", error_text)
        return float(match.group(1)) if match else INITIAL_BID_AMOUNT