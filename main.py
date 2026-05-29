import customtkinter as ctk
import json
import os
import time
from datetime import date, timedelta
from database import Database
from vfx import play_sound

COLORS = ["#4285F4", "#0F9D58", "#F4B400", "#DB4437", "#AB47BC", "#00ACC1", "#FF7043", "#6C63FF"]

class TimerWindow(ctk.CTkToplevel):
    def __init__(self, parent, task, on_finish_callback):
        super().__init__(parent)
        self.title(f"جلسة تركيز: {task['name_ar']}")
        self.geometry("300x200")
        self.transient(parent)
        self.attributes("-topmost", True)
        self.start_time = time.time()
        self.running = True
        self.on_finish = on_finish_callback
        self.task = task
        
        self.lbl_time = ctk.CTkLabel(self, text="00:00:00", font=("Helvetica", 36, "bold"), text_color="#4ECDC4")
        self.lbl_time.pack(pady=30)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack()
        ctk.CTkButton(btn_frame, text="⏹️ إنهاء وتوثيق", fg_color="#DB4437", command=self.stop_and_log).pack(side="left", padx=5)
        self.update_timer()

    def update_timer(self):
        if self.running:
            elapsed = int(time.time() - self.start_time)
            h, rem = divmod(elapsed, 3600)
            m, s = divmod(rem, 60)
            self.lbl_time.configure(text=f"{h:02d}:{m:02d}:{s:02d}")
            self.after(1000, self.update_timer)

    def stop_and_log(self):
        self.running = False
        elapsed_sec = int(time.time() - self.start_time)
        hours = round(elapsed_sec / 3600.0, 2)
        play_sound("success")
        self.on_finish(self.task, max(0.01, hours))
        self.destroy()

class TaskFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.last_action = None
        self.title("SA.A.AT (Dashboard Edition)")
        ctk.set_appearance_mode("dark")
        self.geometry("1000x750")
        self.build_ui()

    def build_ui(self):
        for widget in self.winfo_children(): widget.destroy()
        
        # --- 1. Top Dashboard Cards ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        
        try:
            weekly_total = round(sum(dict(t).get("logged_this_week", 0) for t in self.db.get_weekly_summary()), 1)
        except:
            weekly_total = 0
            
        cards = [
            ("المتبقي هذا الأسبوع", f"{self.db.get_weekly_remaining()} ساعة", "#FF6B6B", "🎯"),
            ("إجمالي هذا الأسبوع", f"{weekly_total} ساعة", "#3DD9AC", "📊"),
            ("إجمالي الأرشيف", f"{self.db.get_total_hours()} ساعة", "#4ECDC4", "⏱️"),
            ("شعلة الاستمرار", f"{self.db.get_current_streak()} أيام", "#FFD700", "🔥")
        ]
        
        for title, val, color, icon in cards:
            card = ctk.CTkFrame(header, fg_color="#2B2B2B", corner_radius=10)
            card.pack(side="right", expand=True, fill="x", padx=10)
            ctk.CTkLabel(card, text=icon, font=("Arial", 24)).pack(pady=(10, 0))
            ctk.CTkLabel(card, text=val, font=("Arial", 18, "bold"), text_color=color).pack(pady=2)
            ctk.CTkLabel(card, text=title, font=("Arial", 12)).pack(pady=(0, 10))

        # --- End of Week Warning ---
        from datetime import datetime
        now = datetime.now()
        if now.weekday() == 3:  # 3 تعني يوم الخميس في لغة بايثون
            rem_hours = 24 - now.hour
            warning_frame = ctk.CTkFrame(self, fg_color="#8A2BE2", corner_radius=10)
            warning_frame.pack(fill="x", padx=20, pady=(0, 10))
            ctk.CTkLabel(warning_frame, text=f"⏳ بقي {rem_hours} ساعة على نهاية الأسبوع!!! 🐎 الخيل الأصيل يلحق تالي!", font=("Arial", 16, "bold"), text_color="white").pack(pady=10)

        # --- 2. Action Controls ---
        ctrl = ctk.CTkFrame(self, fg_color="transparent")
        ctrl.pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(ctrl, text="➕ مهمة جديدة", fg_color="#4285F4", width=120, command=self.add_task_dialog).pack(side="right", padx=5)
        ctk.CTkButton(ctrl, text="📋 من المنسوخ", fg_color="#AB47BC", width=120, command=self.paste_from_clipboard).pack(side="right", padx=5)
        ctk.CTkButton(ctrl, text="💾 تصدير الأرشيف", fg_color="#0F9D58", width=120, command=self.export_data).pack(side="left", padx=5)
        if self.last_action:
            ctk.CTkButton(ctrl, text="↩️ تراجع", fg_color="#DB4437", width=80, command=self.undo_action).pack(side="right", padx=5)

        # --- 3. Main Tabs ---
        self.tabs = ctk.CTkTabview(self, corner_radius=10)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tabs.add("المهام الحالية")
        debts = self.db.get_debts()
        if debts: self.tabs.add("صفحة الديون ⚠️")
        self.tabs.add("الإحصائيات المتقدمة")

        self.build_tasks_tab(self.tabs.tab("المهام الحالية"))
        if debts: self.build_debts_tab(self.tabs.tab("صفحة الديون ⚠️"), debts)
        self.build_stats_tab(self.tabs.tab("الإحصائيات المتقدمة"))

    def build_tasks_tab(self, parent):
        grid = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        tasks = self.db.get_weekly_summary()
        cols = 3
        for i, task in enumerate(tasks):
            r, c = divmod(i, cols)
            self.create_task_card(grid, task).grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
            grid.grid_columnconfigure(c, weight=1)

    def create_task_card(self, parent, task):
        card = ctk.CTkFrame(parent, border_width=2, border_color=task["color"], corner_radius=10)
        temp_badge = "⏳ مؤقت" if task["is_temp"] else "📌 دائم"
        logged = task['logged_all_time'] if task['is_temp'] else task['logged_this_week']
        progress = f"{logged:.1f} / {task['weekly_target_hrs']} س"
        
        h = ctk.CTkFrame(card, fg_color="transparent")
        h.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(h, text=task["name_ar"], font=("Arial", 16, "bold")).pack(side="right")
        ctk.CTkButton(h, text="⚙️", width=30, fg_color="transparent", command=lambda t=task: self.edit_task_dialog(t)).pack(side="left")
        
        ctk.CTkLabel(card, text=f"{temp_badge} | الإنجاز: {progress}", font=("Arial", 12)).pack(pady=5)
        
        bf = ctk.CTkFrame(card, fg_color="transparent")
        bf.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(bf, text="⏱️ جلسة", fg_color="#2B2B2B", command=lambda t=task: TimerWindow(self, t, self.handle_timer_finish)).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(bf, text="➕ تسجيل", fg_color=task["color"], command=lambda t=task: self.log_dialog(t, is_debt=False)).pack(side="right", expand=True, padx=2)
        return card

    def build_debts_tab(self, parent, debts):
        grid = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        for i, task in enumerate(debts):
            card = ctk.CTkFrame(grid, border_width=2, border_color="#DB4437", corner_radius=10)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            grid.grid_columnconfigure(i%3, weight=1)
            ctk.CTkLabel(card, text=task["name_ar"], font=("Arial", 16, "bold")).pack(pady=5)
            ctk.CTkLabel(card, text=f"الدين المتراكم: {task['debt_hours']:.1f} ساعة", text_color="#FF6B6B").pack(pady=5)
            ctk.CTkButton(card, text="💸 قضاء جزء", fg_color="#DB4437", command=lambda t=task: self.log_dialog(t, is_debt=True)).pack(pady=10)

    def build_stats_tab(self, parent):
        top_frame = ctk.CTkFrame(parent, fg_color="transparent")
        top_frame.pack(fill="x", pady=10)
        
        # 1. Bar Chart (Last 7 Days)
        chart_frame = ctk.CTkFrame(top_frame, fg_color="#2B2B2B", corner_radius=10)
        chart_frame.pack(side="right", expand=True, fill="both", padx=5)
        ctk.CTkLabel(chart_frame, text="نشاط آخر 7 أيام", font=("Arial", 14, "bold")).pack(pady=5)
        
        stats = self.db.get_last_7_days_stats()
        if stats:
            canvas = ctk.CTkCanvas(chart_frame, bg="#2B2B2B", highlightthickness=0, height=200)
            canvas.pack(fill="x", padx=10, pady=10)
            max_h = max(stats.values()) if stats else 1
            width, height, bar_w, gap = 400, 150, 40, 20
            x = 20
            for i in range(7):
                d = (date.today() - timedelta(days=6-i)).isoformat()
                val = stats.get(d, 0)
                bar_h = (val / max_h) * height if max_h > 0 else 0
                canvas.create_rectangle(x, height - bar_h + 10, x + bar_w, height + 10, fill="#4ECDC4", outline="")
                canvas.create_text(x + bar_w//2, height - bar_h, text=f"{val:.1f}", fill="white", font=("Arial", 10))
                canvas.create_text(x + bar_w//2, height + 25, text=d[-5:], fill="#A0A0A0", font=("Arial", 9))
                x += bar_w + gap
        else:
            ctk.CTkLabel(chart_frame, text="لا توجد بيانات كافية").pack(pady=50)

        # 2. Distribution Progress Bars (أين ذهبت الساعات؟)
        dist_frame = ctk.CTkFrame(top_frame, fg_color="#2B2B2B", corner_radius=10)
        dist_frame.pack(side="left", expand=True, fill="both", padx=5)
        ctk.CTkLabel(dist_frame, text="أين ذهبت معظم الساعات؟ (التوب 5)", font=("Arial", 14, "bold")).pack(pady=5)
        
        dist = self.db.get_task_distribution()
        if dist:
            max_total = max(t["total"] for t in dist)
            for d in dist:
                lbl_frame = ctk.CTkFrame(dist_frame, fg_color="transparent")
                lbl_frame.pack(fill="x", padx=15, pady=(5, 0))
                ctk.CTkLabel(lbl_frame, text=f"{d['total']:.1f} س", font=("Arial", 12)).pack(side="left")
                ctk.CTkLabel(lbl_frame, text=d['name'], font=("Arial", 12)).pack(side="right")
                
                pb = ctk.CTkProgressBar(dist_frame, progress_color=d["color"], fg_color="#1E1E1E", height=10)
                pb.pack(fill="x", padx=15, pady=(0, 10))
                pb.set(d["total"] / max_total if max_total > 0 else 0)
        else:
            ctk.CTkLabel(dist_frame, text="لا توجد مهام مسجلة").pack(pady=50)

    def log_dialog(self, task, is_debt=False):
        play_sound("click")
        d = ctk.CTkToplevel(self)
        d.title("تسجيل الساعات"); d.geometry("350x250"); d.transient(self)
        ctk.CTkLabel(d, text="عدد الساعات المنجزة:").pack(pady=5)
        hrs = ctk.CTkEntry(d); hrs.pack(pady=5)
        ctk.CTkLabel(d, text="تعليق / ملاحظة (اختياري):").pack(pady=5)
        note = ctk.CTkEntry(d, width=250); note.pack(pady=5)
        
        def submit():
            try:
                val = float(hrs.get())
                if is_debt: self.db.pay_debt(task["id"], val, note.get())
                else: 
                    res = self.db.log_hours(task["id"], val, note.get())
                    if res["just_completed"]: play_sound("milestone")
                play_sound("success")
                d.destroy(); self.build_ui()
            except ValueError: pass
        ctk.CTkButton(d, text="حفظ", command=submit).pack(pady=15)

    def handle_timer_finish(self, task, hours_elapsed):
        d = ctk.CTkToplevel(self)
        d.title("حفظ الجلسة"); d.geometry("350x200"); d.transient(self); d.attributes("-topmost", True)
        ctk.CTkLabel(d, text=f"تم تسجيل: {hours_elapsed:.2f} ساعة. أضف ملاحظتك:").pack(pady=10)
        note = ctk.CTkEntry(d, width=250); note.pack(pady=10)
        def save():
            play_sound("success")
            self.db.log_hours(task["id"], hours_elapsed, note.get())
            d.destroy(); self.build_ui()
        ctk.CTkButton(d, text="حفظ وتوثيق", command=save).pack(pady=10)

    def edit_task_dialog(self, task=None):
        play_sound("click")
        d = ctk.CTkToplevel(self)
        d.title("إعدادات المهمة"); d.geometry("400x400"); d.transient(self)
        ctk.CTkLabel(d, text="الاسم:").pack(pady=2)
        name_ar = ctk.CTkEntry(d, width=250); name_ar.insert(0, task["name_ar"] if task else "مهمة جديدة"); name_ar.pack(pady=5)
        ctk.CTkLabel(d, text="الهدف (ساعات):").pack(pady=2)
        target = ctk.CTkEntry(d); target.insert(0, str(task["weekly_target_hrs"]) if task else "5.0"); target.pack(pady=5)
        is_temp = ctk.CTkCheckBox(d, text="هدف مؤقت")
        if task and task["is_temp"]: is_temp.select()
        is_temp.pack(pady=10)
        
        def save():
            play_sound("click")
            if task: self.db.update_task(task["id"], name_ar.get(), name_ar.get(), float(target.get()), task["color"], is_temp.get())
            else: self.db.add_task(name_ar.get(), name_ar.get(), float(target.get()), COLORS[0], is_temp.get())
            d.destroy(); self.build_ui()
        def delete():
            play_sound("delete"); self.db.delete_task(task["id"]); self.last_action = {"type": "delete", "id": task["id"]}
            d.destroy(); self.build_ui()
            
        ctk.CTkButton(d, text="💾 حفظ", command=save).pack(pady=10)
        if task: ctk.CTkButton(d, text="🗑️ حذف", fg_color="#DB4437", command=delete).pack(pady=5)

    def add_task_dialog(self): self.edit_task_dialog(None)

    def paste_from_clipboard(self):
        try:
            data = json.loads(self.clipboard_get())
            ids = [self.db.add_task(t.get("en", "Task"), t.get("ar", "مهمة"), t.get("hrs", 1.0), t.get("color", COLORS[0]), 1 if t.get("temp") else 0) for t in data]
            self.last_action = {"type": "add_bulk", "ids": ids}
            play_sound("success"); self.build_ui()
        except Exception:
            play_sound("delete"); print("❌ خطأ بالمنسوخ.")

    def undo_action(self):
        play_sound("undo")
        if self.last_action["type"] == "delete": self.db.restore_task(self.last_action["id"])
        elif self.last_action["type"] == "add_bulk": [self.db.delete_task(tid) for tid in self.last_action["ids"]]
        self.last_action = None; self.build_ui()

    def export_data(self):
        play_sound("success")
        path = os.path.expanduser("~/Desktop/TaskFlow_Archive.csv")
        self.db.export_csv(path)
        os.system(f"open -R '{path}'")

if __name__ == "__main__":
    app = TaskFlowApp()
    app.mainloop()
