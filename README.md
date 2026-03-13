# Smart File Organizer

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

ระบบ Desktop สำหรับสแกนโฟลเดอร์และจัดระเบียบไฟล์อัตโนมัติเป็นหมวดหมู่ เช่น Images, Documents, Videos และ Code

พัฒนาด้วย **Python 3.10+** และ **PySide6** พร้อมการออกแบบที่เน้น **OOP + SOLID + Design Patterns**

---

## ข้อมูลทีม

| รายการ | รายละเอียด |
| ------ | ---------- |
| ชื่อทีม | Smart File Organizer |
| สมาชิก | นาย อัษฎาวุธ พันธ์สาลี |
| รหัสนักศึกษา | 68114540737 |
| หน้าที่รับผิดชอบ | ออกแบบและพัฒนาโปรแกรมทั้งหมด (UI, OOP/SOLID, ทดสอบระบบ) |

---

## คุณสมบัติหลัก

- เลือกโฟลเดอร์ผ่าน File Picker
- รองรับ Drag and Drop โฟลเดอร์เข้าสู่โปรแกรม
- สแกนไฟล์และแสดงผลสรุปตามหมวดหมู่
- จัดไฟล์อัตโนมัติไปยังโฟลเดอร์ย่อยตามประเภทไฟล์
- รีเซ็ตไฟล์จากโฟลเดอร์หมวดหมู่กลับโฟลเดอร์หลัก
- ป้องกันชื่อไฟล์ชนกันด้วยการเติม suffix อัตโนมัติ เช่น `_1`, `_2`

---

## Tech Stack

| Layer | Technology |
| ----- | ---------- |
| Language | Python 3.10+ |
| UI Framework | PySide6 |
| Architecture | OOP + SOLID |
| Patterns | Strategy Pattern, Factory Pattern |

---

## โครงสร้างโปรเจกต์

```text
smart-file-organizer/
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── organizer.py      # ประสานการทำงานหลัก Scan/Classify/Move/Reset
│   │   ├── scanner.py        # สแกนไฟล์ในโฟลเดอร์
│   │   └── mover.py          # ย้ายไฟล์และจัดการชื่อซ้ำ
│   ├── classifiers/
│   │   ├── base.py           # Base classifier (abstract)
│   │   ├── factory.py        # Factory สำหรับสร้าง classifiers
│   │   ├── image_classifier.py
│   │   ├── video_classifier.py
│   │   ├── document_classifier.py
│   │   ├── code_classifier.py
│   │   └── custom_classifier.py
│   └── ui/
│       ├── main_window.py    # หน้าจอหลัก
│       ├── widgets.py        # UI components
│       ├── worker.py         # QThread workers
│       └── styles.py         # QSS style
├── requirements.txt
├── pyproject.toml
├── README.md
└── main.py
```

---

## OOP และ Design

### Inheritance + Polymorphism

- `FileClassifier` เป็น abstract base class
- คลาสลูก (`ImageClassifier`, `VideoClassifier`, `DocumentClassifier`, `CodeClassifier`, `CustomClassifier`) override เมธอด `classify()`
- `FileOrganizer` เรียกใช้งาน classifier ผ่านอินเทอร์เฟซเดียวกัน

```python
for classifier in classifiers:
    category = classifier.classify(file_path)
```

### Composition

- `FileOrganizer` ประกอบด้วย `FileScanner`, `FileMover` และรายการ `FileClassifier`

### Encapsulation

- `FileMover` ซ่อน logic ภายในผ่านเมธอด `_create_folder()` และ `_ensure_unique_name()`

### Design Patterns

| Pattern | การใช้งานในโปรเจกต์ |
| ------- | ------------------- |
| Strategy Pattern | classifier แต่ละตัวรับผิดชอบการจำแนกไฟล์แต่ละประเภท |
| Factory Pattern | `ClassifierFactory.create()` สร้างรายการ classifier สำหรับใช้งาน |

---

## การประยุกต์ใช้ SOLID

| หลักการ | การใช้งานในโปรเจกต์ |
| ------- | ------------------- |
| S - Single Responsibility | `FileScanner` ทำหน้าที่สแกนไฟล์, `FileMover` ทำหน้าที่ย้ายไฟล์ |
| O - Open/Closed | เพิ่ม classifier ใหม่ได้โดยไม่ต้องแก้ flow หลักของ organizer |
| L - Liskov Substitution | คลาสลูกของ `FileClassifier` ใช้แทนกันได้ |
| I - Interface Segregation | เมธอดแยกหน้าที่ชัดเจน เช่น `scan`, `classify`, `move` |
| D - Dependency Inversion | `FileOrganizer` รองรับการ inject scanner/mover/classifiers |

---

## การติดตั้ง

### 1) Clone repository

```bash
git clone https://github.com/ubu-lab-atsadawut/Smart-File-Organizer.git
cd Smart-File-Organizer
```

### 2) สร้าง Virtual Environment (แนะนำ)

```bash
python -m venv .venv
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux / macOS (bash, zsh):

```bash
source .venv/bin/activate
```

### 3) ติดตั้ง dependencies

```bash
pip install -r requirements.txt
```

---

## วิธีรันโปรแกรม

```bash
python main.py
```

---

## ขั้นตอนการใช้งาน (Demo Flow)

1. เปิดโปรแกรมและเลือกโฟลเดอร์เป้าหมาย
2. กดปุ่ม **Scan Files** เพื่อดูไฟล์ตามหมวดหมู่
3. กดปุ่ม **Organize Files** เพื่อจัดไฟล์อัตโนมัติ
4. ตรวจสอบผลการจัดไฟล์ในโฟลเดอร์ย่อย
5. กดปุ่ม **Reset Files** เมื่อต้องการย้ายไฟล์กลับโฟลเดอร์หลัก

---

## เอกสารประกอบการส่งงาน

- Source code อยู่ใน repository นี้ครบถ้วน
- มีไฟล์ `README.md`, `requirements.txt`, `pyproject.toml`
- โครงการนี้พัฒนาขึ้นใหม่และแสดงการประยุกต์ใช้ OOP, SOLID และ Design Patterns อย่างชัดเจน

---

## VDO

[Watch Demo Video](https://drive.google.com/file/d/11oko_cs5V-L0hpAej9o1UW6KOqTfua1m/view?usp=sharing)

---