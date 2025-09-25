import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageFont
import os
from typing import List, Optional

class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("简单水印工具")
        self.root.geometry("1000x700")
        
        # 数据存储
        self.images = []  # 存储图片路径
        self.current_image = None
        self.watermark_text = "水印"
        self.watermark_color = (255, 255, 255)  # 白色
        self.watermark_opacity = 128  # 透明度
        self.watermark_position = (50, 50)  # 位置
        self.watermark_size = 24  # 字体大小
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame.pack_propagate(False)
        
        # 图片导入区域
        import_frame = ttk.LabelFrame(control_frame, text="图片导入", padding=10)
        import_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(import_frame, text="选择图片", command=self.import_images).pack(fill=tk.X, pady=2)
        ttk.Button(import_frame, text="选择文件夹", command=self.import_folder).pack(fill=tk.X, pady=2)
        
        # 图片列表
        self.image_listbox = tk.Listbox(import_frame, height=6)
        self.image_listbox.pack(fill=tk.X, pady=5)
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        
        # 水印设置区域
        watermark_frame = ttk.LabelFrame(control_frame, text="水印设置", padding=10)
        watermark_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 水印文本
        ttk.Label(watermark_frame, text="水印文本:").pack(anchor=tk.W)
        self.text_entry = ttk.Entry(watermark_frame)
        self.text_entry.pack(fill=tk.X, pady=2)
        self.text_entry.insert(0, self.watermark_text)
        self.text_entry.bind('<KeyRelease>', self.update_watermark)
        
        # 字体大小
        ttk.Label(watermark_frame, text="字体大小:").pack(anchor=tk.W, pady=(10, 0))
        self.size_var = tk.IntVar(value=self.watermark_size)
        size_scale = ttk.Scale(watermark_frame, from_=10, to=100, variable=self.size_var, 
                              orient=tk.HORIZONTAL, command=self.update_watermark)
        size_scale.pack(fill=tk.X, pady=2)
        
        # 透明度
        ttk.Label(watermark_frame, text="透明度:").pack(anchor=tk.W, pady=(10, 0))
        self.opacity_var = tk.IntVar(value=self.watermark_opacity)
        opacity_scale = ttk.Scale(watermark_frame, from_=0, to=255, variable=self.opacity_var,
                                 orient=tk.HORIZONTAL, command=self.update_watermark)
        opacity_scale.pack(fill=tk.X, pady=2)
        
        # 颜色选择
        ttk.Button(watermark_frame, text="选择颜色", command=self.choose_color).pack(fill=tk.X, pady=5)
        
        # 位置调整
        position_frame = ttk.LabelFrame(control_frame, text="位置调整", padding=10)
        position_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 预设位置按钮
        positions = [
            ("左上", (50, 50)), ("中上", (400, 50)), ("右上", (750, 50)),
            ("左中", (50, 300)), ("中心", (400, 300)), ("右中", (750, 300)),
            ("左下", (50, 550)), ("中下", (400, 550)), ("右下", (750, 550))
        ]
        
        for i, (name, pos) in enumerate(positions):
            btn = ttk.Button(position_frame, text=name, 
                           command=lambda p=pos: self.set_position(p))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2, sticky=tk.W+tk.E)
        
        # 导出区域
        export_frame = ttk.LabelFrame(control_frame, text="导出设置", padding=10)
        export_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(export_frame, text="导出当前图片", command=self.export_current).pack(fill=tk.X, pady=2)
        ttk.Button(export_frame, text="批量导出", command=self.batch_export).pack(fill=tk.X, pady=2)
        
        # 右侧预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="预览", padding=10)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 预览画布
        self.canvas = tk.Canvas(preview_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定鼠标事件用于拖拽水印
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        
    def import_images(self):
        """导入单张或多张图片"""
        files = filedialog.askopenfilenames(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if files:
            self.images.extend(files)
            self.update_image_list()
            
    def import_folder(self):
        """导入文件夹中的所有图片"""
        folder = filedialog.askdirectory(title="选择图片文件夹")
        if folder:
            extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
            for file in os.listdir(folder):
                if file.lower().endswith(extensions):
                    self.images.append(os.path.join(folder, file))
            self.update_image_list()
            
    def update_image_list(self):
        """更新图片列表显示"""
        self.image_listbox.delete(0, tk.END)
        for img_path in self.images:
            filename = os.path.basename(img_path)
            self.image_listbox.insert(tk.END, filename)
            
    def on_image_select(self, event):
        """选择图片时的回调"""
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_image = self.images[index]
            self.update_preview()
            
    def choose_color(self):
        """选择水印颜色"""
        color = colorchooser.askcolor(title="选择水印颜色")
        if color[0]:
            self.watermark_color = tuple(map(int, color[0]))
            self.update_watermark()
            
    def set_position(self, position):
        """设置水印位置"""
        self.watermark_position = position
        self.update_watermark()
        
    def on_canvas_click(self, event):
        """画布点击事件"""
        if self.current_image:
            self.watermark_position = (event.x, event.y)
            self.update_watermark()
            
    def on_canvas_drag(self, event):
        """画布拖拽事件"""
        if self.current_image:
            self.watermark_position = (event.x, event.y)
            self.update_watermark()
            
    def update_watermark(self, *args):
        """更新水印设置"""
        self.watermark_text = self.text_entry.get()
        self.watermark_size = self.size_var.get()
        self.watermark_opacity = self.opacity_var.get()
        self.update_preview()
        
    def update_preview(self):
        """更新预览"""
        if not self.current_image:
            return
            
        try:
            # 加载图片
            img = Image.open(self.current_image)
            
            # 调整图片大小以适应画布
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                self.root.after(100, self.update_preview)
                return
                
            # 计算缩放比例
            img_ratio = img.width / img.height
            canvas_ratio = canvas_width / canvas_height
            
            if img_ratio > canvas_ratio:
                new_width = canvas_width - 20
                new_height = int(new_width / img_ratio)
            else:
                new_height = canvas_height - 20
                new_width = int(new_height * img_ratio)
                
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 添加水印
            img_with_watermark = self.add_watermark(img)
            
            # 转换为tkinter可显示的格式
            from PIL import ImageTk
            self.photo = ImageTk.PhotoImage(img_with_watermark)
            
            # 清除画布并显示图片
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width//2, canvas_height//2, 
                                   image=self.photo, anchor=tk.CENTER)
            
        except Exception as e:
            messagebox.showerror("错误", f"预览失败: {str(e)}")
            
    def add_watermark(self, img):
        """在图片上添加水印"""
        # 创建副本
        watermarked = img.copy()
        
        # 创建绘图对象
        draw = ImageDraw.Draw(watermarked)
        
        # 计算水印位置（相对于缩放后的图片）
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 计算图片在画布中的实际位置
        img_width = watermarked.width
        img_height = watermarked.height
        
        # 将画布坐标转换为图片坐标
        img_x = int((self.watermark_position[0] - canvas_width//2 + img_width//2) * img_width / img_width)
        img_y = int((self.watermark_position[1] - canvas_height//2 + img_height//2) * img_height / img_height)
        
        # 确保位置在图片范围内
        img_x = max(0, min(img_x, img_width))
        img_y = max(0, min(img_y, img_height))
        
        # 设置字体
        try:
            font = ImageFont.truetype("arial.ttf", self.watermark_size)
        except:
            font = ImageFont.load_default()
            
        # 设置颜色（包含透明度）
        color = (*self.watermark_color, self.watermark_opacity)
        
        # 绘制水印
        draw.text((img_x, img_y), self.watermark_text, font=font, fill=color)
        
        return watermarked
        
    def export_current(self):
        """导出当前图片"""
        if not self.current_image:
            messagebox.showwarning("警告", "请先选择一张图片")
            return
            
        # 选择输出文件
        filename = filedialog.asksaveasfilename(
            title="保存图片",
            defaultextension=".png",
            filetypes=[("PNG文件", "*.png"), ("JPEG文件", "*.jpg")]
        )
        
        if filename:
            try:
                # 加载原图
                img = Image.open(self.current_image)
                
                # 添加水印
                watermarked = self.add_watermark(img)
                
                # 保存
                watermarked.save(filename)
                messagebox.showinfo("成功", f"图片已保存到: {filename}")
                
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
                
    def batch_export(self):
        """批量导出"""
        if not self.images:
            messagebox.showwarning("警告", "请先导入图片")
            return
            
        # 选择输出文件夹
        output_dir = filedialog.askdirectory(title="选择输出文件夹")
        if not output_dir:
            return
            
        try:
            for i, img_path in enumerate(self.images):
                # 加载图片
                img = Image.open(img_path)
                
                # 添加水印
                watermarked = self.add_watermark(img)
                
                # 生成输出文件名
                base_name = os.path.splitext(os.path.basename(img_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}_watermarked.png")
                
                # 保存
                watermarked.save(output_path)
                
            messagebox.showinfo("成功", f"已批量导出 {len(self.images)} 张图片")
            
        except Exception as e:
            messagebox.showerror("错误", f"批量导出失败: {str(e)}")

def main():
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
