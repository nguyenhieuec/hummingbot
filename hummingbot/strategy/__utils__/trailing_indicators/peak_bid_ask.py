from decimal import Decimal
from typing import Tuple

import numpy as np

from .base_trailing_indicator import BaseTrailingIndicator


class PeakBidAsk(BaseTrailingIndicator):
    def __init__(self, sampling_length: int = 200, processing_length: int = 30):
        self.peak_ask = 0.0
        self.peak_bid = 0.0
        self.peak_mid = 0.0
        self.peak_spread = 0.0
        super().__init__(sampling_length, processing_length)

    def _indicator_calculation(self):
        prices = self._sampling_buffer.get_as_numpy_array()
        if prices.size > 0:
            peak_ask_in_buffer = np.nanmax(prices)
            peak_bid_in_buffer = np.nanmin(prices)
            self.peak_ask = peak_ask_in_buffer if (self.peak_ask < peak_ask_in_buffer) else self.peak_ask
            self.peak_bid = peak_bid_in_buffer if (peak_bid_in_buffer < self.peak_bid) else self.peak_bid
            self.peak_mid = (peak_ask_in_buffer - peak_bid_in_buffer) / 2
            self.peak_spread = (peak_ask_in_buffer - peak_bid_in_buffer) / peak_ask_in_buffer

        if self.peak_spread != 0.0 and self.peak_spread < 0.2:
            return self.peak_spread

    def current_peak_value(self) -> Tuple[float, float, float, float]:
        return self.peak_bid, self.peak_ask, self.peak_mid, self.peak_spread

    def position_exit_price_level(self):
        last_peak_spread = Decimal(self.current_value)

        if last_peak_spread != 0:
            bid_price = Decimal(self.peak_mid) * (Decimal("1") - last_peak_spread)
            ask_price = Decimal(self.peak_mid) * (Decimal("1") + last_peak_spread)

        else:
            return self.peak_bid, self.peak_ask

        return bid_price, ask_price

    def next_round(self):
        """
        reset peak_bid, peak_ask, peak_mid after a trading round.
        """
        self.peak_ask = 0.0
        self.peak_bid = 0.0
        self.peak_mid = 0.0
