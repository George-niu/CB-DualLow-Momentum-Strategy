import pandas as pd
import akshare as ak

class DataLoader:
    def __init__(self, data_source='akshare'):
        """
        数据加载器：设计为可插拔架构，方便后期无缝切换到 Wind API
        """
        self.data_source = data_source

    def get_cbond_snapshot(self):
        """
        获取全市场可转债最新横截面数据，并计算“双低”指标
        双低得分 = 转债价格 + 转股溢价率 * 100
        """
        if self.data_source == 'akshare':
            print("正在通过 AkShare 拉取全市场可转债实时/最新数据，请稍候...")
            try:
                # 调用集思录可转债数据接口
                df = ak.bond_cb_jsl(cookie=None)
                
                # 【修改点1：替换为截图里真实的列名】
                cols_to_keep = ['代码', '转债名称', '现价', '转股溢价率']
                
                available_cols = [col for col in cols_to_keep if col in df.columns]
                df = df[available_cols].copy()
                
                # 【修改点2：对齐列名进行数据转换】
                df['现价'] = pd.to_numeric(df['现价'], errors='coerce')
                df['转股溢价率'] = pd.to_numeric(df['转股溢价率'], errors='coerce')
                
                # 清除空值
                df = df.dropna(subset=['现价', '转股溢价率'])
                
                # 【核心业务逻辑】：计算双低得分
                df['双低得分'] = df['现价'] + df['转股溢价率']
                
                # 按照双低得分从小到大排序
                df = df.sort_values(by='双低得分', ascending=True).reset_index(drop=True)
                
                return df
                
            except Exception as e:
                print(f"数据拉取失败，请检查网络或 AkShare 接口状态。错误信息: {e}")
                return None
                
        elif self.data_source == 'wind':
            print("【预留接口】入职后将此处替换为 Wind API (w.wsq 或 w.wsd) 的调用代码。")
            return pd.DataFrame()
        else:
            raise ValueError("不支持的数据源类型！")


# 单元测试模块：只有直接运行当前脚本时才会执行
if __name__ == "__main__":
    # 实例化我们的数据加载器
    loader = DataLoader(data_source='akshare')
    
    # 获取数据
    cbond_df = loader.get_cbond_snapshot()
    
    if cbond_df is not None:
        print("\n拉取成功！当前市场【双低得分】排名前 10 的可转债如下：")
        # 打印前 10 行数据
        print(cbond_df.head(10).to_markdown())