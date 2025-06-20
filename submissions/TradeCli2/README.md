# 🤙 TerminalCraft: TradeCLI

<p align="center">
   <a href="https://github.com/MaheshDhingra/TradeCLI/stargazers">
      <img src="https://img.shields.io/github/stars/MaheshDhingra/TradeCLI?style=social" alt="GitHub Stars">
   </a>
   <a href="https://github.com/MaheshDhingra/TradeCLI/releases">
      <img src="https://img.shields.io/github/v/release/MaheshDhingra/TradeCLI" alt="Latest Release">
   </a>
   <a href="LICENSE">
      <img src="https://img.shields.io/github/license/MaheshDhingra/TradeCLI" alt="License">
   </a>
   <a href="https://www.python.org/">
      <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
   </a>
</p>

---

Welcome to **TradeCLI**, your command-line trading companion. TradeCLI makes managing trades **simple, fast**, and even a little fun—all with real, live market data from Alpha Vantage.

---

**Now powered by Alpha Vantage!**
- All prices, charts, and market data are fetched live from Alpha Vantage using a built-in API key.
- No API key setup needed for price/market data. Only required for real buy/sell trading.

---

## 🎯 Features

* 🧠 **Beginner-Friendly** – Intuitive commands you’ll remember in seconds.
* ⚡ **Fast & Lightweight** – No bloat, just the tools you need.
* 💬 **Cheerful UX** – Friendly prompts and positive feedback.
* 📈 **Visuals** – Generate simple charts for quick price insights.
* 📁 **Portfolio Overview** – Track your positions and performance.
* ⭐ **Favourites** – Mark tickers you love for quick access.
* 🔍 **Market Screener** – Find opportunities at a glance.
* 🚀 **Live Market Data** – All prices and charts are real, not simulated.
* 🏆 **Gainers/Losers** – See top movers in your session.
* 🕒 **Last Trade Time** – Track how fresh your data is.
* 🛡️ **Robust Error Handling** – All commands check for valid ticker data, preventing crashes.
* 🐞 **Bug-Free Analytics** – Analytics, gainers, and screener commands are now fully reliable.
* 🤖 **Hack Club AI Integration** – Ask questions or get help from AI right in your terminal.

---

## 🛠️ Commands Overview

| Command               | Description                                 |
| --------------------- | ------------------------------------------- |
| `help`                | Show all available commands                 |
| `quote <ticker>`      | Fetch current market quote                  |
| `buy <ticker> <qty>`  | Buy shares of a ticker                      |
| `sell <ticker> <qty>` | Sell shares of a ticker                     |
| `positions`           | View current holdings and P&L               |
| `chart <ticker>`      | Show price history chart                    |
| `dashboard`           | View overall portfolio performance          |
| `analytics`           | Show advanced analytics                     |
| `alert`               | Set price/volume alerts                     |
| `integrations`        | Integrations menu                           |
| `exportcsv`           | Export portfolio to CSV                     |
| `customize`           | Customize dashboard                         |
| `popular`             | Display popular trading pairs with price & holding |
| `gainers`             | Show top gainers and losers (session)       |
| `lasttrade`           | Show last trade time for tickers            |
| `favourite <ticker>`  | Add ticker to favourites                    |
| `removefav`           | Remove ticker from favourites               |
| `favourites`          | List all favourite tickers                  |
| `screener`            | Run the market screener                     |
| `ai <prompt>`          | Ask Hack Club AI any question                |
| `clear` / `cls`       | Clear the terminal screen                   |
| `exit`                | Exit TradeCLI                               |

---

## 🚀 Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/MaheshDhingra/TradeCLI.git
   cd TradeCLI
   ```

2. **(Optional) Set up a virtual environment**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # or
   source .venv/bin/activate  # On Mac/Linux
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**

   ```bash
   python main.py
   ```

---

## 📦 Requirements

* Python 3.8 or higher
* Internet connection (for live data fetching)
* Terminal/Command Line access

---

## 🔒 License

This project is licensed under the [MIT License](LICENSE).
You're free to use, modify, and distribute it.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to improve.

---

## 🦡 Thanks for Using TradeCLI!

We hope this little tool makes your trading journey a bit brighter.
Happy trading — and may your positions always be green! 📈✨

---

### ✅ To Do in Future Releases:

* More analytics, alerts, and integrations
* Advanced charting
* Customizable dashboards
* ...and more!
