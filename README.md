Convertible Bond Dual-Low & Momentum Rotational Strategy 📈

📖 Project Overview

This project implements a systematic quantitative trading framework targeting the China A-Share Convertible Bond (CB) Market. It combines a rigorous historical backtesting engine with a real-time daily signal generation radar ("Semi-Auto Trading").

The core strategy is built upon the classic "Dual-Low" (Price + Premium Rate) factor, augmented by a Cross-Sectional Momentum Filter (20-Day MA) to strictly control maximum drawdowns and avoid value traps (e.g., defaulted or persistently declining bonds).

🧠 Core Strategy Logic

The "Dual-Low" Factor (Value & Elasticity): * Identifies convertible bonds with low absolute prices (providing a solid bond-floor defense) and low conversion premium rates (providing high equity-upside elasticity).

The "Momentum Shield" (Risk Management):

Employs a 20-Day Moving Average (MA20) filter. Any bond falling below its MA20 is ruthlessly eliminated from the candidate pool, effectively avoiding falling knives during systemic liquidity crises.

Dynamic Rotation:

Rebalances the portfolio periodically (e.g., every 20 trading days) to capture the top 5 ranking CBs, ensuring capital efficiency and continuous exposure to the most optimal risk-reward profiles.

🛠️ Engineering Highlights & Tech Stack

Beyond the financial logic, this project is engineered with performance and robustness in mind (Quant Developer mindset):

Event-Driven Backtesting: Built on the Backtrader framework, fully simulating real-world transaction friction (commissions, slippage, and capital limits).

High-Performance Data Lake: Engineered an automated local data caching system.

Multi-Threading Concurrency: Utilized concurrent.futures.ThreadPoolExecutor to fetch and process historical daily bars for 500+ active convertible bonds simultaneously, reducing data preparation time by over 90%.

Live Daily Radar (Webhook Integration): Includes a standalone lightweight script (daily_radar.py) for live market deployment. It calculates real-time Dual-Low scores post-market and automatically pushes the target trading list via DingTalk/WeChat Webhooks.

🚀 Quick Start

1. Run the Historical Backtest

# Clone the repository
git clone [https://github.com/YourUsername/CB-DualLow-Momentum-Strategy.git](https://github.com/YourUsername/CB-DualLow-Momentum-Strategy.git)
cd CB-DualLow-Momentum-Strategy

# Install dependencies
pip install -r requirements.txt

# Execute the backtest engine (automatically downloads data if first run)
python backtest_engine.py


2. Run the Daily Live Radar (After Market Closes)

python daily_radar.py

Note: Make sure to configure your own Webhook URL in daily_radar.py to receive mobile notifications.



📝 Disclaimer

This project is for academic research and technical demonstration purposes only. It does not constitute any investment advice. The Chinese Convertible Bond market carries inherent risks, including but not limited to default risks and systemic liquidity drains.
