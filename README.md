# Smart File Organizer

โปรแกรม Desktop สำหรับสแกนโฟลเดอร์และจัดระเบียบไฟล์อัตโนมัติแยกตามหมวดหมู่

## ข้อมูลทีม

- ชื่อทีม: Smart File Organizer
- สมาชิก: นาย อัษฎาวุฑ พันธ์สาลี
- หน้าที่ความรับผิดชอบ: ออกแบบและพัฒนาโปรแกรม (UI, โครงสร้าง OOP/SOLID, ทดสอบการทำงาน)

## ความสามารถของโปรแกรม

- เลือกโฟลเดอร์ผ่านปุ่มเลือกไฟล์
- ลากและวางพาธโฟลเดอร์ลงในโปรแกรมได้
- สแกนไฟล์และแสดงสรุปตามหมวดหมู่
- จัดไฟล์ลงโฟลเดอร์ย่อย เช่น Images, Documents, Videos และ Code
- ย้ายไฟล์กลับจากโฟลเดอร์หมวดหมู่มายังโฟลเดอร์หลักได้ (Reset)
- ป้องกันชื่อไฟล์ชนกัน โดยเติม suffix เช่น _1, _2

## เทคโนโลยีที่ใช้

- Python 3.10+
- PySide6

## โครงสร้างโปรเจกต์

```text
smart-file-organizer/
  src/
    main.py
    core/
      organizer.py
      scanner.py
      mover.py
    classifiers/
      base.py
      factory.py
      image_classifier.py
      video_classifier.py
      document_classifier.py
      code_classifier.py
    ui/
      main_window.py
  requirements.txt
  pyproject.toml
  README.md
  main.py
```

## การออกแบบเชิงวัตถุ (OOP)

### Inheritance และ Polymorphism

- FileClassifier เป็นคลาสแม่ (base class)
- ImageClassifier, VideoClassifier, DocumentClassifier และ CodeClassifier ทำการ override เมธอด classify()
- FileOrganizer เรียกใช้งาน classifier ผ่านอินเทอร์เฟซเดียวกัน

```python
for classifier in classifiers:
    category = classifier.classify(file_path)
```

### Composition

FileOrganizer ประกอบด้วย scanner, mover และ classifier strategies

### Encapsulation

FileMover มีเมธอดภายในที่ซ่อนรายละเอียดการทำงาน เช่น _create_folder() และ _ensure_unique_name()

### Design Patterns

- Strategy Pattern: classifier แต่ละตัวทำหน้าที่เป็นกลยุทธ์การจำแนกไฟล์
- Factory Pattern: ClassifierFactory.create() ใช้สร้างรายการ classifier ที่ต้องใช้งาน

## การประยุกต์ใช้ SOLID

- S (Single Responsibility): FileScanner ทำหน้าที่เฉพาะการสแกนไฟล์
- O (Open/Closed): สามารถเพิ่ม classifier ใหม่ได้โดยไม่กระทบ flow หลัก
- L (Liskov Substitution): คลาสลูกแทนที่ FileClassifier ได้
- I (Interface Segregation): เมธอดมีหน้าที่เล็กและชัดเจน เช่น scan, classify, move
- D (Dependency Inversion): Organizer พึ่งพา abstraction และรองรับการ inject dependency

## วิธีติดตั้ง

```bash
pip install -r requirements.txt
```

## วิธีรันโปรแกรม

```bash
python main.py
```

## ขั้นตอนการเดโม

1. เลือกโฟลเดอร์เป้าหมาย (เช่น Downloads)
2. กดปุ่ม Scan Files
3. กดปุ่ม Organize Files
4. ไฟล์จะถูกย้ายไปโฟลเดอร์หมวดหมู่ เช่น Images, Documents, Videos, Code
5. กดปุ่ม Reset Files เพื่อย้ายไฟล์กลับจาก Images/Documents/Videos/Code/Others ไปยังโฟลเดอร์หลัก
