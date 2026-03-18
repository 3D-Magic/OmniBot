
import yfinance as yf
class HybridDataClient:
    def get_bars(self, symbol, limit=100, timeframe='5m'):
        try:
            df = yf.Ticker(symbol).history(period="3d", interval="5m")
            if df.empty: return None
            return df.rename(columns={'Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume'})
        except: return None
data_client = HybridDataClient()
