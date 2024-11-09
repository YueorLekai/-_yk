import tkinter as tk
from tkinter import filedialog, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import handle_function  # 导入 handle_function 模块

# 全局变量用来保存读取的图片
wait_handle = None
transformed_img_global = None


class DualSlider(ttk.Frame):
    def __init__(self, master=None, from_=0, to=100, label1="滑块1", label2="滑块2", **kwargs):
        super().__init__(master, **kwargs)

        self.scale_var1 = tk.IntVar(value=from_)
        self.scale_var2 = tk.IntVar(value=to)

        # 创建第一个滑块及其标签
        frame1 = ttk.Frame(self)
        frame1.grid(row=0, column=0, padx=10, pady=10)
        self.label1 = ttk.Label(frame1, text=f"{label1}: {self.scale_var1.get()}")
        self.label1.pack(anchor=tk.W)
        self.scale1 = ttk.Scale(frame1, from_=from_, to=to, orient=tk.HORIZONTAL,
                                variable=self.scale_var1, command=self.on_slider_move)
        self.scale1.pack()

        # 创建第二个滑块及其标签
        frame2 = ttk.Frame(self)
        frame2.grid(row=0, column=1, padx=10, pady=10)
        self.label2 = ttk.Label(frame2, text=f"{label2}: {self.scale_var2.get()}")
        self.label2.pack(anchor=tk.E)
        self.scale2 = ttk.Scale(frame2, from_=from_, to=to, orient=tk.HORIZONTAL,
                                variable=self.scale_var2, command=self.on_slider_move)
        self.scale2.pack()

        # 创建一个文本框来显示滑块的值
        self.value_display = tk.StringVar()
        self.value_label = ttk.Label(self, textvariable=self.value_display)
        self.value_label.grid(row=1, column=0, columnspan=2, pady=10)

        self.update_labels()

    def on_slider_move(self, *args):
        # 防止滑块重叠
        if self.scale_var1.get() > self.scale_var2.get():
            self.scale_var1.set(self.scale_var2.get())
        elif self.scale_var2.get() < self.scale_var1.get():
            self.scale_var2.set(self.scale_var1.get())

        # 更新显示
        self.update_labels()

        # 实时更新图像
        apply_current_transformation()

    def update_labels(self):
        self.label1.config(text=f"{self.label1.cget('text').split(':')[0]}: {self.scale_var1.get()}")
        self.label2.config(text=f"{self.label2.cget('text').split(':')[0]}: {self.scale_var2.get()}")
        self.value_display.set(f"({self.scale_var1.get()}, {self.scale_var2.get()})")


def load_image():
    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(
        title="选择图片",
        filetypes=[("Image files", "*.bmp *.jpg *.jpeg *.png *.gif *.tiff")]
    )

    if file_path:
        # 使用numpy和cv2读取图片
        img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

        # 获取按钮的实际宽度
        button_width = load_button.winfo_width()

        # 计算新的图像尺寸
        height, width = img.shape[:2]
        new_width = 2 * button_width
        new_height = int(height * (new_width / width))

        # 调整图像大小
        img = cv2.resize(img, (new_width, new_height))

        # 转换颜色通道，因为OpenCV默认是BGR而Tkinter需要RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # 将图像转换为Tkinter PhotoImage
        global photo, wait_handle
        photo = ImageTk.PhotoImage(image=Image.fromarray(img))

        # 保存图像到全局变量
        wait_handle = img

        # 更新标签上的图像
        image_label.config(image=photo)
        image_label.image = photo  # 防止垃圾回收


def apply_linear_trans():
    if wait_handle is not None:
        # 获取滑块的值
        a = original_range_slider.scale_var1.get()
        b = original_range_slider.scale_var2.get()
        c = target_range_slider.scale_var1.get()
        d = target_range_slider.scale_var2.get()
        flag = use_c_d_flag.get()  # 获取复选框的值

        # 转换为灰度图
        gray_img = cv2.cvtColor(wait_handle, cv2.COLOR_RGB2GRAY)

        # 应用线性变换
        transformed_img = handle_function.linear_trans(gray_img, a, b, c, d, flag)

        # 将结果转换为 uint8 类型
        transformed_img = np.clip(transformed_img, 0, 255).astype(np.uint8)

        # 转换颜色通道，因为OpenCV默认是BGR而Tkinter需要RGB
        transformed_img = cv2.cvtColor(transformed_img, cv2.COLOR_GRAY2RGB)

        # 将图像转换为Tkinter PhotoImage
        transformed_photo = ImageTk.PhotoImage(image=Image.fromarray(transformed_img))

        # 更新标签上的图像
        transformed_image_label.config(image=transformed_photo)
        transformed_image_label.image = transformed_photo  # 防止垃圾回收

        # 保存变换后的图像到全局变量
        global transformed_img_global
        transformed_img_global = transformed_img


