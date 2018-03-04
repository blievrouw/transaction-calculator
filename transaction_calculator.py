from forex_python.converter import CurrencyRates
import argparse


def euro_to_dollar(euro):
    c = CurrencyRates()
    return round(float(euro) * c.get_rates('EUR')['USD'], 2)


def dollar_to_euro(dollar):
    c = CurrencyRates()
    return round(float(dollar) * c.get_rates('USD')['EUR'], 2)


# Broker fees (per exchange / exchange country, per broker)
BROKER_FEES_PER_TRANSACTION = {
    'degiro': {
        'US': {
            'fixed_fee_per_transaction': euro_to_dollar(0.50),
            'fixed_fee_per_share': 0.004,
            'fractional_fee_percentage': 0.1  # Valuta FX trader
        }

    }
}

# Taxation (per country)
TAXES_PER_TRANSACTION = {
    'BE': {
        'fractional_fee_percentage': 0.27
    }
}


def calculate_profit_before_taxes_and_broker_fees(buy_pps_dollar, sell_pps_dollar, nshares):
    """
    Calculates profit before taxes and broker fees based on buy/sell price and amount of shares
    """
    profit_before_taxes_and_broker_fees = (float(sell_pps_dollar) - float(buy_pps_dollar)) * int(nshares)
    return round(profit_before_taxes_and_broker_fees, 2)


def calculate_taxes(buy_pps_dollar, sell_pps_dollar, nshares, country):
    """
    Calculates taxes on 2 transactions (buying and selling of a certain amount shares)
    """
    fractional_fee_percentage = TAXES_PER_TRANSACTION[country]['fractional_fee_percentage']
    taxes = (float(buy_pps_dollar) + float(sell_pps_dollar)) * int(nshares) * (fractional_fee_percentage / 100)
    return round(taxes, 2)


def calculate_broker_fees(buy_pps_dollar, sell_pps_dollar, nshares, broker, exchange):
    """
    Calculates broker fees on 2 transactions (buying and selling of a certain amount of shares)
    """
    fixed_fee_per_transaction = BROKER_FEES_PER_TRANSACTION[broker][exchange]['fixed_fee_per_transaction']
    fixed_fee_per_share = BROKER_FEES_PER_TRANSACTION[broker][exchange]['fixed_fee_per_share']
    fractional_fee_percentage = BROKER_FEES_PER_TRANSACTION[broker][exchange]['fractional_fee_percentage']

    broker_fee = (2 * fixed_fee_per_transaction) + (2 * nshares * fixed_fee_per_share) + ((buy_pps_dollar + sell_pps_dollar) * nshares * (fractional_fee_percentage / 100))
    return round(broker_fee, 2)


def calculate_profit(profit_before_taxes_and_broker_fees, taxes, broker_fees):
    return round(profit_before_taxes_and_broker_fees - (taxes + broker_fees), 2)


def calculate_profit_margin_pct(profit, buy_pps_dollar, nshares):
    return round((profit / (buy_pps_dollar * nshares)) * 100, 2)



# User input
parser = argparse.ArgumentParser(description='Calculates taxes, fees and profits from buying and selling a certain amount of shares')
parser.add_argument('nshares', type=int, default=1, help='Number of shares')
parser.add_argument('buy', type=float, help='Buy price per share ($)')
parser.add_argument('sell', type=float, help='Sell price per share ($)')
parser.add_argument('--exchange', type=str, default='US', help='Exchange (or country of exchange)')
parser.add_argument('--tax_country', type=str, default='BE', choices=TAXES_PER_TRANSACTION.keys(), help='Country of taxation')
parser.add_argument('--broker', type=str, default='degiro', choices=BROKER_FEES_PER_TRANSACTION.keys(), help='Broker')
arguments = parser.parse_args()


# Results
profit_before_taxes_and_broker_fees = calculate_profit_before_taxes_and_broker_fees(buy_pps_dollar=arguments.buy,
                                                                                    sell_pps_dollar=arguments.sell,
                                                                                    nshares=arguments.nshares)
taxes = calculate_taxes(buy_pps_dollar=arguments.buy,
                        sell_pps_dollar=arguments.sell,
                        nshares=arguments.nshares,
                        country=arguments.tax_country)
broker_fees = calculate_broker_fees(buy_pps_dollar=arguments.buy,
                                    sell_pps_dollar=arguments.sell,
                                    nshares=arguments.nshares,
                                    broker=arguments.broker,
                                    exchange=arguments.exchange)
profit = calculate_profit(profit_before_taxes_and_broker_fees, taxes, broker_fees) 
profit_margin_percentage = calculate_profit_margin_pct(profit, arguments.buy, arguments.nshares)

# Report
print(50 * "-")
print("Broker: {}".format(arguments.broker))
print("Exchange (country): {}".format(arguments.exchange))
print("Taxation country: {}\n".format(arguments.tax_country))

print("Amount of shares: {}".format(arguments.nshares))
print("Buy at ${},\nSell at ${}\n".format(arguments.buy, arguments.sell))

print("Taxes: ${} (€{})".format(taxes, dollar_to_euro(taxes)))
print("Broker fees: ${} (€{})".format(broker_fees, dollar_to_euro(broker_fees)))
print(50 * "-")
print("Profit:\n${} (€{})".format(profit, dollar_to_euro(profit)))
print("Profit margin: {}%".format(profit_margin_percentage))
print(50 * "-")
