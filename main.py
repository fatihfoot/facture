import flet as ft
import datetime
import sqlite3

# دالة لإنشاء قاعدة البيانات والجدول
def create_db():
    with sqlite3.connect('records.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                name TEXT NOT NULL,
                amount INTEGER NOT NULL
            )
        ''')
        conn.commit()

# دالة لإضافة السجل إلى قاعدة البيانات
def add_to_db(date, name, amount):
    with sqlite3.connect('records.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO records (date, name, amount)
            VALUES (?, ?, ?)
        ''', (date, name, amount))
        conn.commit()

# دالة لاسترجاع العناصر من قاعدة البيانات المرتبطة بتاريخ معين
def get_items_by_date(date):
    with sqlite3.connect('records.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, amount FROM records WHERE date = ?
        ''', (date,))
        return cursor.fetchall()

# دالة لحساب المجموع الكلي لجميع الأرقام المدخلة في قاعدة البيانات
def calculate_total():
    with sqlite3.connect('records.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(amount) FROM records
        ''')
        total = cursor.fetchone()[0]  # الحصول على المجموع
        return total if total else 0  # إذا لم تكن هناك عناصر، إرجاع 0

# دالة لتحديث التاريخ المعروض على الصفحة
def update_date(page, date_label, date):
    date_label.value = date.strftime("%Y-%m-%d")  # عرض التاريخ بشكل صحيح
    page.update()

# دالة لإضافة يوم إلى التاريخ
def add_day(page, date_label, current_date):
    new_date = current_date + datetime.timedelta(days=1)
    update_date(page, date_label, new_date)  # تحديث التاريخ
    return new_date  # إعادة التاريخ الجديد

# دالة لإنقاص يوم من التاريخ
def subtract_day(page, date_label, current_date):
    new_date = current_date - datetime.timedelta(days=1)
    update_date(page, date_label, new_date)  # تحديث التاريخ
    return new_date  # إعادة التاريخ الجديد

def main(page: ft.Page):
    page.scroll = "auto"
    page.window_width = 375
    page.window_height = 600
    page.window_left = 1200
    page.window_top = 140
    page.padding = 20
    page.horizontal_alignment = "center"

    # إنشاء قاعدة البيانات إذا لم تكن موجودة
    create_db()

    # إنشاء حقل الإدخال
    input_field = ft.TextField(label="الاسم الكامل")
    input_field2 = ft.TextField(label=" المبلغ المرسل اليه")
    items_list = ft.Column(width="auto")

    # دالة لتحميل العناصر من قاعدة البيانات وعرضها حسب التاريخ
    def load_items():
        items_list.controls.clear()  # مسح العناصر القديمة
        items = get_items_by_date(date_label.value)
        for name, amount in items:
            icon_show = ft.Icon(ft.icons.ARROW_BACK_OUTLINED, color="white")
            buton_dh = ft.Text(f'{amount} DH ', color="white", size=18)
            delete_button = ft.IconButton(icon=ft.icons.DELETE, icon_color="red", on_click=lambda e, text=name: on_delete_click(text))

            item_container = ft.Container(
                content=ft.Row(
                    controls=[buton_dh, icon_show, ft.Text(f'{name}', color="white", size=18), delete_button],
                    scroll=ft.ScrollMode.AUTO, alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=10, margin=5, border_radius=10, bgcolor="blue",
                border=ft.border.all(2, ft.colors.BLUE), width="auto", height="auto",
            )
            items_list.controls.append(item_container)

        # تحديث المجموع الكلي لجميع العناصر في قاعدة البيانات
        total = calculate_total()
        total_label.value = f"المجموع الكلي: {total} DH"
        page.update()
    
    # دالة لإضافة عنصر جديد إلى قاعدة البيانات
    def on_add_click(e):
        def check_num(e):
            if item_text != int:
                input_field2.error_text = "jhj"
        
            page.update()
        item_text = f'{input_field.value}'
        item_text2 = f'{input_field2.value}'

        if item_text and item_text2.isdigit():
            # إضافة السجل إلى قاعدة البيانات مع التاريخ الحالي
            current_date = date_label.value
            add_to_db(current_date, item_text, int(item_text2))

            # تحديث قائمة العناصر
            load_items()

            # مسح حقل الإدخال بعد الإضافة
            input_field2.value = ""
            input_field.value = ""
            page.update()

    # دالة لحذف العنصر عند الضغط على زر "حذف"
    def on_delete_click(item_text):
        with sqlite3.connect('records.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM records WHERE name = ?
            ''', (item_text,))
            conn.commit()

        # تحديث قائمة العناصر بعد الحذف
        load_items()

    # دالة لتحديث التاريخ إلى اليوم الحالي
    current_date = datetime.date.today()

    def on_refresh_button_click(e):
        nonlocal current_date
        current_date = datetime.date.today()  # إعادة التاريخ إلى اليوم الحالي
        update_date(page, date_label, current_date)
        load_items()  # تحميل العناصر المرتبطة بالتاريخ الحالي

    # إنشاء مربع النص لعرض التاريخ (يتم تعيين التاريخ الحالي مباشرة هنا)
    date_label = ft.Text(value=current_date.strftime("%Y-%m-%d"), size=24, text_align="center")

    # أزرار إضافة وإنقاص الأيام
    def on_add_button_click(e):
        nonlocal current_date
        current_date = add_day(page, date_label, current_date)
        load_items()  # تحميل العناصر المرتبطة بالتاريخ الجديد

    def on_subtract_button_click(e):
        nonlocal current_date
        current_date = subtract_day(page, date_label, current_date)
        load_items()  # تحميل العناصر المرتبطة بالتاريخ الجديد

    add_button = ft.IconButton(icon=ft.icons.ADD, icon_size=30, on_click=on_add_button_click)
    subtract_button = ft.IconButton(icon=ft.icons.REMOVE, icon_size=30, on_click=on_subtract_button_click)

    # تنسيق الوقت (التاريخ)
    time = ft.Row(
        [
            subtract_button,  # زر تقليص اليوم
            ft.Container(date_label, width=200, height=50, bgcolor="green", border_radius=10),
            add_button,  # زر إضافة يوم
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
    )

    # زر التحديث
    reload_time = ft.ElevatedButton("تحديث", style=ft.ButtonStyle(padding=1), on_click=on_refresh_button_click)

    # الشريط العلوي
    appbarr = ft.AppBar(
        title=ft.Text("تسجيل الدخول", color="white"),
        center_title=True,
        bgcolor="blue",
        actions=[ft.IconButton(ft.icons.SEARCH, icon_color="white")],
        leading=reload_time
    )

    add_button = ft.ElevatedButton("إضافة", on_click=on_add_click)

    # إضافة المحتوى إلى الصفحة
    page.add(appbarr, time, input_field, input_field2, add_button, items_list)

    # إضافة المجموع الكلي أسفل الصفحة
    global total_label
    total_label = ft.Text(value="المجموع الكلي: 0 DH", size=18, text_align="left", color="blue")
    page.add(total_label)

    page.update()

    # تحميل العناصر عند بداية التطبيق
    load_items()

ft.app(main)
