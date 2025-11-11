from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "change_this_secret_in_production"

DB = "database.db"

def connect_db():
    return sqlite3.connect(DB)

def init_db():
    conn = connect_db()
    cur = conn.cursor()
    
    # ساخت جداول
    cur.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            class_id INTEGER,
            voted INTEGER DEFAULT 0,
            UNIQUE(name, class_id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            candidate_id INTEGER
        )
    """)

    # اضافه کردن کلاس‌ها
    cur.execute("SELECT COUNT(*) FROM classes")
    if cur.fetchone()[0] == 0:
        classes = ["110","111","112","113","210","211","310","311","312"]
        for c in classes:
            cur.execute("INSERT INTO classes(name) VALUES(?)", (c,))

    # دانش‌آموزان هر کلاس
    classes_students = {
        "110": [
            "محمد عباس ارباب پوری","آیو برزن آرشپور","بهنیا باقلی","امیر محمد بزم آرا",
            "علیرضا بهزادی","محمد بهمنی","مارین تافته","شاهین جاویده",
            "آرین جلیلیان","کمیل جمشیدی","سید علی خاموشی","محمد طاها خزایی",
            "دانیال دیرکی","کیسان رادورزنگنه","محمد پارسا زارعی","آریا شهلایی",
            "محمد پارسا شیخه","محمد مبین صفری","امیرحسین عبدی","محمد حسین فرهادی",
            "ارشیا فرهنگیان","محمد قبادی صفت","ماهان قربان پور","متین قهرمانی",
            "پدرام کلهری","بردیا محمد یاری","پوریا نصیری","نیما نوروزی‌زاده",
            "پویان نوری","بردیا یوسف شاهی"
        ],
        "111": [
            "سبحان افراه","امیرعلی افکاری","امیر محمد الفتی","رضا امجدیان",
            "رهام امیری","امیرحسین امیریان","امیرحسین باوندپور","فربد بشیرزاده",
            "ماهان بهرامی","محمدرضا پگاه","رامتین جعفری","سینا حیدری",
            "رضا داوری","محمد جواد رفیعی","محمد طاها روشن","ارشیا زابلی",
            "آرش شیخیان","سهیل صید محمدی","سید سپهر طیاری","حسام قادری",
            "محمدعلی قنبری","کوروش قنبری","طاها کامیابی","نیما لطفی",
            "آرین محسن پور","حسین مرادی","امیدرضا نادری","ابوالفضل نصرتی",
            "امیررضا هوکری"
        ],
        "112": [
            "امیر محمد القاصی","امیرحسین امامی","ماهان امیدیان","ارشیا امیری",
            "برسام امیری","ماهان بداغی","مهدی بهرامی","محمد پارسا جوزی",
            "محمد جواد جهانبخشی","امیرحسین حاتمی","سید نیما حسینی","اهورا حیدری",
            "محمد طاها رازیانی","علی رجب‌پور","آرتین رستمی","امیررضا رضایی",
            "آریا زارعی","حسام سوری","علیرضا شهابی منش","پارسا صادقی",
            "سید ابوالفضل صفاری","شاهرخ غفاری","امیر محمد غلامی","ایلیا فرجی",
            "سروش فلاحی","امیرعلی کسرایی","آرمان گودرزی","امیرحسین گومه",
            "سید علیرضا موسوی","سهیل نظری","علوی ویسی","اشکان یاوری",
            "پارسا یاوری"
        ],
        "113": [
            "امیرعلی ابدالی","اروین اکبری","محمد رسول اکبری","محمدعلی بهبد",
            "امیرعلی بیرامی","سیروان جلیلی","محمد مهدی جلیلیان","محمد مهدی جمعه‌زاده",
            "علیرضا خادمی","علی خزایی","حسین خزایی","امیررضا دانش ور",
            "محمد دلفانی پور","محمد مهدی رشتیانی","ابوالفضل طاهری","امیرعلی طاهریان",
            "محمد پارسا عبدلی","مهدي عزیزی","صادق عزیزی","رضا غلامی",
            "محمد ماهان قرباقستانی","علیرضا کرمی","امیر عباس کنجوری","امیررضا گنجی",
            "اهورا متین","متین محبی","محمد سپهر مرادی","محمد طاها مرادی",
            "رهام میرشکار","ابوالفضل نجفی"
        ],
        "210": [
            "محمد مهدی احمدخانی","امیرعلی امیرخانی","محمد طاها امیری","رامتین امیریان",
            "امیرعلی حیدری","سهیل حیدریان","محمد امین خورشیدی","صدرا رحمانی",
            "کسرا رحمانی","محمد سام رضایی","محمد رهام سعیدی","محمد سینا صالحی",
            "امیر محمد عظیمی","محمد پارسا عیوضی","امیر محمد قاسمی","کسرا کرمی",
            "صدرا کرمی","رضا مجرد","امیر محمد مرادی","پرهام محمدی",
            "امیر محمد ملکی","محمد منتظریان","محمدرضا نوری","امیر یعقوب نیا"
        ],
        "211": [
            "محمد پارسا آزادی","شاهین احمدی","امیر عباس باباخانی","محمد صالح پاشایی",
            "امیر محمد پیری","ایلیا حاتمی","امیر محمد حیدریان","محراب دارابی فر",
            "ایلیا سبحانی","مارتیا سلطانقلی","ماهان سلیمانی","معین صالحی",
            "متین صالحی افشار","امیر محمد صفری","مهیار صفری","یوسف عزیزی",
            "محمد جواد فخری","عباس لطفی","امیر محمدی گلدسته","احسان محمدی نیک",
            "امیرعلی مروتی","کیا ناصری","محمد مهدی نجاتی","سید مهدی نوری",
            "امیرعلی وحیدی","یزدان همت پور","امیرحسین یزدانی"
        ],
        "310": [
            "آریا آزاده ده عباسانی","محمد جواد افسری نظر آبادی","محمد صالح اکبری",
            "امیر محمد امیری","حسین بشارتی","حسام پژوهنده","سید علیرضا جعفری سمنگانی",
            "ابولفضل حسینی","پارسا خزانی","پارسا خنجری","ایلیا روشنی سید حسینی",
            "محمدطه سرخوش","پوریا سلیمانی","محمد سهرابی","آرین شاه گل",
            "محمد جواد صیدی","رضا طاهری","مهراب عزیزی مرزاله","رضا فرهادی",
            "امید فربد ستا","امیررضا فلاحی","محمدطه کردبهمنی","علیرضا مرادی",
            "آرین معمار باش","ابوالفضل نوربخش","آرشام همتی","محمد یزدانی",
            "محمد حسام ویسی","علیرضا کیهانی"
        ],
        "311": [
            "سروش احمدی","محمد پارسا احمدی","رامتین اکبری","امیررضا باتمانی",
            "حسین چگوند","سینا حسنی","ابوالفضل خانی","محمد مهدی خسروی",
            "ماهان خورسندی","امیرعلی دهقانی","سینا سلیمی","محمد جواد صادقی",
            "امیرعلی صادقی","بنیامین صفری","محمد پارسا ضیایی","امیرحسین فتحی",
            "اشکان فیلی","ارشیا کولانی","اهورا کوه گرد","علیرضا محمودی",
            "امیر محمد مرادی","محمد مهدی مرزبانی"
        ],
        "312": [
            "امیر محمد آقایی","حسام اشرف آبادی","مهدی بابک فرد","آرشام باقری",
            "امیر محمد بشیری","طاها بهرامی","محمد طاها تاتاری","محمد مهدی حشمتی",
            "امیر عباس خمیس آبادی","محمدرضا ذهابی","محمد سینا رجبی","رضا رشتیانی",
            "امیررضا رضایی نیا","آرین سهرابی","محمد آرین سیابانی","پارسا صفرپور",
            "امیرحسین صفری","محمد سبحان صیادی","امیر حسام عزیزی","شایان فاضلی",
            "سپهر فرخ روز","ابوالفضل قاسمی","امیرحسین کماسی","امیر محمد کولانی",
            "امیرحسین محتشم پور","امیررضا محمدی","علی محمودی","محمد طاها مرادیان",
            "سید حمیدرضا موسوی","سامان میر عزیزی","پارسا ویسی","امیر محمد یاسی"
        ]
    }

    # اضافه کردن دانش‌آموزان به دیتابیس
    for class_name, students in classes_students.items():
        cur.execute("SELECT id FROM classes WHERE name=?", (class_name,))
        class_row = cur.fetchone()
        if class_row:
            class_id = class_row[0]
            cur.execute("SELECT COUNT(*) FROM students WHERE class_id=?", (class_id,))
            if cur.fetchone()[0] == 0:
                for s in students:
                    cur.execute("INSERT INTO students(name, class_id) VALUES(?,?)", (s, class_id))

    conn.commit()
    conn.close()

# 🟢 --- سیستم انتخاب تم --- 🟢
@app.route("/set_theme/<mode>")
def set_theme(mode):
    if mode in ["glass", "fast"]:
        session["theme"] = mode
    return redirect(request.referrer or url_for("home"))

# روت‌ها
@app.route("/")
def home():
    theme = session.get("theme", "glass")
    return render_template("home.html", theme=theme)

@app.route("/classes")
def select_class():
    theme = session.get("theme", "glass")
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM classes ORDER BY name")
    classes = cur.fetchall()
    conn.close()
    return render_template("select_class.html", classes=classes, theme=theme)

@app.route("/class/<int:class_id>")
def students_list(class_id):
    theme = session.get("theme", "glass")
    search = request.args.get("search", "").strip()
    conn = connect_db()
    cur = conn.cursor()
    if search:
        cur.execute("""
            SELECT id, name, voted FROM students
            WHERE class_id = ? AND name LIKE ?
            ORDER BY name
        """, (class_id, f"%{search}%"))
    else:
        cur.execute("SELECT id, name, voted FROM students WHERE class_id=? ORDER BY name", (class_id,))
    students = cur.fetchall()
    cur.execute("SELECT name FROM classes WHERE id=?", (class_id,))
    cls = cur.fetchone()
    class_name = cls[0] if cls else ""
    conn.close()
    return render_template("students_list.html",
                           students=students,
                           class_id=class_id,
                           class_name=class_name,
                           search=search,
                           theme=theme)

@app.route("/vote/<int:class_id>/<int:student_id>", methods=["GET","POST"])
def vote(class_id, student_id):
    theme = session.get("theme", "glass")
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, voted FROM students WHERE id=? AND class_id=?", (student_id, class_id))
    student = cur.fetchone()
    if not student:
        conn.close()
        flash("دانش‌آموز پیدا نشد.", "error")
        return redirect(url_for("students_list", class_id=class_id))
    if request.method == "POST":
        if student[2] == 1:
            conn.close()
            flash("این دانش‌آموز قبلاً رأی داده است.", "warning")
            return redirect(url_for("students_list", class_id=class_id))
        
        candidate_ids = request.form.getlist("candidates")
        if not candidate_ids:
            flash("حداقل یک کاندید انتخاب کنید.", "error")
            cur.execute("SELECT id, name FROM candidates ORDER BY name")
            candidates = cur.fetchall()
            conn.close()
            return render_template("vote.html", student=student, candidates=candidates, class_id=class_id, theme=theme)
        
        for cid in candidate_ids:
            cur.execute("INSERT INTO votes(student_id, candidate_id) VALUES(?,?)", (student_id, cid))
        
        cur.execute("UPDATE students SET voted=1 WHERE id=?", (student_id,))
        conn.commit()
        conn.close()
        flash(f"رأی برای {student[1]} ثبت شد ✅", "success")
        return redirect(url_for("students_list", class_id=class_id))
    
    cur.execute("SELECT id, name FROM candidates ORDER BY name")
    candidates = cur.fetchall()
    conn.close()
    return render_template("vote.html", student=student, candidates=candidates, class_id=class_id, theme=theme)

@app.route("/admin")
def admin_panel():
    theme = session.get("theme", "glass")
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM candidates ORDER BY name")
    candidates = cur.fetchall()
    cur.execute("""
        SELECT candidates.id, candidates.name, COUNT(votes.id) as cnt
        FROM candidates
        LEFT JOIN votes ON candidates.id = votes.candidate_id
        GROUP BY candidates.id
        ORDER BY cnt DESC, candidates.name
    """)
    results = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM students WHERE voted=1")
    voted_students = cur.fetchone()[0]
    conn.close()
    return render_template("admin_panel.html", candidates=candidates, results=results,
                           total_students=total_students, voted_students=voted_students, theme=theme)

@app.route("/admin/print_results")
def print_results():
    theme = session.get("theme", "glass")
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT candidates.name, COUNT(votes.id) as vote_count
        FROM candidates
        LEFT JOIN votes ON candidates.id = votes.candidate_id
        GROUP BY candidates.id
        ORDER BY vote_count DESC, candidates.name
    """)
    results = cur.fetchall()
    conn.close()
    return render_template("print_results.html", results=results, theme=theme)