def apply_piecewise_linear_trans():
    if wait_handle is not None:
        # 获取滑块的值
        a = original_range_slider.scale_var1.get()
        b = original_range_slider.scale_var2.get()
        c = target_range_slider.scale_var1.get()
        d = target_range_slider.scale_var2.get()

        # 转换为灰度图
        gray_img = cv2.cvtColor(wait_handle, cv2.COLOR_RGB2GRAY)

        # 应用分段线性变换
        transformed_img = handle_function.P_linear_trans(gray_img, a, b, c, d)

        # 将结果转换为 uint8 类型
        transformed_img = np.clip(transformed_img, 0, 255).astype(np.uint8)

        # 转换颜色通道，因为OpenCV默认是BGR而Tkinter需要RGB
        transformed_img = cv2.cvtColor(transformed_img, cv2.COLOR_GRAY2RGB)

        # 将图像转换为Tkinter PhotoImage
        transformed_photo = ImageTk.PhotoImage(image=Image.fromarray(transformed_img))

        # 更新标签上的图像
        transformed_image_label.config(image=transformed_photo)
        transformed_image_label.image = transformed_photo  # 防止垃圾回收

        # 保存变换后的图像到全局变量
        global transformed_img_global
        transformed_img_global = transformed_img


def apply_threshold_trans():
    if wait_handle is not None:
        # 获取阈值
        T = threshold_slider_var.get()
        min_val = target_range_slider.scale_var1.get()
        max_val = target_range_slider.scale_var2.get()

        # 转换为灰度图
        gray_img = cv2.cvtColor(wait_handle, cv2.COLOR_RGB2GRAY)

        # 应用阈值变换
        transformed_img = handle_function.threshold_trans(gray_img, T, min_val, max_val)

        # 将结果转换为 uint8 类型
        transformed_img = np.clip(transformed_img, 0, 255).astype(np.uint8)

        # 转换颜色通道，因为OpenCV默认是BGR而Tkinter需要RGB
        transformed_img = cv2.cvtColor(transformed_img, cv2.COLOR_GRAY2RGB)

        # 将图像转换为Tkinter PhotoImage
        transformed_photo = ImageTk.PhotoImage(image=Image.fromarray(transformed_img))

        # 更新标签上的图像
        transformed_image_label.config(image=transformed_photo)
        transformed_image_label.image = transformed_photo  # 防止垃圾回收

        # 保存变换后的图像到全局变量
        global transformed_img_global
        transformed_img_global = transformed_img


def apply_invert_gray():
    if wait_handle is not None:
        # 转换为灰度图
        gray_img = cv2.cvtColor(wait_handle, cv2.COLOR_RGB2GRAY)

        # 应用灰度反转
        transformed_img = handle_function.invert_gray(gray_img)

        # 将结果转换为 uint8 类型
        transformed_img = np.clip(transformed_img, 0, 255).astype(np.uint8)

        # 转换颜色通道，因为OpenCV默认是BGR而Tkinter需要RGB
        transformed_img = cv2.cvtColor(transformed_img, cv2.COLOR_GRAY2RGB)

        # 将图像转换为Tkinter PhotoImage
        transformed_photo = ImageTk.PhotoImage(image=Image.fromarray(transformed_img))

        # 更新标签上的图像
        transformed_image_label.config(image=transformed_photo)
        transformed_image_label.image = transformed_photo  # 防止垃圾回收

        # 保存变换后的图像到全局变量
        global transformed_img_global
        transformed_img_global = transformed_img


def apply_log_trans():
    if wait_handle is not None:
        # 获取对数变换参数
        c = log_slider_var.get()

        # 转换为灰度图
        gray_img = cv2.cvtColor(wait_handle, cv2.COLOR_RGB2GRAY)

        # 应用对数变换
        transformed_img = handle_function.log_trans(gray_img, c)

        # 转换颜色通道，因为OpenCV默认是BGR而Tkinter需要RGB
        transformed_img = cv2.cvtColor(transformed_img, cv2.COLOR_GRAY2RGB)

        # 将图像转换为Tkinter PhotoImage
        transformed_photo = ImageTk.PhotoImage(image=Image.fromarray(transformed_img))

        # 更新标签上的图像
        transformed_image_label.config(image=transformed_photo)
        transformed_image_label.image = transformed_photo  # 防止垃圾回收

        # 保存变换后的图像到全局变量
        global transformed_img_global
        transformed_img_global = transformed_img


