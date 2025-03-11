import requests

class CurrencyConverter:
    def __init__(self):
        self.rates = {}
        self.update_rates()

    def update_rates(self):
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
            self.rates = response.json()["rates"]
        except Exception as e:
            print(f"Error fetching rates: {e}")
            self.rates = {"USD": 1.0, "INR": 83.0}  # Fallback rates

    def convert(self, amount, from_currency, to_currency):
        if from_currency == to_currency:
            return amount
        if from_currency not in self.rates or to_currency not in self.rates:
            return amount  # Fallback to no conversion
        amount_in_usd = amount / self.rates[from_currency]
        return amount_in_usd * self.rates[to_currency]