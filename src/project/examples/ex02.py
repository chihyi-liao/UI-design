import sys
import tkinter as tk
from dataclasses import dataclass

import pandas as pd

try:
    import matplotlib
    import mplfinance as mpf

    matplotlib.use("QtAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.text import Text
except ImportError:
    raise

from .style import Gold, Green, Red, White, default_style


@dataclass
class TextUIComponent:
    title: Text
    date_name: Text
    date_value: Text
    open_name: Text
    open_value: Text
    high_name: Text
    high_value: Text
    low_name: Text
    low_value: Text
    close_name: Text
    close_value: Text
    change_name: Text
    change_value: Text
    volume_name: Text
    volume_value: Text
    strategy_name: Text

    @classmethod
    def create_with_canvas(cls, canvas: Figure):
        return cls(
            title=canvas.text(0.12, 0.95, "", color=Gold),
            date_name=canvas.text(0.12, 0.92, "日期:"),
            date_value=canvas.text(0.15, 0.92, "", animated=True),
            open_name=canvas.text(0.22, 0.95, "開盤價:"),
            open_value=canvas.text(0.27, 0.95, "", animated=True),
            close_name=canvas.text(0.22, 0.92, "收盤價:"),
            close_value=canvas.text(0.27, 0.92, "", animated=True),
            high_name=canvas.text(0.33, 0.95, "最高價:"),
            high_value=canvas.text(0.38, 0.95, "", animated=True),
            low_name=canvas.text(0.33, 0.92, "最低價:"),
            low_value=canvas.text(0.38, 0.92, "", animated=True),
            change_name=canvas.text(0.43, 0.92, "漲跌:"),
            change_value=canvas.text(0.48, 0.92, "", animated=True),
            volume_name=canvas.text(0.43, 0.95, "成交量:"),
            volume_value=canvas.text(0.48, 0.95, "", animated=True),
            strategy_name=canvas.text(0.92, 0.92, ""),
        )


class Canvas(FigureCanvas):
    def __init__(self, fig):
        super().__init__(fig)
        self.fig = fig
        self.axes = []

    def add_axes(self, *args, **kwargs):
        self.axes.append(self.fig.add_axes(*args, **kwargs))


class CandlestickWidget(tk.Frame):
    def __init__(
        self,
        parent=None,
        title: str = "",
        data: pd.DataFrame | None = None,
    ):
        super().__init__(parent)
        self.data = data
        self.title = title

        # 狀態變數
        self.is_pressing = False
        self.press_x = None
        self.press_xmin = None
        self.press_xmax = None
        self.bg_snapshot = None
        self.view_num = 200

        # 如果一開始沒傳資料，先顯示提示文字
        if self.data is None or self.data.empty:
            self.placeholder_label = tk.Label(self, text="暫無資料")
            self.placeholder_label.pack()
            return

        # 初始繪圖
        self.init_stock_settings()
        self.init_plot()

    def init_stock_settings(self):
        """計算資料總數與初始顯示範圍"""
        if self.data is None:
            return

        # 記錄整張大資料表的絕對總筆數
        self.total_count = self.data.shape[0]

        # 預設一開始畫面上顯示最後的 100 根 K 線
        self.current_visible_count = 100
        self.xmin = max(0, self.total_count - self.current_visible_count)
        self.xmax = self.total_count

    def init_plot(self):
        """初始化繪圖"""
        if self.data is None or self.data.empty:
            return

        # 資料切片預設60筆
        initial_df = self.data.iloc[int(self.xmin) : int(self.xmax)]
        self.fig = mpf.figure(style=default_style())
        self.canvas = Canvas(self.fig)
        self.canvas.add_axes([0.08, 0.25, 0.88, 0.65])
        self.canvas.add_axes([0.08, 0.15, 0.88, 0.1], sharex=self.canvas.axes[0])
        self.main_ax = self.canvas.axes[0]
        self.vol_ax = self.canvas.axes[1]
        self.main_ax.set_ylabel("股價")
        self.vol_ax.set_ylabel("成交量")
        mpf.plot(
            initial_df,
            type="candle",
            ax=self.main_ax,
            volume=self.vol_ax,
            datetime_format="%y-%m-%d",
            xrotation=0,
        )
        # 建立垂直線與水平線
        self.v_line = self.main_ax.axvline(color=Gold, linestyle="--", linewidth=0.8, animated=True)
        self.h_line = self.main_ax.axhline(color=Gold, linestyle="--", linewidth=0.8, animated=True)

        self.text_ui = TextUIComponent.create_with_canvas(self.fig)
        self.text_ui.title.set_text(self.title)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 註冊事件
        self.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        self.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.canvas.mpl_connect("draw_event", self.on_draw_finished)

        # 更新視圖
        self.update_view()

    def refresh_text(self, data: pd.DataFrame):
        """更新視圖文字"""

        def set_text_color(curr, prev, text_obj):
            if curr > prev:
                text_obj.set_color(Red)
            elif curr < prev:
                text_obj.set_color(Green)
            else:
                text_obj.set_color(White)

        # 用兩天收盤價判斷漲跌幅
        prev_data, curr_data = data.iloc[0], data.iloc[1]
        change = round((curr_data["Close"] - prev_data["Close"]), 2)
        rate = round((change / prev_data["Close"]) * 100, 2)

        # 更新日期
        date_str = pd.to_datetime(curr_data.name, format="%Y-%m-%d").strftime("%y-%m-%d")
        self.text_ui.date_value.set_text(f"{date_str}")

        # 更新股價
        text_objs = [
            (curr_data["Open"], self.text_ui.open_value),
            (curr_data["High"], self.text_ui.high_value),
            (curr_data["Low"], self.text_ui.low_value),
            (curr_data["Close"], self.text_ui.close_value),
            (change, self.text_ui.change_value),
        ]
        for i, (price, item) in enumerate(text_objs):
            if i == len(text_objs) - 1:
                set_text_color(price, 0, item)
                text = f"{change} ({rate}%)"
                item.set_text(text)
            else:
                set_text_color(price, prev_data["Close"], item)
                item.set_text(price)

        # 更新成交量
        if self.vol_ax:
            self.text_ui.volume_value.set_text(int(curr_data["Volume"]))

    def on_draw_finished(self, event):
        if event is not None and event.canvas != self.canvas:
            return

        # 捕捉主圖區域的像素快照
        if self.canvas is not None:
            self.bg_snapshot = self.canvas.copy_from_bbox(self.fig.bbox)

    def on_motion(self, event):
        """滑鼠移動"""
        if self.data is None or self.canvas is None:
            return

        # 滑鼠正在拖曳
        if self.is_pressing and event.x is not None and self.press_x is not None:
            if self.press_xmax is None or self.press_xmin is None:
                return

            dx_pixels = event.x - self.press_x
            # 取得畫布實際寬度
            canvas_width = self.canvas.get_tk_widget().winfo_width()
            if canvas_width <= 0:
                canvas_width = 600

            # 根據滑鼠移動像素比例，換算成移動的 K 線根數
            visible_range = self.press_xmax - self.press_xmin
            dx_k_lines = (dx_pixels / canvas_width) * visible_range

            # 計算出新的邊界嘗試值
            self.xmin = self.press_xmin - dx_k_lines
            self.xmax = self.press_xmax - dx_k_lines

            # 4. 自動在 update_view 裡做邊界校正與拖曳基準點補償
            self.update_view()
            return

        # 滑鼠游標不在主圖上
        if event.inaxes != self.main_ax or self.bg_snapshot is None:
            if self.v_line.get_visible() or self.h_line.get_visible():
                self.v_line.set_visible(False)
                self.h_line.set_visible(False)
                self.canvas.draw_idle()
            return

        # 滑鼠游標在主圖上
        self.canvas.restore_region(self.bg_snapshot)

        # event.xdata 就是畫面相對索引 (0 ~ 寬度)
        local_idx = int(round(event.xdata))

        # 換算出大資料表的絕對全域索引
        global_idx = int(round(self.xmin)) + local_idx

        if 1 <= global_idx < self.data.shape[0]:
            two_days_df = self.data.iloc[global_idx - 1 : global_idx + 1]
            self.refresh_text(two_days_df)

        # 重新繪製看板文字
        self.fig.draw_artist(self.text_ui.date_value)
        self.fig.draw_artist(self.text_ui.open_value)
        self.fig.draw_artist(self.text_ui.high_value)
        self.fig.draw_artist(self.text_ui.low_value)
        self.fig.draw_artist(self.text_ui.close_value)
        self.fig.draw_artist(self.text_ui.change_value)
        if self.vol_ax:
            self.fig.draw_artist(self.text_ui.volume_value)

        # 十字線位置更新
        if 0 <= global_idx < self.data.shape[0]:
            close_price = self.data.iloc[global_idx]["Close"]
            self.v_line.set_xdata([local_idx, local_idx])  # 垂直線對齊畫面相對位置
            self.h_line.set_ydata([close_price, close_price])  # 水平線對齊絕對股價
        else:
            self.v_line.set_xdata([event.xdata, event.xdata])
            self.h_line.set_ydata([event.ydata, event.ydata])

        self.v_line.set_visible(True)
        self.h_line.set_visible(True)
        self.main_ax.draw_artist(self.v_line)
        self.main_ax.draw_artist(self.h_line)
        self.canvas.blit(self.fig.bbox)

    def on_scroll(self, event):
        """滾輪縮放"""
        if event.inaxes is None:
            return
        cur_width = self.xmax - self.xmin
        scale_factor = 1.2 if event.button == "up" else 0.8 if event.button == "down" else 1.0

        mouse_x = event.xdata
        new_width = cur_width * scale_factor

        # 限制畫面的最大寬度
        max_limit = min(self.view_num, self.total_count)
        if new_width < 30 or new_width > max_limit:
            return

        rel_pos = (mouse_x - self.xmin) / cur_width
        self.xmin = mouse_x - new_width * rel_pos
        self.xmax = mouse_x + new_width * (1 - rel_pos)
        self.update_view()

    def on_press(self, event):
        if event.inaxes == self.main_ax and event.button == 1:
            self.is_pressing = True
            self.press_x = event.x

            # 記錄左右邊界邊緣
            self.press_xmin = self.xmin
            self.press_xmax = self.xmax

            #  隱藏十字線與清空快照
            self.v_line.set_visible(False)
            self.h_line.set_visible(False)
            self.bg_snapshot = None

    def on_release(self, event):
        self.is_pressing = False
        self.press_x = None
        if self.canvas is not None:
            self.canvas.draw()

    def update_view(self):
        """更新視窗"""
        if self.data is None:
            return

        # 計算並限制當前畫面的安全寬度
        current_width = self.xmax - self.xmin
        current_width = max(30, min(current_width, self.view_num))
        current_width = min(current_width, self.total_count)

        # 邊界判斷
        if self.xmin < 0:
            self.xmin = 0
            self.xmax = current_width
            # 超出左邊界立即重新錨定
            if self.is_pressing:
                self.press_xmin = self.xmin
                self.press_xmax = self.xmax
                self.press_x = self.press_x if hasattr(self, "press_x") else None
        elif self.xmax > self.total_count:
            self.xmax = self.total_count
            self.xmin = self.total_count - current_width
            # 超出右邊界立即重新錨定
            if self.is_pressing:
                self.press_xmin = self.xmin
                self.press_xmax = self.xmax

        start_idx = int(round(self.xmin))
        end_idx = int(round(self.xmax))
        if start_idx >= end_idx:
            return

        # 只把畫面上看得到的K線餵給圖表
        visible_data = self.data.iloc[start_idx:end_idx]

        # 十字線從主圖拔掉，防止被 clear() 銷毀
        if hasattr(self, "v_line") and self.v_line in self.main_ax.lines:
            self.v_line.remove()
        if hasattr(self, "h_line") and self.h_line in self.main_ax.lines:
            self.h_line.remove()

        # 清除舊像素
        self.main_ax.clear()
        if self.vol_ax is not None:
            self.vol_ax.clear()

        # 重新繪製
        mpf.plot(
            visible_data,
            type="candle",
            style=default_style(),
            ax=self.main_ax,
            volume=self.vol_ax,
            datetime_format="%y-%m-%d",
            xrotation=0,
            panel_ratios=(5, 1),
        )

        # 重新補上 Y 軸標籤
        self.main_ax.set_ylabel("股價")
        if self.vol_ax is not None:
            self.vol_ax.set_ylabel("成交量")

        # 重繪完成後，立刻把十字線加回主圖中
        if hasattr(self, "v_line"):
            self.main_ax.add_line(self.v_line)
        if hasattr(self, "h_line"):
            self.main_ax.add_line(self.h_line)

        if self.canvas is not None:
            self.canvas.draw_idle()

    def update_data(self, new_data: pd.DataFrame):
        """提供外部更新資料"""
        if new_data is None or new_data.empty:
            return

        self.data = new_data
        # 如果原本有顯示「暫無資料」的文字，將它移除
        if hasattr(self, "placeholder_label") and self.placeholder_label:
            self.placeholder_label.pack_forget()
            self.placeholder_label = None

        # 如果原本就有畫布，先清掉舊的
        if hasattr(self, "canvas") and self.canvas:
            self.canvas.fig.clf()
            self.canvas = None

        # 重新初始化並繪圖
        self.init_stock_settings()
        self.init_plot()

    def change_max_view_limit(self, num: int):
        """提供外部設定觀看數量限制"""
        self.view_num = num
        self.update_view()


def create_test_data(num: int = 300):
    from datetime import datetime

    import numpy as np
    import pandas as pd

    today = datetime.today()
    # 設定隨機種子
    np.random.seed()

    # 自動產生 300 個連續的交易日期 (跳過週六日)
    date_range = pd.date_range(end=today.strftime("%Y-%m-%d"), periods=num, freq="B")

    # 模擬 300 天的股價走勢
    prices = np.zeros(num)
    prices[0] = 1000.0  # 起始股價設定為 100 元
    for i in range(1, num):
        change = np.random.uniform(-0.02, 0.02)  # 每日隨機漲跌 -2% 到 +2%
        prices[i] = prices[i - 1] * (1 + change)

    # 根據每日基本股價，生成隨機的開高低收與成交量
    open_prices = prices * np.random.uniform(0.99, 1.01, num)
    close_prices = prices * np.random.uniform(0.99, 1.01, num)
    high_prices = np.maximum(open_prices, close_prices) * np.random.uniform(1.00, 1.02, num)
    low_prices = np.minimum(open_prices, close_prices) * np.random.uniform(0.98, 1.00, num)
    volumes = np.random.randint(1000, 5000, num)
    df = pd.DataFrame(
        {
            "Date": date_range,
            "Open": np.round(open_prices, 2),
            "High": np.round(high_prices, 2),
            "Low": np.round(low_prices, 2),
            "Close": np.round(close_prices, 2),
            "Volume": volumes,
        }
    )

    # 將 Date 轉為時間索引
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    return df


def main():
    app = tk.Tk()
    app.geometry("1600x1200")
    widget = CandlestickWidget(app, title="2330(台積電)", data=create_test_data(500))
    widget.pack(pady=50)
    app.mainloop()


if __name__ == "__main__":
    sys.exit(main())
