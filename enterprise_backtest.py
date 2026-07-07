import os
import backtrader as bt
import pandas as pd
import akshare as ak
import datetime
import concurrent.futures
from tqdm import tqdm

# ==========================================
# 1. 定义策略类 (保持双低+动量逻辑不变)
# ==========================================
class DoubleLowMomentumRotation(bt.Strategy):
    params = (
        ('sel_num', 5),          
        ('rebalance_days', 20),   
        ('ma_period', 20),        
    )

    def __init__(self):
        print(f"初始化策略：【全市场双低选美】 + 【{self.params.ma_period}日动量过滤】...")
        self.days_passed = 0 
        self.bonds_data = {} 
        
        for d in self.datas:
            self.bonds_data[d] = dict()
            self.bonds_data[d]['score'] = d.close 
            self.bonds_data[d]['ma20'] = bt.indicators.SimpleMovingAverage(
                d.close, period=self.params.ma_period
            )

    def next(self):
        current_date = self.datas[0].datetime.date(0)
        self.days_passed += 1

        if self.days_passed % self.params.rebalance_days != 0:
            return

        current_scores = []
        for d in self.datas:
            if len(d) > 0: 
                current_price = d.close[0]
                current_ma20 = self.bonds_data[d]['ma20'][0]
                score = self.bonds_data[d]['score'][0]
                
                # 动量过滤：必须在 20 日均线之上
                if current_price > current_ma20:
                    current_scores.append((d, score))
                
        # 按照得分从小到大排序
        current_scores.sort(key=lambda x: x[1])
        
        # 选出 Top 5
        target_bonds = [x[0] for x in current_scores[:self.params.sel_num]]
        
        if len(target_bonds) > 0:
            print(f"[{current_date}] 调仓换股! 入选标的数: {len(target_bonds)}")

            
        # 轮动交易：目标仓位管理
        for d in self.datas:
            if d in target_bonds:
                target_weight = 0.95 / len(target_bonds) # 满仓 95%，均分给选中的标的
                self.order_target_percent(d, target=target_weight)
            else:
                if self.getposition(d).size > 0:
                    self.order_target_percent(d, target=0.0)

# ==========================================
# 2. 并发下载与本地缓存
# ==========================================
DATA_DIR = "./data"

def get_all_active_cbonds():
    """获取当前所有存续可转债的代码，并自动匹配 sh/sz 前缀"""
    print("正在拉取全市场可转债名录...")
    df = ak.bond_cb_jsl(cookie=None)
    codes = df['代码'].tolist()
    
    # 智能匹配前缀：沪市通常以 11 开头，深市以 12 开头
    full_symbols = []
    for code in codes:
        if code.startswith('11'):
            full_symbols.append('sh' + code)
        elif code.startswith('12'):
            full_symbols.append('sz' + code)
    return full_symbols

def download_and_cache_bond(symbol):
    """单只转债的下载与本地缓存逻辑"""
    file_path = os.path.join(DATA_DIR, f"{symbol}.csv")
    
    # 如果本地已经有缓存，直接跳过
    if os.path.exists(file_path):
        return symbol, True

    try:
        df = ak.bond_zh_hs_cov_daily(symbol=symbol)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        # 清洗并保存到本地
        df = df[['open', 'high', 'low', 'close', 'volume']]
        df.to_csv(file_path)
        return symbol, True
    except Exception:
        # 部分转债可能刚刚上市，或者接口无数据，直接忽略
        return symbol, False

def prepare_data_lake():
    """使用多线程并发构建数据湖"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    symbols = get_all_active_cbonds()
    print(f"共发现 {len(symbols)} 只可转债，开始多线程同步数据...")
    
    valid_symbols = []
    # 开 10 个工作线程并发下载
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # 使用 tqdm 显示进度条
        futures = {executor.submit(download_and_cache_bond, sym): sym for sym in symbols}
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(symbols), desc="数据下载/检查进度"):
            sym, success = future.result()
            if success:
                valid_symbols.append(sym)
                
    return valid_symbols

# ==========================================
# 3. 引擎主控室
# ==========================================
def run_backtest():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(DoubleLowMomentumRotation)

    # 1. 准备数据湖 (第一次会花几分钟下载，第二次以后只需几秒)
    valid_symbols = prepare_data_lake()
    
    # 2. 将本地 CSV 批量注入 Backtrader
    print(f"\n正在将 {len(valid_symbols)} 只转债的历史数据加载进回测引擎内存...")
    for sym in tqdm(valid_symbols, desc="内存加载进度"):
        file_path = os.path.join(DATA_DIR, f"{sym}.csv")
        try:
            df = pd.read_csv(file_path, index_col='date', parse_dates=True)
            # 截取近两年数据进行回测，保证每只转债的数据长度一致
            df = df.tail(500) 
            if len(df) > 50: # 剔除上市时间太短的新债
                data = bt.feeds.PandasData(dataname=df, name=sym)
                cerebro.adddata(data)
        except:
            continue

    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.0002)

    print(f"\n=====================================")
    print(f"【全市场500只轮动】回测正式启动！初始资金: {cerebro.broker.getvalue():.2f}")
    print(f"=====================================")
    
    # 启动大脑！全市场的运算可能需要几十秒，耐心等待
    cerebro.run()
    
    print(f"=====================================")
    print(f"回测结束！最终资金: {cerebro.broker.getvalue():.2f}")
    print(f"=====================================")

if __name__ == '__main__':
    run_backtest()