@app.route("/admin/add_candidate", methods=["GET","POST"])
def add_candidate():
    theme = session.get("theme", "glass")
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("نام کاندید را وارد کنید.", "error")
            return redirect(url_for("add_candidate"))
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO candidates(name) VALUES(?)", (name,))
            conn.commit()
            flash("کاندید اضافه شد.", "success")
        except sqlite3.IntegrityError:
            flash("کاندیدی با این نام وجود دارد.", "warning")
        conn.close()
        return redirect(url_for("admin_panel"))
    return render_template("add_candidate.html", theme=theme)

@app.route("/admin/delete_candidate/<int:candidate_id>", methods=["POST"])
def delete_candidate(candidate_id):
    conn = connect_db()
    cur = conn.cursor()
    # حذف آرای مربوط به کاندید
    cur.execute("DELETE FROM votes WHERE candidate_id=?", (candidate_id,))
    # حذف خود کاندید
    cur.execute("DELETE FROM candidates WHERE id=?", (candidate_id,))
    conn.commit()
    conn.close()
    flash("کاندید و آرای مرتبط با آن حذف شدند.", "success")
    return redirect(url_for("admin_panel"))

@app.route("/admin/add_student/<int:class_id>", methods=["GET","POST"])
def add_student(class_id):
    theme = session.get("theme", "glass")
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("نام دانش‌آموز را وارد کنید.", "error")
            return redirect(url_for("add_student", class_id=class_id))
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO students(name, class_id) VALUES(?,?)", (name, class_id))
            conn.commit()
            flash("دانش‌آموز اضافه شد.", "success")
        except sqlite3.IntegrityError:
            flash("این دانش‌آموز قبلاً در این کلاس ثبت شده است.", "warning")
        conn.close()
        return redirect(url_for("students_list", class_id=class_id))
    return render_template("add_student.html", class_id=class_id, theme=theme)

@app.route("/admin/reset_votes", methods=["POST"])
def reset_votes():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM votes")
    cur.execute("UPDATE students SET voted=0")
    conn.commit()
    conn.close()
    flash("همهٔ آرای ذخیره شده بازنشانی شدند.", "success")
    return redirect(url_for("admin_panel"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
