from src.core import Antrade
import time


class BotTest(Antrade):

    def main(self, open_position=False):
        while True:
            if not open_position:
                self.place_order('BUY')
                open_position = True
            if open_position:
                self.place_order('SELL')
                open_position = False

            time.sleep(2)
            