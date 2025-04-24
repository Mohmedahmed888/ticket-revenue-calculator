import customtkinter as ctk
from itertools import product
from functools import lru_cache
import datetime
import sqlite3
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import winsound
import numpy as np

class TicketRevenueApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # إعدادات النافذة الرئيسية
        self.title("Ticket Revenue Calculator")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # تهيئة المتغيرات
        self.fig = None
        self.ax = None
        self.canvas = None
        self.db_connection = None
        self._is_closing = False
        self.current_revenue = 0
        
        # إنشاء اتصال قاعدة البيانات
        self.initialize_database()
        
        # إنشاء نظام علامات التبويب
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # إضافة علامات التبويب
        self.tab_calculator = self.tabview.add("Calculator")
        self.tab_results = self.tabview.add("Results")
        self.tab_analytics = self.tabview.add("Analytics")
        self.tab_history = self.tabview.add("History")
        self.tab_settings = self.tabview.add("Settings")
        
        # تهيئة الإطارات والمتغيرات المطلوبة
        self.result_frame = None
        self.input_frame = None
        self.analytics_frame = None
        self.history_data_frame = None
        self.main_result_entry = None
        self.main_prices_label = None
        self.main_tickets_label = None
        self.main_algo_label = None
        self.main_time_label = None
        
        # إنشاء محتوى كل علامة تبويب
        self.create_calculator_tab()
        self.create_results_tab()
        self.create_analytics_tab()
        self.create_history_tab()
        self.create_settings_tab()
        
        # تسجيل دالة التنظيف عند الإغلاق
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # تسجيل دالة التنظيف عند انتهاء التطبيق
        self.bind("<Destroy>", self.cleanup)
        
        # تحميل البيانات التاريخية
        self.load_history_data()
    
    def initialize_database(self):
        """تهيئة قاعدة البيانات وإنشاء الجداول"""
        try:
            self.db_connection = sqlite3.connect('ticket_revenue.db')
            self.create_database()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
    
    def create_database(self):
        """إنشاء جدول قاعدة البيانات إذا لم يكن موجوداً"""
        if self.db_connection:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS revenue_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    prices TEXT NOT NULL,
                    tickets INTEGER NOT NULL,
                    revenue INTEGER NOT NULL,
                    method TEXT NOT NULL,
                    duration REAL NOT NULL
                )
            ''')
            self.db_connection.commit()
    
    def create_calculator_tab(self):
        # Main frame for calculator tab
        main_frame = ctk.CTkFrame(self.tab_calculator, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Input section frame (top)
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Title for input section
        input_title = ctk.CTkLabel(input_frame, text="Enter Ticket Prices", font=("Arial", 20, "bold"))
        input_title.pack(pady=10)
        
        # حقول إدخال الأسعار (9 حقول)
        self.price_entries = []
        entries_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        entries_frame.pack(fill="x", padx=20, pady=10)
        
        for row in range(3):
            row_frame = ctk.CTkFrame(entries_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            row_frame.grid_columnconfigure((0,1,2), weight=1)
            
            for col in range(3):
                entry = ctk.CTkEntry(
                    row_frame,
                    placeholder_text=f"Price {row*3 + col + 1}",
                    font=ctk.CTkFont(size=13),
                    height=35
                )
                entry.grid(row=0, column=col, padx=5, sticky="ew")
                self.price_entries.append(entry)
        
        # إطار عدد التذاكر
        tickets_frame = ctk.CTkFrame(input_frame)
        tickets_frame.pack(pady=10, padx=20, fill="x")
        
        tickets_label = ctk.CTkLabel(
            tickets_frame,
            text="Number of Tickets:",
            font=ctk.CTkFont(size=14)
        )
        tickets_label.pack(side="left", padx=10, pady=10)
        
        self.tickets_entry = ctk.CTkEntry(
            tickets_frame,
            width=100,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.tickets_entry.pack(side="left", padx=10, pady=10)
        
        # إطار اختيار الخوارزمية
        algo_frame = ctk.CTkFrame(input_frame)
        algo_frame.pack(pady=10, padx=20, fill="x")
        
        algo_label = ctk.CTkLabel(
            algo_frame,
            text="Select Algorithm:",
            font=ctk.CTkFont(size=14)
        )
        algo_label.pack(side="left", padx=10, pady=10)
        
        self.algorithm_var = ctk.StringVar(value="brute_force")
        
        # إنشاء الأزرار الاختيارية للخوارزميات
        algorithms = [
            ("Brute Force", "brute_force"),
            ("Dynamic Programming", "dynamic"),
            ("Optimized Greedy", "greedy")
        ]
        
        radio_frame = ctk.CTkFrame(algo_frame, fg_color="transparent")
        radio_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        for text, value in algorithms:
            radio = ctk.CTkRadioButton(
                radio_frame,
                text=text,
                value=value,
                variable=self.algorithm_var,
                font=ctk.CTkFont(size=13)
            )
            radio.pack(side="left", padx=10)
        
        # Progress bar frame
        progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=20, pady=5)
        
        # Create progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.set(0)
        
        # Calculate button
        calculate_button = ctk.CTkButton(main_frame,
                                     text="Calculate Maximum Revenue ▶",
                                     font=("Arial", 18, "bold"),
                                     height=50,
                                     command=self.calculate_revenue)
        calculate_button.pack(pady=20)
    
    @lru_cache(maxsize=1024)
    def optimized_max_revenue(self, prices_tuple, tickets_remaining, current_sum=0):
        """حساب أقصى إيراد ممكن باستخدام البرمجة الديناميكية"""
        if tickets_remaining == 0:
            return current_sum
        
        # تحسين: استخدام أعلى سعر مباشرة إذا كان عدد التذاكر كبيراً
        if tickets_remaining > 100:  # حد أقصى للحسابات التفصيلية
            max_price = max(prices_tuple)
            return current_sum + (max_price * tickets_remaining)
        
        return max(self.optimized_max_revenue(prices_tuple, tickets_remaining-1, current_sum+price) 
                  for price in sorted(prices_tuple, reverse=True))  # ترتيب تنازلي للأسعار
    
    def brute_force_max_revenue(self, prices, total_tickets):
        """
        حساب أقصى إيراد ممكن باستخدام القوة الغاشمة
        القيود:
        - لا يمكن استخدام سعر أقل بعد استخدام سعر أعلى
        - يجب استخدام جميع التذاكر
        
        مثال:
        [10, 20, 30, 40], 5 تذاكر -> 150 (40 + 40 + 30 + 20 + 20)
        الشرح: نبدأ بأعلى سعر (40) ونستخدمه مرتين، ثم 30 مرة، ثم 20 مرتين
        """
        if not prices or total_tickets <= 0:
            return 0
            
        # ترتيب الأسعار تنازلياً
        sorted_prices = sorted(prices, reverse=True)
        
        def get_max_revenue(tickets_left, max_price_index=0, memo=None):
            if memo is None:
                memo = {}
            
            # الحالة الأساسية: لا تذاكر متبقية
            if tickets_left == 0:
                return 0
                
            # الحالة الأساسية: لا أسعار متبقية
            if max_price_index >= len(sorted_prices):
                return float('-inf')  # قيمة سالبة كبيرة لتجنب هذا المسار
            
            # مفتاح التخزين المؤقت
            key = (tickets_left, max_price_index)
            if key in memo:
                return memo[key]
            
            current_price = sorted_prices[max_price_index]
            max_rev = float('-inf')
            
            # تجربة استخدام السعر الحالي
            if tickets_left >= 1:
                using_current = current_price + get_max_revenue(
                    tickets_left - 1,
                    max_price_index,  # يمكن استخدام نفس السعر مرة أخرى
                    memo
                )
                max_rev = max(max_rev, using_current)
            
            # تجربة السعر التالي
            not_using_current = get_max_revenue(
                tickets_left,
                max_price_index + 1,
                memo
            )
            max_rev = max(max_rev, not_using_current)
            
            memo[key] = max_rev
            return max_rev
        
        result = get_max_revenue(total_tickets)
        return result if result != float('-inf') else 0
    
    def dynamic_programming_max_revenue(self, prices, total_tickets):
        """
        حساب أقصى إيراد باستخدام البرمجة الديناميكية
        التعقيد الزمني: O(n * k) حيث n هو عدد الأسعار و k هو عدد التذاكر
        التعقيد المكاني: O(n * k)
        """
        if not prices or total_tickets <= 0:
            return 0
            
        n = len(prices)
        # ترتيب الأسعار تنازلياً
        prices = sorted(prices, reverse=True)
        
        # مصفوفة التخزين المؤقت
        # dp[i][j] تمثل أقصى إيراد يمكن تحقيقه باستخدام j تذكرة من الأسعار [0:i]
        dp = [[0] * (total_tickets + 1) for _ in range(n + 1)]
        
        # جدول التتبع لإعادة بناء الحل
        path = [[0] * (total_tickets + 1) for _ in range(n + 1)]
        
        for i in range(1, n + 1):
            current_price = prices[i-1]
            for j in range(1, total_tickets + 1):
                # لا نستخدم السعر الحالي
                dp[i][j] = dp[i-1][j]
                
                # نستخدم السعر الحالي إذا كان ممكناً
                if j >= 1:
                    using_current = current_price + dp[i][j-1]
                    if using_current > dp[i][j]:
                        dp[i][j] = using_current
                        path[i][j] = 1  # نشير إلى أننا استخدمنا هذا السعر
        
        # إعادة بناء الحل
        used_prices = []
        i, j = n, total_tickets
        while j > 0:
            if path[i][j] == 1:
                used_prices.append(prices[i-1])
                j -= 1
            else:
                i -= 1
        
        return dp[n][total_tickets], used_prices

    def optimized_greedy_max_revenue(self, prices, total_tickets):
        """
        حساب أقصى إيراد باستخدام الطريقة الجشعة المحسنة
        التعقيد الزمني: O(n log n) للترتيب + O(k) للتوزيع حيث k هو عدد التذاكر
        التعقيد المكاني: O(n)
        """
        if not prices or total_tickets <= 0:
            return 0
            
        # ترتيب الأسعار تنازلياً
        sorted_prices = sorted(prices, reverse=True)
        
        revenue = 0
        used_prices = []
        tickets_left = total_tickets
        
        # توزيع التذاكر على أعلى الأسعار أولاً
        i = 0
        while tickets_left > 0 and i < len(sorted_prices):
            revenue += sorted_prices[i]
            used_prices.append(sorted_prices[i])
            tickets_left -= 1
            
            # إذا كان السعر التالي أقل بكثير، نستمر باستخدام السعر الحالي
            if i + 1 < len(sorted_prices) and sorted_prices[i] > sorted_prices[i+1] * 1.5:
                continue
            i += 1
        
        return revenue, used_prices

    def calculate_revenue(self):
        try:
            # إظهار وبدء شريط التقدم
            self.progress_bar.pack(fill="x", padx=10, pady=5)
            self.progress_bar.start()
            
            # جمع الأسعار من حقول الإدخال
            prices = []
            for entry in self.price_entries:
                value = entry.get().strip()
                if value:
                    try:
                        price = int(value)
                        if price <= 0:
                            raise ValueError("Prices must be positive numbers")
                        prices.append(price)
                    except ValueError:
                        raise ValueError("Please enter valid numbers for prices")
            
            try:
                total_tickets = int(self.tickets_entry.get())
                if total_tickets <= 0:
                    raise ValueError("Number of tickets must be positive")
                elif total_tickets > 1000:
                    raise ValueError("Maximum number of tickets is 1000")
            except ValueError as e:
                if "Maximum number" in str(e):
                    raise e
                raise ValueError("Please enter a valid number of tickets")
            
            if not prices:
                raise ValueError("Please enter at least one price")
            
            # حساب الإيراد باستخدام الخوارزمية المختارة
            algorithm = self.algorithm_var.get()
            start_time = datetime.datetime.now()
            
            if algorithm == "brute_force":
                revenue = self.brute_force_max_revenue(prices, total_tickets)
                used_prices = []
                complexity = "O(n^k)"
                space = "O(k)"
                description = "1. Sort prices in descending order\n2. Try all possible combinations of prices\n3. Use memoization to avoid recalculating same states\n4. Return maximum revenue found"
            elif algorithm == "dynamic":
                revenue, used_prices = self.dynamic_programming_max_revenue(prices, total_tickets)
                complexity = "O(n*k)"
                space = "O(n*k)"
                description = "1. Sort prices in descending order\n2. Create DP table of size n×k\n3. Fill table using optimal substructure\n4. Track used prices during calculation\n5. Return maximum revenue and used prices"
            else:  # greedy
                revenue, used_prices = self.optimized_greedy_max_revenue(prices, total_tickets)
                complexity = "O(n log n)"
                space = "O(n)"
                description = "1. Sort prices in descending order\n2. Start with highest price\n3. Keep using current price if next price is much lower\n4. Move to next price if difference is small\n5. Return total revenue and used prices"
            
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # حفظ قيمة الإيراد في المتغير العام
            self.current_revenue = revenue
            
            # تحديث النتيجة في تبويب النتائج
            self.main_result_entry.configure(state="normal")
            self.main_result_entry.delete(0, "end")
            self.main_result_entry.insert(0, f"{revenue:,}")
            self.main_result_entry.configure(state="readonly")
            
            # تحديث التفاصيل في تبويب النتائج
            self.main_prices_label.configure(text=f"Prices: {', '.join(map(str, sorted(prices, reverse=True)))}")
            self.main_tickets_label.configure(text=f"Number of Tickets: {total_tickets}")
            self.main_algo_label.configure(text=f"Algorithm: {algorithm.replace('_', ' ').title()}")
            self.main_time_label.configure(text=f"Time: {duration:.4f} seconds")
            
            # تحديث معلومات التعقيد والخطوات
            self.main_time_complexity_label.configure(text=f"Time Complexity: {complexity}")
            self.main_space_complexity_label.configure(text=f"Space Complexity: {space}")
            self.main_steps_label.configure(text=description)
            
            # تحديث التحليلات
            self.update_analytics(prices, revenue)
            
            # تشغيل صوت النجاح
            self.play_sound("success")
            
            # التبديل إلى تبويب النتائج
            self.tabview.set("Results")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.play_sound("error")
        finally:
            # إيقاف وإخفاء شريط التقدم
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
    
    def create_analytics_tab(self):
        self.analytics_frame = ctk.CTkFrame(self.tab_analytics, fg_color="#ffffff")
        self.analytics_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # إضافة نص إرشادي مؤقت
        self.analytics_label = ctk.CTkLabel(self.analytics_frame, 
                                          text="Analytics will be shown here after calculations",
                                          text_color="gray")
        self.analytics_label.pack(pady=50)
    
    def update_analytics(self, prices, revenue):
        """تحديث الرسوم البيانية في تبويب التحليلات"""
        try:
            # تنظيف الإطار إذا كان هناك رسم بياني سابق
            for widget in self.analytics_frame.winfo_children():
                widget.destroy()
            
            # إغلاق الرسم البياني السابق إذا كان موجوداً
            if hasattr(self, 'fig') and self.fig:
                plt.close(self.fig)
            
            # إنشاء رسم بياني جديد
            self.fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            self.fig.patch.set_facecolor('#F0F0F0')  # لون خلفية الرسم البياني
            
            # الرسم البياني الأول: توزيع الأسعار
            unique_prices = sorted(set(prices), reverse=True)
            price_counts = [prices.count(p) for p in unique_prices]
            
            ax1.pie(price_counts, 
                   labels=[f"${p}" for p in unique_prices],
                   autopct='%1.1f%%',
                   colors=plt.cm.Pastel1(np.linspace(0, 1, len(unique_prices))))
            ax1.set_title('Price Distribution', pad=20, fontsize=12, fontweight='bold')
            
            # الرسم البياني الثاني: تحليل الإيراد
            avg_price = sum(prices) / len(prices)
            max_price = max(prices)
            potential_revenue = max_price * len(prices)
            
            categories = ['Average\nPrice', 'Highest\nPrice', 'Achieved\nRevenue', 'Maximum\nPotential']
            values = [avg_price, max_price, revenue, potential_revenue]
            colors = ['#3498DB', '#E74C3C', '#2ECC71', '#95A5A6']
            
            bars = ax2.bar(categories, values, color=colors)
            ax2.set_title('Revenue Analysis', pad=20, fontsize=12, fontweight='bold')
            
            # إضافة القيم على الأعمدة
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:,.0f}',
                        ha='center', va='bottom')
            
            # تحسين مظهر الرسم
            ax2.grid(True, linestyle='--', alpha=0.3)
            ax2.set_ylabel('Value ($)', fontsize=10)
            plt.xticks(rotation=0)
            
            # ضبط المساحة بين الرسوم البيانية
            plt.tight_layout(pad=3.0)
            
            # تضمين الرسم البياني في واجهة التطبيق
            canvas = FigureCanvasTkAgg(self.fig, master=self.analytics_frame)
            canvas.draw()
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill="both", expand=True, padx=20, pady=20)
            
            # إضافة أزرار التحكم
            control_frame = ctk.CTkFrame(self.analytics_frame, fg_color="transparent")
            control_frame.pack(fill="x", padx=20, pady=10)
            
            save_button = ctk.CTkButton(
                control_frame,
                text="Save Chart",
                font=ctk.CTkFont(size=14),
                width=120,
                height=32,
                command=self.save_chart
            )
            save_button.pack(side="right", padx=5)
            
        except Exception as e:
            messagebox.showerror("Analytics Error", f"Failed to update analytics: {str(e)}")
            # إعادة النص الإرشادي في حالة الخطأ
            self.analytics_label = ctk.CTkLabel(
                self.analytics_frame,
                text="Failed to generate analytics. Please try again.",
                text_color="red"
            )
            self.analytics_label.pack(pady=50)
    
    def save_chart(self):
        if self.fig:
            filename = f"ticket_analytics_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.fig.savefig(filename)
            messagebox.showinfo("Saved", f"Chart saved as {filename}")
    
    def create_history_tab(self):
        # إنشاء الإطار الرئيسي
        main_frame = ctk.CTkFrame(self.tab_history)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # إضافة عنوان
        title_label = ctk.CTkLabel(main_frame, 
                                 text="Calculation History",
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # إنشاء إطار للجدول
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True, pady=10)
        
        # تكوين الشبكة للجدول
        table_frame.grid_columnconfigure(0, weight=2)  # Date
        table_frame.grid_columnconfigure(1, weight=2)  # Prices
        table_frame.grid_columnconfigure(2, weight=1)  # Tickets
        table_frame.grid_columnconfigure(3, weight=1)  # Revenue
        table_frame.grid_columnconfigure(4, weight=1)  # Method
        table_frame.grid_columnconfigure(5, weight=1)  # Duration
        
        # إنشاء رؤوس الأعمدة
        headers = ["Date", "Prices", "Tickets", "Revenue", "Method", "Duration"]
        header_style = {
            "font": ctk.CTkFont(size=14, weight="bold"),
            "height": 35,
            "width": 150  # تحديد عرض ثابت للعناوين
        }
        
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(table_frame, text=header, **header_style)
            label.grid(row=0, column=col, padx=2, pady=(0, 5), sticky="nsew")
        
        # إنشاء إطار للبيانات مع شريط التمرير
        data_frame = ctk.CTkScrollableFrame(table_frame)
        data_frame.grid(row=1, column=0, columnspan=6, sticky="nsew", padx=2, pady=5)
        table_frame.grid_rowconfigure(1, weight=1)
        
        # تكوين أعمدة إطار البيانات
        for i in range(6):
            data_frame.grid_columnconfigure(i, weight=1, minsize=150)  # تحديد الحد الأدنى للعرض
        
        # حفظ مرجع لإطار البيانات
        self.history_data_frame = data_frame
        
        # إطار للأزرار
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        # أزرار التحكم
        button_style = {
            "font": ctk.CTkFont(size=13),
            "width": 120,
            "height": 32
        }
        
        refresh_btn = ctk.CTkButton(btn_frame, text="Refresh", 
                                  command=self.load_history_data,
                                  **button_style)
        refresh_btn.pack(side="left", padx=5)
        
        export_btn = ctk.CTkButton(btn_frame, text="Export Excel", 
                                 command=self.export_to_excel,
                                 **button_style)
        export_btn.pack(side="left", padx=5)
        
        clear_btn = ctk.CTkButton(btn_frame, text="Clear History", 
                                command=self.clear_history,
                                **button_style)
        clear_btn.pack(side="left", padx=5)
        
        # تحميل البيانات الأولية
        self.load_history_data()
    
    def create_settings_tab(self):
        frame = ctk.CTkFrame(self.tab_settings)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # إضافة عنوان
        title_label = ctk.CTkLabel(
            frame,
            text="Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # إطار الإعدادات
        settings_frame = ctk.CTkFrame(frame)
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        # إعدادات المظهر
        appearance_label = ctk.CTkLabel(
            settings_frame,
            text="Appearance Settings:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        appearance_label.pack(fill="x", padx=15, pady=(15, 5))
        
        self.appearance_mode = ctk.StringVar(value=ctk.get_appearance_mode().lower())
        appearance_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["light", "dark", "system"],
            command=self.change_appearance_mode,
            variable=self.appearance_mode,
            width=200,
            height=32,
            dynamic_resizing=False
        )
        appearance_menu.pack(padx=15, pady=(0, 15))
        
        # خط فاصل
        separator1 = ctk.CTkFrame(settings_frame, height=2)
        separator1.pack(fill="x", padx=15, pady=10)
        
        # إعدادات الصوت
        sound_label = ctk.CTkLabel(
            settings_frame,
            text="Sound Settings:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        sound_label.pack(fill="x", padx=15, pady=5)
        
        self.sound_var = ctk.BooleanVar(value=True)
        sound_checkbox = ctk.CTkCheckBox(
            settings_frame,
            text="Enable Sounds",
            variable=self.sound_var,
            font=ctk.CTkFont(size=14),
            checkbox_width=24,
            checkbox_height=24
        )
        sound_checkbox.pack(padx=15, pady=(0, 15))
        
        # خط فاصل
        separator2 = ctk.CTkFrame(settings_frame, height=2)
        separator2.pack(fill="x", padx=15, pady=10)
        
        # معلومات التطبيق
        info_frame = ctk.CTkFrame(settings_frame)
        info_frame.pack(fill="x", padx=15, pady=5)
        
        app_info_label = ctk.CTkLabel(
            info_frame,
            text="App Information:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        app_info_label.pack(fill="x", pady=5)
        
        version_label = ctk.CTkLabel(
            info_frame,
            text="App Version: 1.0.0",
            font=ctk.CTkFont(size=14)
        )
        version_label.pack(fill="x", pady=2)
        
        dev_label = ctk.CTkLabel(
            info_frame,
            text="Developed by: Your Team",
            font=ctk.CTkFont(size=14)
        )
        dev_label.pack(fill="x", pady=2)
    
    def play_sound(self, sound_type):
        if self.sound_var.get():
            if sound_type == "success":
                winsound.Beep(1000, 200)
            elif sound_type == "error":
                winsound.Beep(500, 300)
    
    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)
    
    def load_history_data(self):
        """تحميل البيانات التاريخية من قاعدة البيانات"""
        try:
            if not self.db_connection:
                self.initialize_database()
            
            # مسح البيانات القديمة
            for widget in self.history_data_frame.winfo_children():
                widget.destroy()
            
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM revenue_history ORDER BY date DESC")
            records = cursor.fetchall()
            
            if records:
                # نمط الخلايا
                cell_style = {
                    "font": ctk.CTkFont(family="Consolas", size=13),
                    "height": 30,
                    "width": 150,
                    "anchor": "center"
                }
                
                # إضافة البيانات
                for row_idx, record in enumerate(records):
                    # تنسيق البيانات
                    date = record[1]
                    prices = record[2]
                    tickets = str(record[3])
                    revenue = f"{record[4]:,}"
                    method = record[5]
                    duration = f"{record[6]:.2f}s"
                    
                    # إنشاء الخلايا
                    cells = [date, prices, tickets, revenue, method, duration]
                    for col_idx, cell_text in enumerate(cells):
                        cell = ctk.CTkLabel(
                            self.history_data_frame,
                            text=cell_text,
                            **cell_style
                        )
                        cell.grid(row=row_idx, column=col_idx, padx=2, pady=1, sticky="nsew")
            else:
                # رسالة عند عدم وجود بيانات
                no_data_label = ctk.CTkLabel(
                    self.history_data_frame,
                    text="No historical records available",
                    font=ctk.CTkFont(size=14),
                    height=40
                )
                no_data_label.grid(row=0, column=0, columnspan=6, padx=2, pady=10, sticky="nsew")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history: {str(e)}")
    
    def export_to_excel(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM revenue_history ORDER BY date DESC")
            records = cursor.fetchall()
            
            if records:
                df = pd.DataFrame(records, columns=["ID", "Date", "Prices", "Tickets", "Revenue", "Method", "Duration"])
                filename = f"ticket_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df.to_excel(filename, index=False)
                messagebox.showinfo("Exported", f"History exported to {filename}")
            else:
                messagebox.showwarning("No Data", "No records to export")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def clear_history(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete all historical records?"):
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("DELETE FROM revenue_history")
                self.db_connection.commit()
                self.load_history_data()
                messagebox.showinfo("Deleted", "All history records deleted")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete records: {str(e)}")
    
    def save_result(self):
        """حفظ نتيجة الحساب في قاعدة البيانات"""
        try:
            # جمع البيانات للحفظ
            prices = ",".join([entry.get() for entry in self.price_entries if entry.get().strip()])
            tickets = int(self.tickets_entry.get())
            method = self.algorithm_var.get()
            
            # استخدام قيمة الإيراد المحفوظة
            if hasattr(self, 'current_revenue'):
                revenue = self.current_revenue
            else:
                raise ValueError("No calculation results available")
            
            # إدخال البيانات في قاعدة البيانات
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO revenue_history 
                (date, prices, tickets, revenue, method, duration)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                prices,
                tickets,
                revenue,
                method,
                0.0  # قيمة افتراضية للمدة
            ))
            self.db_connection.commit()
            
            # تحديث عرض السجل التاريخي
            self.load_history_data()
            messagebox.showinfo("Success", "Result saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save result: {str(e)}")
    
    def cleanup(self, event=None):
        """تنظيف الموارد عند إغلاق التطبيق"""
        if event and event.widget != self:
            return
        
        try:
            # إلغاء جميع الأحداث المعلقة
            for widget in self.winfo_children():
                widget.after_cancel('all')
            
            # إغلاق قاعدة البيانات
            if hasattr(self, 'db_connection') and self.db_connection:
                try:
                    self.db_connection.close()
                except:
                    pass
            
            # إغلاق الرسوم البيانية
            if hasattr(self, 'fig') and self.fig:
                try:
                    plt.close(self.fig)
                except:
                    pass
            
            # إلغاء تسجيل الأحداث
            try:
                self.unbind('<Destroy>')
            except:
                pass
            
        except Exception as e:
            print(f"Cleanup error: {e}")

    def on_closing(self):
        """معالجة إغلاق النافذة"""
        if hasattr(self, '_is_closing') and self._is_closing:
            return
        
        self._is_closing = True
        
        try:
            # إيقاف أي عمليات جارية
            if hasattr(self, 'progress_bar'):
                try:
                    self.progress_bar.stop()
                except:
                    pass
            
            # تنظيف الموارد
            self.cleanup()
            
            # إغلاق النافذة
            try:
                self.quit()
            except:
                pass
            finally:
                self.destroy()
            
        except Exception as e:
            print(f"Error during closing: {e}")
            try:
                self.destroy()
            except:
                pass

    def clear_fields(self):
        # Clear price entry fields
        for entry in self.price_entries:
            entry.delete(0, 'end')
        
        # Clear ticket entry field
        self.tickets_entry.delete(0, 'end')
        
        # Reset result display
        self.main_result_entry.configure(text="")
        self.main_prices_label.configure(text="Prices: -")
        self.main_tickets_label.configure(text="Number of Tickets: -")
        self.main_algo_label.configure(text="Algorithm: -")
        self.main_time_label.configure(text="Time: -")

    def create_results_tab(self):
        # الإطار الرئيسي
        main_frame = ctk.CTkFrame(self.tab_results)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # عنوان النتائج
        title_label = ctk.CTkLabel(
            main_frame,
            text="Calculation Results",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # إطار النتيجة الرئيسية
        self.result_frame = ctk.CTkFrame(main_frame)
        self.result_frame.pack(fill="x", padx=30, pady=10)
        
        # عنوان النتيجة
        result_label = ctk.CTkLabel(
            self.result_frame,
            text="Maximum Revenue",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        result_label.pack(pady=10)
        
        # حقل النتيجة
        self.main_result_entry = ctk.CTkEntry(
            self.result_frame,
            font=ctk.CTkFont(size=48, weight="bold"),
            height=100,
            justify="center",
            state="readonly",
            text_color="#2ECC71"
        )
        self.main_result_entry.pack(pady=(5, 20), padx=40, fill="x")
        self.main_result_entry.insert(0, "0")
        
        # إطار التفاصيل
        details_frame = ctk.CTkFrame(main_frame)
        details_frame.pack(fill="x", padx=30, pady=20)
        
        # عنوان التفاصيل
        details_title = ctk.CTkLabel(
            details_frame,
            text="Calculation Details",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        details_title.pack(pady=10)
        
        # العمود الأيسر للتفاصيل
        left_details = ctk.CTkFrame(details_frame, fg_color="transparent")
        left_details.pack(side="left", fill="x", expand=True, padx=20)
        
        self.main_prices_label = ctk.CTkLabel(
            left_details,
            text="Prices: -",
            font=ctk.CTkFont(size=16),
            anchor="w"
        )
        self.main_prices_label.pack(fill="x", pady=5)
        
        self.main_tickets_label = ctk.CTkLabel(
            left_details,
            text="Number of Tickets: -",
            font=ctk.CTkFont(size=16),
            anchor="w"
        )
        self.main_tickets_label.pack(fill="x", pady=5)
        
        # العمود الأيمن للتفاصيل
        right_details = ctk.CTkFrame(details_frame, fg_color="transparent")
        right_details.pack(side="right", fill="x", expand=True, padx=20)
        
        self.main_algo_label = ctk.CTkLabel(
            right_details,
            text="Algorithm: -",
            font=ctk.CTkFont(size=16),
            anchor="w"
        )
        self.main_algo_label.pack(fill="x", pady=5)
        
        self.main_time_label = ctk.CTkLabel(
            right_details,
            text="Time: -",
            font=ctk.CTkFont(size=16),
            anchor="w"
        )
        self.main_time_label.pack(fill="x", pady=5)
        
        # إطار تحليل الخوارزمية
        algo_frame = ctk.CTkFrame(main_frame)
        algo_frame.pack(fill="x", padx=30, pady=20)
        
        # عنوان تحليل الخوارزمية
        algo_title = ctk.CTkLabel(
            algo_frame,
            text="Algorithm Analysis",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        algo_title.pack(pady=10)
        
        # إطار التعقيد
        complexity_frame = ctk.CTkFrame(algo_frame, fg_color="transparent")
        complexity_frame.pack(fill="x", padx=20, pady=5)
        
        # تعقيد الوقت والمساحة
        self.main_time_complexity_label = ctk.CTkLabel(
            complexity_frame,
            text="Time Complexity: -",
            font=ctk.CTkFont(size=16),
            anchor="w"
        )
        self.main_time_complexity_label.pack(fill="x", pady=5)
        
        self.main_space_complexity_label = ctk.CTkLabel(
            complexity_frame,
            text="Space Complexity: -",
            font=ctk.CTkFont(size=16),
            anchor="w"
        )
        self.main_space_complexity_label.pack(fill="x", pady=5)
        
        # إطار خطوات الخوارزمية
        steps_frame = ctk.CTkFrame(algo_frame)
        steps_frame.pack(fill="x", padx=20, pady=10)
        
        steps_title = ctk.CTkLabel(
            steps_frame,
            text="Algorithm Steps",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        steps_title.pack(pady=5)
        
        self.main_steps_label = ctk.CTkLabel(
            steps_frame,
            text="-",
            font=ctk.CTkFont(size=14),
            wraplength=800,
            justify="left"
        )
        self.main_steps_label.pack(fill="x", pady=5, padx=10)
        
        # إطار الأزرار
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=30)
        
        # زر حفظ النتائج
        save_button = ctk.CTkButton(
            button_frame,
            text="Save Results 💾",
            font=ctk.CTkFont(size=20, weight="bold"),
            height=60,
            width=300,
            fg_color="#3498DB",
            hover_color="#2980B9",
            command=self.save_result
        )
        save_button.pack(pady=10)
        
        # زر مسح النتائج
        clear_button = ctk.CTkButton(
            button_frame,
            text="Clear Results ⌫",
            font=ctk.CTkFont(size=20, weight="bold"),
            height=60,
            width=300,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            command=self.clear_fields
        )
        clear_button.pack(pady=10)

if __name__ == "__main__":
    try:
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        app = TicketRevenueApp()
        app.mainloop()
        
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        try:
            # التأكد من إغلاق جميع النوافذ المتبقية
            plt.close('all')
        except:
            pass