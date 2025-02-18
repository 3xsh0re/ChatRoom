import random
import sqlite3
import hashlib
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from need_module import json, ctypes, sys, os
import time


class Login(object):
    def __init__(self, Register, Chat, master=None):
        self.root = master  # 定义内部变量root
        self.root.title("登录窗口")
        self.Register = Register
        self.Chat = Chat
        self.root.iconbitmap(r"images/icon/login.ico")  # 设置左上角窗口图标

        # 设置窗口居中
        sw = self.root.winfo_screenwidth()  # 计算水平距离
        sh = self.root.winfo_screenheight()  # 计算垂直距离
        w = 690  # 宽
        h = 535  # 高
        x = (sw - w) / 2
        y = (sh - h) / 2
        self.root.geometry("%dx%d+%d+%d" % (w, h, (x + 160), y))
        self.root.resizable(0, 0)  # 窗口设置为不可放大缩小
        # 告诉操作系统使用程序自身的dpi适配
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        # 获取屏幕的缩放因子
        ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        # 设置程序缩放
        self.root.tk.call("tk", "scaling", ScaleFactor / 75)
        self.creatlogin()
        # new
        self.failed_attempts = 0
        self.locked_until = 0
        self.max_failed_attempts = 3  # 设置最大失败次数
        self.lock_duration = 60  # 锁定时长，单位为秒

    def creatlogin(self):
        self.fr2 = Frame(self.root)
        self.fr2.pack()
        self.fr1 = Frame(self.root)
        self.fr1.pack(pady=10)

        self.benner_list = [
            "images/benner/banner-1.jpg",
            "images/benner/banner-2.jpg",
            "images/benner/banner-3.jpg",
            "images/benner/banner-4.jpg",
            "images/benner/banner-5.jpg",
            "images/benner/banner-6.jpg",
        ]
        self.benner_img = random.choice(self.benner_list)  # 随机一张背景图

        # 图片大小：690x300
        self.pic = Image.open(self.benner_img)
        self.login_benner = ImageTk.PhotoImage(self.pic)

        # 标签 图片
        self.imgLabel = Label(self.fr2, image=self.login_benner)
        self.imgLabel.pack()

        # 标签 用户和密码
        self.label_usr = Label(self.fr1, text="用户名：")
        self.label_usr.grid(row=0, column=0, pady=10)
        self.label_pwd = Label(self.fr1, text="密  码：")
        self.label_pwd.grid(row=1, column=0)

        # 文本框 用户名
        self.var_usr_name = StringVar()
        self.entry_name = Entry(self.fr1, textvariable=self.var_usr_name)
        self.entry_name.grid(row=0, column=1)
        self.entry_name.focus_set()  # 获得焦点
        # 文本框 密码
        self.var_usr_pwd = StringVar()
        self.entry_pwd = Entry(self.fr1, textvariable=self.var_usr_pwd, show="*")
        self.entry_pwd.grid(row=1, column=1)

        self.saved_msg()

        self.fr3 = Frame(self.root)
        self.fr3.pack()
        self.rd_login = IntVar()
        self.rd_Passwd = IntVar()
        self.checkboxLogin = Checkbutton(self.fr3, text="自动登录", variable=self.rd_login)
        self.checkboxPasswd = Checkbutton(
            self.fr3, text="记住密码", variable=self.rd_Passwd
        )

        self.la = Label(self.fr3, width=5)
        self.la.grid(row=0, column=0)
        self.checkboxLogin.grid(row=0, column=1)
        self.checkboxPasswd.grid(row=0, column=2)
        # 登录
        self.root.bind("<Return>", self.check_login)  # 绑定回车键

        self.bt_login = Button(
            self.fr3, text=" 登录 ", command=lambda: self.check_login()
        )
        self.bt_login.grid(row=1, column=1, pady=5)
        self.bt_quit = Button(self.fr3, text=" 退出 ", command=sys.exit)
        self.bt_quit.grid(row=1, column=2)

        # # 底部标签
        self.fr4 = Frame(self.root)
        self.fr4.pack(side="bottom")

        self.bt_register = Button(
            self.fr4,
            text=" 注册账号",
            relief=FLAT,
            bg="#f0f0f0",
            command=self.login_win_close,
        )
        self.bt_register.pack(side="left", anchor="s")
        self.la2 = Label(self.fr4, width=150)
        self.la2.pack()
        self.tsLabel2 = Label(self.fr4, text="聊天登录界面 by LGH ", fg="red")
        self.tsLabel2.pack(side="right", anchor="s", pady=5)

    def red_msg(self):
        if self.rd_Passwd.get() == 1:
            # 创建新的JSON
            new_usr = {
                "username": self.var_usr_name.get(),
                "password": self.var_usr_pwd.get(),
            }
            with open("usr.json", "w") as wp:
                json.dump(new_usr, wp)

    def saved_msg(self):
        self.saved_name = ""
        self.saved_pwd = ""
        if os.path.exists("usr.json"):
            with open("usr.json", "r") as fp:
                json_file = json.load(fp)
                json_str = json.dumps(json_file)

                json_date = json.loads(json_str)
                print(json_date)
                self.saved_name = json_date["username"]
                self.saved_pwd = json_date["password"]
                # print(self.saved_name,self.saved_pwd)
        if self.saved_name != "":
            self.entry_name.insert(END, self.saved_name)
            self.entry_pwd.insert(END, self.saved_pwd)

    def login_win_close(self):
        self.fr1.destroy()
        self.fr2.destroy()
        self.fr3.destroy()
        self.fr4.destroy()  # 登录界面卸载
        self.Register(Login, self.Chat, self.root)  # 密码对，就把主窗体模块的界面加载

    def check_login(self, *args):
        self.usr_name = self.var_usr_name.get()
        self.usr_pwd = self.var_usr_pwd.get()
        conn = sqlite3.connect("yonghu.db")
        cursor = conn.cursor()

        if self.usr_name == "" or self.usr_pwd == "":
            messagebox.showwarning(title="提示", message="用户名密码不能为空")
        else:
            # 检查账号是否处于锁定状态
            if self.locked_until > time.time():
                remaining_time = int(self.locked_until - time.time())
                messagebox.showwarning(
                    title="提示", message=f"账号已被锁定，请在{remaining_time}秒后重试！"
                )
            else:
                # 查询哈希密码
                cursor.execute(
                    "SELECT password FROM user WHERE username=?", (self.usr_name,)
                )
                hashed_pwd = cursor.fetchone()

                if hashed_pwd:
                    # 验证密码，首先尝试使用明文密码验证
                    if self.usr_pwd == hashed_pwd[0]:
                        messagebox.showinfo(title="提示", message="登录成功，欢迎回来!")
                        self.root.unbind("<Return>")
                        self.red_msg()
                        print("是否记住密码:", self.rd_Passwd.get())
                        self.fr1.destroy()
                        self.fr2.destroy()
                        self.fr3.destroy()
                        self.fr4.destroy()
                        self.Chat(self.usr_name)
                        # 重置登录失败次数
                        self.failed_attempts = 0
                    else:
                        # 尝试使用哈希密码验证
                        hashed_input_pwd = hashlib.sha256(
                            self.usr_pwd.encode()
                        ).hexdigest()
                        if hashed_input_pwd == hashed_pwd[0]:
                            messagebox.showinfo(title="提示", message="登录成功，欢迎回来!")
                            self.root.unbind("<Return>")
                            self.red_msg()
                            print("是否记住密码:", self.rd_Passwd.get())
                            self.fr1.destroy()
                            self.fr2.destroy()
                            self.fr3.destroy()
                            self.fr4.destroy()
                            self.Chat(self.usr_name)
                            # 重置登录失败次数
                            self.failed_attempts = 0
                        else:
                            # 增加登录失败次数并检查是否需要锁定账号
                            self.failed_attempts += 1
                            if self.failed_attempts >= self.max_failed_attempts:
                                # 锁定账号
                                self.locked_until = time.time() + self.lock_duration
                                self.failed_attempts = 0  # 重置登录失败次数
                                messagebox.showerror(
                                    title="提示", message="失败次数过多，账号已被锁定！"
                                )
                            else:
                                messagebox.showerror(title="提示", message="用户名或密码错误！")
                else:
                    messagebox.showerror(title="提示", message="没有该用户！")

        cursor.close()
        conn.close()
        return "break"
