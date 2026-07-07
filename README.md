Convertible Bond Dual-Low & Momentum Backtesting Engine 📈

📖 Project Overview

This project implements an enterprise-level quantitative backtesting framework targeting the China A-Share Convertible Bond (CB) Market. It is designed to strictly evaluate the performance of a "Dual-Low" (Price + Premium Rate) rotational strategy, augmented by a Cross-Sectional Momentum Filter (20-Day MA) to control maximum drawdowns and avoid value traps.

The repository is modularized into two core components: a high-concurrency data acquisition module (data_loader.py) and an event-driven backtesting engine (backtest_engine.py).

🧠 Core Strategy Logic

The "Dual-Low" Factor (Value & Elasticity): * Identifies convertible bonds with low absolute prices (providing a solid bond-floor defense) and low conversion premium rates (providing high equity-upside elasticity).

The "Momentum Shield" (Risk Management):

Employs a 20-Day Moving Average (MA20) filter. Any bond falling below its MA20 is ruthlessly eliminated from the candidate pool, effectively avoiding falling knives during systemic liquidity crises.

Dynamic Rotation:

Rebalances the portfolio periodically (e.g., every 20 trading days) to capture the top 5 ranking CBs, ensuring capital efficiency and continuous exposure to the most optimal risk-reward profiles.

🏗️ System Architecture & File Structure

This framework separates data engineering from financial logic to ensure scalability and performance (Quant Developer mindset).

1. data_loader.py: Asynchronous Data Lake Construction

Data fetching in quantitative research is often the biggest bottleneck. This module handles data engineering with high efficiency:

Multi-Threading Concurrency: Utilizes concurrent.futures.ThreadPoolExecutor to fetch historical daily bars for 500+ active convertible bonds simultaneously via akshare. This reduces data preparation time by over 90%.

Data Cleaning & Caching: Automatically formats date indices, extracts essential OHLCV data, and caches them locally as CSV files in a data/ directory. This creates a local "Data Lake" to speed up subsequent backtest iterations.

Fault Tolerance: Implements strict try...except blocks to handle network timeouts and seamlessly ignore newly listed bonds with insufficient historical data.

2. backtest_engine.py: Event-Driven Strategy Engine

The core execution environment built on top of the Backtrader framework:

Automated Data Injection: Iterates through the local Data Lake, loads time-series data using Pandas, and aligns data lengths (e.g., trimming to the last 500 trading days) before feeding it into the Cerebro engine.

Custom Strategy Class: Implements the DoubleLowMomentumRotation strategy. It calculates the MA20 indicators, ranks the cross-sectional data, and executes portfolio rebalancing every $N$ days.

Real-World Friction Simulation: Configures initial capital, strict commission rates (e.g., 0.02%), and handles realistic order executions to prevent overfitting and "liquidity illusions".

🚀 Quick Start

Prerequisites

# Clone the repository
git clone [https://github.com/YourUsername/CB-DualLow-Momentum-Strategy.git](https://github.com/YourUsername/CB-DualLow-Momentum-Strategy.git)
cd CB-DualLow-Momentum-Strategy

# Install dependencies
pip install pandas akshare backtrader tqdm


Execution

Step 1: Build the Data Lake
Run the data loader to fetch the latest market data and build your local CSV cache.

python data_loader.py

Step 2: Run the Backtest
Once the data is cached, execute the engine to simulate the strategy performance.

python backtest_engine.py


📝 Disclaimer

This project is for academic research and technical demonstration purposes only. It does not constitute any investment advice. The Chinese Convertible Bond market carries inherent risks, including but not limited to default risks and systemic liquidity drains.