def apply_power_trans():
    if wait_handle is not None:
        # 获取幂次变换参数
        gamma = power_slider.scale_var1.get()
        c = power_slider.scale_var2.get()

        # 转换为灰度图
        gray_img = cv2.cvtColor(wait_handle, cv2.COLOR_RGB2GRAY)

        # 应用幂次变换
        transformed_img = handle_function.power_trans(gray_img, gamma, c)

        # 转换颜色通道，因为OpenCV默认是BGR而Tkinter需要RGB
        transformed_img = cv2.cvtColor(transformed_img, cv2.COLOR_GRAY2RGB)

        # 将图像转换为Tkinter PhotoImage
        transformed_photo = ImageTk.PhotoImage(image=Image.fromarray(transformed_img))

        # 更新标签上的图像
        transformed_image_label.config(image=transformed_photo)
        transformed_image_label.image = transformed_photo  # 防止垃圾回收

        # 保存变换后的图像到全局变量
        global transformed_img_global
        transformed_img_global = transformed_img


def apply_histogram_equalization():
    if wait_handle is not None:
        # 转换为灰度图
        gray_img = cv2.cvtColor(wait_handle, cv2.COLOR_RGB2GRAY)

        # 应用直方图均衡化
        transformed_img = handle_function.Histogram_Equalization(gray_img)

        # 将结果转换为 uint8 类型
        transformed_img = np.clip(transformed_img, 0, 255).astype(np.uint8)

        # 转换颜色通道，因为OpenCV默认是BGR而Tkinter需要RGB
        transformed_img = cv2.cvtColor(transformed_img, cv2.COLOR_GRAY2RGB)

        # 将图像转换为Tkinter PhotoImage
        transformed_photo = ImageTk.PhotoImage(image=Image.fromarray(transformed_img))

        # 更新标签上的图像
        transformed_image_label.config(image=transformed_photo)
        transformed_image_label.image = transformed_photo  # 防止垃圾回收

        # 保存变换后的图像到全局变量
        global transformed_img_global
        transformed_img_global = transformed_img


def apply_current_transformation(*args):
    current_transformation = transformation_var.get()
    print(f"Applying transformation: {current_transformation}")  # 调试输出
    if current_transformation == "线性变换":
        apply_linear_trans()
    elif current_transformation == "分段线性变换":
        apply_piecewise_linear_trans()
    elif current_transformation == "阈值变换":
        apply_threshold_trans()
    elif current_transformation == "灰度反转":
        apply_invert_gray()
    elif current_transformation == "对数变换":
        apply_log_trans()
    elif current_transformation == "幂次变换":
        apply_power_trans()
    elif current_transformation == "直方图均衡化":
        apply_histogram_equalization()


def update_ui():
    current_transformation = transformation_var.get()
    print(f"Updating UI for: {current_transformation}")  # 调试输出

    # 隐藏所有滑块和复选框
    original_range_slider.grid_remove()
    target_range_slider.grid_remove()
    threshold_slider.grid_remove()
    log_slider.grid_remove()
    power_slider.grid_remove()
    use_c_d_checkbox.grid_remove()

    if current_transformation == "线性变换":
        original_range_slider.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        target_range_slider.grid(row=2, column=1, padx=10, pady=10, sticky=tk.E)
        use_c_d_checkbox.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
    elif current_transformation == "分段线性变换":
        original_range_slider.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        target_range_slider.grid(row=2, column=1, padx=10, pady=10, sticky=tk.E)
    elif current_transformation == "阈值变换":
        threshold_slider_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        threshold_slider.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        target_range_slider.grid(row=2, column=1, padx=10, pady=10, sticky=tk.E)
    elif current_transformation == "灰度反转" or current_transformation == "直方图均衡化":
        pass
    elif current_transformation == "对数变换":
        log_slider_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        log_slider.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
    elif current_transformation == "幂次变换":
        power_slider.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)


