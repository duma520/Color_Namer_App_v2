import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import colorsys
import pandas as pd
from PIL import Image, ImageTk

class HSLColorNamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HSL/RGB颜色命名工具")
        self.file_type = "RGB"  # 默认处理RGB格式
        self.setup_ui()
        
    def setup_ui(self):
        # 文件类型选择
        tk.Label(self.root, text="输入文件格式:").grid(row=0, column=0, padx=5, pady=5)
        self.format_var = tk.StringVar(value="RGB")
        formats = ttk.Combobox(self.root, textvariable=self.format_var, 
                             values=["RGB", "HSL"], state="readonly")
        formats.grid(row=0, column=1, sticky='w')
        formats.bind("<<ComboboxSelected>>", self.change_format)

        # 颜色预览区域
        self.color_canvas = tk.Canvas(self.root, width=200, height=200, bg='white')
        self.color_canvas.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        
        # 输入控件动态区域
        self.input_frame = tk.Frame(self.root)
        self.input_frame.grid(row=2, column=0, columnspan=3)
        self.setup_input_controls()

        # 结果显示
        self.result_label = tk.Label(self.root, text="颜色名称将显示在这里", font=('Microsoft YaHei', 10))
        self.result_label.grid(row=3, column=0, columnspan=3)
        
        # 文件操作区域
        tk.Label(self.root, text="批量处理:").grid(row=4, column=0, sticky='e', pady=(20,0))
        self.import_btn = tk.Button(self.root, text="导入CSV", command=self.import_csv)
        self.import_btn.grid(row=4, column=1, sticky='w', pady=(20,0))
        
        self.export_btn = tk.Button(self.root, text="导出CSV", state='disabled', command=self.export_csv)
        self.export_btn.grid(row=4, column=2, sticky='w', pady=(20,0))
        
        # 数据存储
        self.df = None
    
    def setup_input_controls(self):
        """根据当前选择的格式动态创建输入控件"""
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        
        if self.file_type == "RGB":
            tk.Label(self.input_frame, text="R:").grid(row=0, column=0)
            self.c1_entry = tk.Entry(self.input_frame, width=5)
            self.c1_entry.grid(row=0, column=1)
            self.c1_entry.insert(0, "255")
            
            tk.Label(self.input_frame, text="G:").grid(row=1, column=0)
            self.c2_entry = tk.Entry(self.input_frame, width=5)
            self.c2_entry.grid(row=1, column=1)
            self.c2_entry.insert(0, "0")
            
            tk.Label(self.input_frame, text="B:").grid(row=2, column=0)
            self.c3_entry = tk.Entry(self.input_frame, width=5)
            self.c3_entry.grid(row=2, column=1)
            self.c3_entry.insert(0, "0")
        else:
            tk.Label(self.input_frame, text="H (0-360):").grid(row=0, column=0)
            self.c1_entry = tk.Entry(self.input_frame, width=5)
            self.c1_entry.grid(row=0, column=1)
            self.c1_entry.insert(0, "0")
            
            tk.Label(self.input_frame, text="S (0-100):").grid(row=1, column=0)
            self.c2_entry = tk.Entry(self.input_frame, width=5)
            self.c2_entry.grid(row=1, column=1)
            self.c2_entry.insert(0, "100")
            
            tk.Label(self.input_frame, text="L (0-100):").grid(row=2, column=0)
            self.c3_entry = tk.Entry(self.input_frame, width=5)
            self.c3_entry.grid(row=2, column=1)
            self.c3_entry.insert(0, "50")
        
        self.name_btn = tk.Button(self.input_frame, text="获取颜色名称", command=self.show_color_name)
        self.name_btn.grid(row=3, column=0, columnspan=2, pady=5)
    
    def change_format(self, event):
        """切换文件格式时更新界面"""
        self.file_type = self.format_var.get()
        self.setup_input_controls()
    
    def get_hsl_name(self, h, s, l):
        """HSL精细化命名算法"""
        # 转换到0-1范围
        s /= 100.0
        l /= 100.0
        
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
            (15, "红"), (45, "橙红"), (60, "橙"), 
            (90, "黄橙"), (120, "黄绿"), (180, "绿"),
            (210, "青绿"), (240, "青"), (270, "蓝青"),
            (300, "蓝"), (330, "紫蓝"), (360, "紫红")
        ]
        
        for threshold, name in hues:
            if h <= threshold:
                return f"{saturation_desc}{lightness_desc}{name}"
        return "未知颜色"
    
    def update_color_preview(self, color):
        """更新颜色预览区域"""
        if self.file_type == "RGB":
            r, g, b = color
        else:
            r, g, b = [int(x*255) for x in colorsys.hls_to_rgb(color[0]/360, color[2]/100, color[1]/100)]
        
        color_img = Image.new('RGB', (200, 200), (r, g, b))
        self.color_img = ImageTk.PhotoImage(color_img)
        self.color_canvas.create_image(0, 0, anchor='nw', image=self.color_img)
    
    def show_color_name(self):
        """处理单个颜色命名"""
        try:
            c1 = float(self.c1_entry.get())
            c2 = float(self.c2_entry.get())
            c3 = float(self.c3_entry.get())
            
            if self.file_type == "RGB":
                if not (0 <= c1 <=255 and 0 <= c2 <=255 and 0 <= c3 <=255):
                    raise ValueError("RGB值需在0-255范围内")
                h = colorsys.rgb_to_hls(c1/255, c2/255, c3/255)[0] * 360
                s = colorsys.rgb_to_hls(c1/255, c2/255, c3/255)[2] * 100
                l = colorsys.rgb_to_hls(c1/255, c2/255, c3/255)[1] * 100
                color_name = self.get_hsl_name(h, s, l)
                self.update_color_preview((c1, c2, c3))
            else:
                if not (0 <= c1 <=360 and 0 <= c2 <=100 and 0 <= c3 <=100):
                    raise ValueError("HSL值需在H:0-360 S/L:0-100范围内")
                color_name = self.get_hsl_name(c1, c2, c3)
                self.update_color_preview((c1, c2, c3))
            
            self.result_label.config(text=f"颜色名称: {color_name}")
            
        except ValueError as e:
            messagebox.showerror("错误", str(e))
    
    def import_csv(self):
        """导入CSV文件"""
        filepath = filedialog.askopenfilename(filetypes=[("CSV文件", "*.csv")])
        if not filepath:
            return
            
        try:
            self.df = pd.read_csv(filepath, header=None)
            if len(self.df.columns) < 3:
                raise ValueError("CSV需要至少3列数据")
                
            # 根据格式处理数据
            if self.file_type == "RGB":
                # 验证RGB范围
                if not ((self.df.iloc[:, :3] >= 0).all().all() and (self.df.iloc[:, :3] <= 255).all().all()):
                    raise ValueError("RGB值需在0-255范围内")
                
                # 转换为HSL用于命名
                hsl_data = []
                for _, row in self.df.iterrows():
                    r, g, b = row[0]/255, row[1]/255, row[2]/255
                    h, l, s = colorsys.rgb_to_hls(r, g, b)
                    hsl_data.append([h*360, s*100, l*100])
                
                self.df['颜色名称'] = [self.get_hsl_name(*hsl) for hsl in hsl_data]
            else:
                # 验证HSL范围
                if not ((self.df.iloc[:, 0] >= 0).all() and (self.df.iloc[:, 0] <= 360).all() and
                        (self.df.iloc[:, 1] >= 0).all() and (self.df.iloc[:, 1] <= 100).all() and
                        (self.df.iloc[:, 2] >= 0).all() and (self.df.iloc[:, 2] <= 100).all()):
                    raise ValueError("HSL值需在H:0-360 S/L:0-100范围内")
                
                self.df['颜色名称'] = self.df.apply(
                    lambda row: self.get_hsl_name(row[0], row[1], row[2]), axis=1)
            
            self.export_btn.config(state='normal')
            messagebox.showinfo("成功", f"已处理 {len(self.df)} 行数据")
            
        except Exception as e:
            messagebox.showerror("错误", f"文件处理失败: {str(e)}")
    
    def export_csv(self):
        """导出结果CSV"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv")]
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
    app = HSLColorNamerApp(root)
    root.mainloop()
