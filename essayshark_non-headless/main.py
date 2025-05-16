import time
from essayshark.driver_setup import setup_driver
from essayshark.authenticator import Authenticator
from essayshark.bid_handler import BidHandler
from essayshark.file_downloader import FileDownloader
from essayshark.navigation_helper import NavigationHelper
from essayshark.config import ESSAYSHARK_URL

class EssaySharkBot:
    def __init__(self):
        self.driver = setup_driver()
        self.authenticator = Authenticator(self.driver)
        self.bid_handler = BidHandler(self.driver)
        self.file_downloader = FileDownloader(self.driver)
        self.navigation = NavigationHelper(self.driver)

    def run(self):
        self.authenticator.login()
        while True:  # Keep the bot running to process multiple orders
            self.driver.get(ESSAYSHARK_URL)
            time.sleep(3)  # Allow page to load

            if self.is_order_page():
                print("On an order page. Handling order...")
                self.file_downloader.download_file()
                self.bid_handler.place_bid()
            else:
                print("Not on an order details page. Navigating...")
                self.navigation.navigate_to_orders()

            time.sleep(10)  # Wait before checking for new orders

    def is_order_page(self):
        return "/writer/orders/" in self.driver.current_url

if __name__ == "__main__":
    bot = EssaySharkBot()
    bot.run()