def export_image():
    global transformed_img_global

    if transformed_img_global is not None:
        # 打开文件保存对话框
        file_path = filedialog.asksaveasfilename(
            title="保存图片",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )

        if file_path:
            # 获取文件扩展名
            file_extension = file_path.split('.')[-1].lower()

            # 使用OpenCV将图像编码为字节流
            if file_extension == 'png':
                encode_params = [int(cv2.IMWRITE_PNG_COMPRESSION), 9]
            elif file_extension in ['jpg', 'jpeg']:
                encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            else:
                encode_params = []

            success, img_encoded = cv2.imencode('.' + file_extension, transformed_img_global, encode_params)

            if success:
                # 使用numpy的tofile()方法保存字节流
                img_encoded.tofile(file_path)
                print(f"图像已成功保存到: {file_path}")
            else:
                print(f"保存图像失败: {file_path}")
        else:
            print("未选择保存路径。")
    else:
        print("没有可保存的图像。请先加载并处理图像。")


# 创建主窗口
root = tk.Tk()
root.title("乐凯图片灰度图片处理")

# 设置窗口大小
root.geometry("550x800")  # 宽度800像素，高度600像素

# 使用 ttk 模块的样式
style = ttk.Style()
style.theme_use('clam')

# 创建一个按钮，用于触发文件选择
load_button = ttk.Button(root, text="读取图片", command=load_image)
load_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

# 创建一个标签，用于显示原始图片
image_label = ttk.Label(root)
image_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

# 创建一个标签，用于显示变换后的图片
transformed_image_label = ttk.Label(root)
transformed_image_label.grid(row=1, column=1, padx=10, pady=10, sticky=tk.E)

# 创建两个DualSlider对象
original_range_slider = DualSlider(root, from_=0, to=255, label1="原图灰度下界(a)", label2="变换上界(b)")
target_range_slider = DualSlider(root, from_=0, to=255, label1="目标最小值(c)", label2="最大值(d)")

# 创建一个单滑块对象
threshold_slider_var = tk.IntVar(value=128)
threshold_slider_label = ttk.Label(root, text="阈值(T)")
threshold_slider = ttk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, variable=threshold_slider_var,
                             command=apply_current_transformation)

log_slider_var = tk.DoubleVar(value=1.0)
log_slider_label = ttk.Label(root, text="c")
log_slider = ttk.Scale(root, from_=0, to=105.9, orient=tk.HORIZONTAL, variable=log_slider_var,
                       command=apply_current_transformation)

power_slider = DualSlider(root, from_=0, to=10, label1="Gamma", label2="C")

# 创建一个复选框来控制 flag 的值
use_c_d_flag = tk.BooleanVar(value=True)  # 默认勾选
use_c_d_checkbox = ttk.Checkbutton(root, text="非目标区段使用c,d定值", variable=use_c_d_flag,
                                   command=apply_linear_trans)

# 创建一个导出按钮
export_button = ttk.Button(root, text="导出图像", command=export_image)
export_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# 创建功能按钮
transformation_var = tk.StringVar(value="线性变换")

linear_trans_button = ttk.Button(root, text="线性变换",
                                 command=lambda: [transformation_var.set("线性变换"), update_ui(),
                                                  apply_current_transformation()])
linear_trans_button.grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)

piecewise_linear_trans_button = ttk.Button(root, text="分段线性变换",
                                           command=lambda: [transformation_var.set("分段线性变换"), update_ui(),
                                                            apply_current_transformation()])
piecewise_linear_trans_button.grid(row=5, column=1, padx=10, pady=10, sticky=tk.E)

threshold_trans_button = ttk.Button(root, text="阈值变换",
                                    command=lambda: [transformation_var.set("阈值变换"), update_ui(),
                                                     apply_current_transformation()])
threshold_trans_button.grid(row=6, column=0, padx=10, pady=10, sticky=tk.W)

invert_gray_button = ttk.Button(root, text="灰度反转", command=lambda: [transformation_var.set("灰度反转"), update_ui(),
                                                                        apply_current_transformation()])
invert_gray_button.grid(row=6, column=1, padx=10, pady=10, sticky=tk.E)

log_trans_button = ttk.Button(root, text="对数变换", command=lambda: [transformation_var.set("对数变换"), update_ui(),
                                                                      apply_current_transformation()])
log_trans_button.grid(row=7, column=0, padx=10, pady=10, sticky=tk.W)

power_trans_button = ttk.Button(root, text="幂次变换", command=lambda: [transformation_var.set("幂次变换"), update_ui(),
                                                                        apply_current_transformation()])
power_trans_button.grid(row=7, column=1, padx=10, pady=10, sticky=tk.E)

histogram_equalization_button = ttk.Button(root, text="直方图均衡化",
                                           command=lambda: [transformation_var.set("直方图均衡化"), update_ui(),
                                                            apply_current_transformation()])
histogram_equalization_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

# 初始状态设置
update_ui()

# 运行主循环
root.mainloop()