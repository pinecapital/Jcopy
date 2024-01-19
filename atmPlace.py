from ib_insync import * 
from datetime import datetime

def orderATM(strike_price, option_type, quantity):
    # Create an instance of IB class
    ib = IB()

    # Connect to the Interactive Brokers server
    ib.connect('127.0.0.1', 7497, clientId=1)

    # Get today's date and format it to match the required format
    today_full = datetime.today().strftime('%Y%m%d')
    today_short = datetime.today().strftime('%y%m%d')

    # Define the option contract
    option = Option('SPX', today_full, strike_price, option_type.upper(), 'SMART', localSymbol=f'SPXW  {today_short}{option_type[0].upper()}{strike_price:05}000', multiplier=100)

    # Use qualifyContracts to fill in additional contract details from the Interactive Brokers server
    ib.qualifyContracts(option)

    # Here we use a market order as an example, you may want to use a limit order or other types of order depending on your needs
    order = MarketOrder('BUY', quantity)

    # Place the order
    trade = ib.placeOrder(option, order)

    print(trade)
        # Disconnect from the server
    ib.disconnect()
    # Return the contract
    return option


def closePosition(contract, quantity):
    # Create an instance of IB class
    ib = IB()

    # Connect to the Interactive Brokers server
    ib.connect('127.0.0.1', 7497, clientId=1)

    # Use qualifyContracts to fill in additional contract details from the Interactive Brokers server
    ib.qualifyContracts(contract)

    # Here we use a market order as an example, you may want to use a limit order or other types of order depending on your needs
    order = MarketOrder('SELL', quantity)

    # Place the order
    trade = ib.placeOrder(contract, order)

    print(trade)
    # Disconnect from the server
    ib.disconnect()


contract = orderATM(4750, "call", 2)

closePosition(contract, 2)