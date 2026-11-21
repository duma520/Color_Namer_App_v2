import tkinter as tk
from tkinter import filedialog, messagebox
import colorsys
import pandas as pd
import numpy as np
from PIL import Image, ImageTk

class ColorNamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RGB颜色命名工具")
        self.setup_ui()
        
    def setup_ui(self):
        # 颜色预览区域
        self.color_canvas = tk.Canvas(self.root, width=200, height=200, bg='white')
        self.color_canvas.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        
        # RGB输入控件
        tk.Label(self.root, text="R:").grid(row=1, column=0, sticky='e')
        self.r_entry = tk.Entry(self.root, width=5)
        self.r_entry.grid(row=1, column=1, sticky='w')
        self.r_entry.insert(0, "255")
        
        tk.Label(self.root, text="G:").grid(row=2, column=0, sticky='e')
        self.g_entry = tk.Entry(self.root, width=5)
        self.g_entry.grid(row=2, column=1, sticky='w')
        self.g_entry.insert(0, "0")
        
        tk.Label(self.root, text="B:").grid(row=3, column=0, sticky='e')
        self.b_entry = tk.Entry(self.root, width=5)
        self.b_entry.grid(row=3, column=1, sticky='w')
        self.b_entry.insert(0, "0")
        
        # 命名按钮
        self.name_btn = tk.Button(self.root, text="获取颜色名称", command=self.show_color_name)
        self.name_btn.grid(row=4, column=0, columnspan=2, pady=5)
        
        # 结果显示
        self.result_label = tk.Label(self.root, text="颜色名称将显示在这里", font=('Microsoft YaHei', 10))
        self.result_label.grid(row=5, column=0, columnspan=3)
        
        # 文件操作区域
        tk.Label(self.root, text="批量处理:").grid(row=6, column=0, sticky='e', pady=(20,0))
        self.import_btn = tk.Button(self.root, text="导入CSV", command=self.import_csv)
        self.import_btn.grid(row=6, column=1, sticky='w', pady=(20,0))
        
        self.export_btn = tk.Button(self.root, text="导出CSV", state='disabled', command=self.export_csv)
        self.export_btn.grid(row=6, column=2, sticky='w', pady=(20,0))
        
        # 数据存储
        self.df = None
    
    def get_hsl_name(self, r, g, b):
        """精细化HSL命名算法"""
        h, s, l = colorsys.rgb_to_hls(r/255, g/255, b/255)
        h_deg = h * 360
        
        # 明度/饱和度判断
        if l < 0.1: return "黑色"
        if l > 0.9 and s < 0.1: return "白色"
        if s < 0.1: return f"{'深灰' if l < 0.4 else '浅灰' if l > 0.6 else '灰色'}"
        
        # 饱和度描述
        saturation_desc = ""
        if s < 0.3: saturation_desc = "淡"
        elif s > 0.8: saturation_desc = "鲜艳"
        
        # 明度描述
        lightness_desc = ""
        if l < 0.3: lightness_desc = "暗"
        elif l > 0.7: lightness_desc = "亮"
        
        # 色相分段 (中文名称)
        hues = [
            (0, "红"), (20, "橙红"), (45, "橙"), 
            (60, "黄橙"), (90, "黄绿"), (120, "绿"),
            (180, "青"), (210, "蓝绿"), (240, "蓝"),
            (270, "紫蓝"), (300, "紫"), (330, "粉红"),
            (360, "红")
        ]
        
        for threshold, name in hues:
            if h_deg <= threshold:
                return f"{saturation_desc}{lightness_desc}{name}"
    
    def update_color_preview(self, r, g, b):
        """更新颜色预览区域"""
        color_img = Image.new('RGB', (200, 200), (r, g, b))
        self.color_img = ImageTk.PhotoImage(color_img)
        self.color_canvas.create_image(0, 0, anchor='nw', image=self.color_img)
    
    def show_color_name(self):
        """处理单个颜色命名"""
        try:
            r = int(self.r_entry.get())
            g = int(self.g_entry.get())
            b = int(self.b_entry.get())
            
            if not (0 <= r <=255 and 0 <= g <=255 and 0 <= b <=255):
                raise ValueError
            
            color_name = self.get_hsl_name(r, g, b)
            self.result_label.config(text=f"颜色名称: {color_name}")
            self.update_color_preview(r, g, b)
            
        except ValueError:
            messagebox.showerror("错误", "请输入0-255之间的整数")
    
    def import_csv(self):
        """导入CSV文件"""
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if not filepath:
            return
            
        try:
            self.df = pd.read_csv(filepath, header=None)
            if len(self.df.columns) < 3:
                messagebox.showerror("错误", "CSV需要至少3列(R,G,B)")
                return
                
            # 添加颜色名称列
            self.df['颜色名称'] = self.df.apply(
                lambda row: self.get_hsl_name(row[0], row[1], row[2]), 
                axis=1
            )
            self.export_btn.config(state='normal')
            messagebox.showinfo("成功", f"已处理 {len(self.df)} 行数据")
            
        except Exception as e:
            messagebox.showerror("错误", f"文件读取失败: {str(e)}")
    
    def export_csv(self):
        """导出结果CSV"""
        if self.df is None:
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if not filepath:
            return
            
        try:
            self.df.to_csv(filepath, index=False, header=False)
            messagebox.showinfo("成功", f"文件已保存到: {filepath}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorNamerApp(root)
    root.mainloop()
