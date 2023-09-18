from datetime import datetime
from functions import debug, log

class Trade:
    def __init__(self, 
                 entry_ts: datetime,
                 entry: float, 
                 entry_leg1: float,
                 entry_leg2: float,
                 open_vol: float, 
                 profit_target: float, 
                 symbol: str,
                 trade_id=None):
        self.entry_ts = entry_ts
        self.entry = entry
        self.entry_leg1 = entry_leg1
        self.entry_leg2 = entry_leg2
        self.open_vol = open_vol
        self.profit_target = profit_target
        self.symbol = symbol
        self.trade_id=trade_id
        self.is_open = True
        self.remaining_vol = open_vol
        self.exit_ts = None
        self.open_pnl = 0
        self.realised_pnl = 0
        self.pnl = 0

    def exit_triggered(self, ts:datetime, price: float, volume: float):
        if self.remaining_vol > 0:
            if price - self.entry >= self.profit_target:
                self.remaining_vol = max(self.remaining_vol - volume, 0)
                if self.remaining_vol == 0:
                    self.is_open = False
                    self.exit_ts = ts
                
                self.realised_pnl += abs((price - self.entry) * (self.open_vol - self.remaining_vol))
                log(f"Closed trade #{self.trade_id} at {price} on {ts}, remaining: x{self.remaining_vol}")
        
            # Calculate how much volume left on screen and return that back
            return max(volume - self.remaining_vol, 0)

        else:
            if self.entry - price >= self.profit_target:
                self.remaining_vol = min(self.remaining_vol + volume, 0)
                if self.remaining_vol == 0:
                    self.is_open = False
                    self.exit = price
                    self.exit_ts = ts
                
                self.realised_pnl += abs((price - self.entry) * (self.remaining_vol - self.open_vol))
                log(f"Closed trade #{self.trade_id} at {price} on {ts}, remaining volume: {self.remaining_vol}")

            return max(volume + self.remaining_vol, 0)
        

    def calculate_mtm(self, settlement: float):
        self.open_pnl = (settlement - self.entry) * self.remaining_vol
        self.pnl = self.open_pnl + self.realised_pnl


class TradeBook:
    def __init__(self):
        self.trades = []
        self.reports = []
    
    def add_trade(self, 
                  entry_ts: datetime, 
                  entry: float,
                  entry_leg1: float,
                  entry_leg2: float,
                  open_vol: float,
                  exit_target: float, 
                  symbol: str):
        if open_vol == 0:
            return
        self.trades.append(Trade(entry_ts, entry, entry_leg1, entry_leg2, open_vol, exit_target, symbol, trade_id=len(self.trades)+1))

    def get_all_open_trades(self):
        return [trade for trade in self.trades if trade.is_open]

    def check_exit_trigger(self, ts:datetime, bid: float, offer: float, bv: float, av: float):
        open_trades = self.get_all_open_trades()
        remaining_screen_bv = bv
        remaining_screen_av = av
        for trade in open_trades:
             # If you are long, you close by looking at bids
             if trade.remaining_vol > 0:
                 remaining_screen_bv = trade.exit_triggered(ts=ts, price=bid, volume=remaining_screen_bv)
                 
                 # Nothing left on screen to fill
                 if remaining_screen_bv == 0:
                     return remaining_screen_bv, remaining_screen_av
    
             else:
                 remaining_screen_av = trade.exit_triggered(ts=ts, price=offer, volume=remaining_screen_av)
                 # Nothing left on screen to fill
                 if remaining_screen_av == 0:
                     return remaining_screen_bv, remaining_screen_av
        
        return remaining_screen_bv, remaining_screen_av

    def mtm(self, settlement: float):
        for trade in self.trades:
            trade.calculate_mtm(settlement)
    
    def eod(self, ts: datetime, settlement: float):
        """Function to run every eod to ensure updated state"""
        self.mtm(settlement)
        eod_report = {"timestamp": ts, "P&L": sum([trade.pnl for trade in self.trades])}
        self.reports.append(eod_report)