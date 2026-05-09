# Bulk Create SAC Teams from Excel

เครื่องมือนี้ใช้สำหรับอัปโหลด Excel workbook เพียงไฟล์เดียว แล้วสั่งงานจากหน้าแอป local เพื่อ:

- สร้าง Team
- assign Role ให้ Team
- assign existing user เข้า Team

ทั้งหมดจากหน้าเดียว

## สถานะ

เอกสารและ workflow ชุดนี้จัดไว้ตามสถานะของ repo ณ วันที่ **9 May 2026**

## จุดยืนของ repo นี้

repo นี้เป็น **implementation ของเราเอง**
และเป็น **free source-available toolkit** ไม่ใช่ open-source ตามนิยามทั่วไป เพราะ license ปัจจุบันยังจำกัดการใช้งานเชิงพาณิชย์

สิ่งที่ SAP รองรับในเอกสารที่ใช้อ้างอิงใน workspace นี้ คือแนวคิดฝั่ง SAC เช่น:

- จัดการ Teams จาก `Security > Teams`
- assign roles ให้ users และ teams
- สร้าง OAuth Clients จาก `System > Administration > App Integration`
- ใช้ `User Provisioning` สำหรับ access ที่เกี่ยวกับ SCIM

สิ่งที่ repo นี้ต่อยอดขึ้นมาเอง:

- รูปแบบ Excel workbook
- flow การประมวลผลด้วย Python
- หน้า Streamlit upload tool
- การกรอก config ผ่าน UI

## โครงไฟล์หลัก

```text
SAC_ROLE/
├── .streamlit/
│   └── config.toml
├── data/
│   └── sac_team_data.xlsx
├── app.py
├── sac_role_core.py
├── README.md
├── README_TH.md
├── LICENSE.md
├── config.ini.example
├── requirements.txt
├── run.command
├── run.bat
└── tests/
```

## โครงสร้าง Excel ที่รองรับ

แอปรับไฟล์ `.xlsx` ที่มี sheet และคอลัมน์ตามนี้

### `Create_Teams`

คอลัมน์ที่ต้องมี:

- `Team ID`
- `Team Description`

### `Assign_Roles`

คอลัมน์ที่ต้องมี:

- `TeamID`
- `RoleID`

### `Users`

คอลัมน์ที่ต้องมี:

- `UserName`
- `TeamID`

หมายเหตุ:

- `RoleID` จะถูกส่งตามที่กรอกใน Excel ตรงๆ
- `Assign_Roles` ใช้ได้ทั้งกับทีมที่สร้างในรอบนี้ และทีมที่มีอยู่แล้วใน SAC
- `Users` ใช้สำหรับ assign existing user เข้า Team เท่านั้น

## Clone -> Install -> Run

```bash
git clone <your-repo-url>
cd <repo-folder-name>
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

หรือจะ double-click:

- `run.command` บน macOS
- `run.bat` บน Windows

## วิธีใช้งาน

1. กด `Download Excel template` หากต้องการ template
2. อัปโหลดไฟล์ `.xlsx` ของคุณ
3. เปิด `Connection Settings`
4. กรอก:
   - `tenant_url`
   - `token_url`
   - `client_id`
   - `client_secret`
5. ถ้าต้องการจำค่าไว้ในเครื่อง กด `Save locally`
6. ถ้าต้องการดึงค่าที่เคยเซฟ กด `Load saved`
7. เลือก task จาก dropdown
8. กด `Run`

task ที่เลือกได้:

- `Validate & Preview`
- `Create Teams`
- `Assign Roles`
- `Assign Users`
- `Run All`

## Summary ที่แสดงในหน้าแอป

หลังอัปโหลดไฟล์แล้ว หน้าแอปจะแสดงสรุปแบบสั้นเท่านั้น:

- จำนวน record สำหรับสร้าง Team
- จำนวน record สำหรับ assign Role
- จำนวน record สำหรับ assign User

จะไม่โชว์รายการทั้งหมดของแต่ละชีทโดยอัตโนมัติ

## คำแนะนำเรื่องการ Deploy

toolkit นี้เหมาะกับ:

- consult ที่ดูแลงาน setup หรือ validate provisioning ใน SAC
- admin ที่รันงานแบบ local หรือใน environment ภายในที่ควบคุมได้

ถ้าจะดัดแปลงไปเป็น UI ที่ deploy ให้ลูกค้าใช้งานต่อ ควรระวังเรื่อง credential เป็นพิเศษ:

- อย่า hardcode `client_secret`
- อย่า expose OAuth credentials ใน code ที่ฝั่ง browser เข้าถึงได้
- อย่า commit ไฟล์ config ของลูกค้าลง Git
- อย่าให้ secret หลุดผ่าน log, screenshot, demo video หรือ package ที่แจกต่อ
- ควรเก็บ secret ฝั่ง server หรือใช้ secret manager ที่ปลอดภัย
- ควรใช้ OAuth client แยก และให้เฉพาะ scope ที่จำเป็นจริง
- ควรทดสอบ flow ใน SAC non-production tenant ก่อนเสมอ

## ข้อควรระวังตอนใช้งานจริง

- `Validate & Preview` รันได้โดยยังไม่ต้องใส่ credential แต่ task อื่นต้องมี connection settings ที่ถูกต้อง
- `Assign Roles` ต้องอิงกับ team ที่มีอยู่ใน SAC แล้ว หรือถูกสร้างมาก่อนใน flow เดียวกัน
- `Assign Users` ใช้กับ existing SAC users เท่านั้น ไม่ได้ create user profile ใหม่จาก workbook รูปแบบนี้
- ควรทดสอบ role assignment และ user assignment ใน non-production tenant ก่อน โดยเฉพาะถ้า tenant มี policy หรือ naming convention เข้ม
- ถ้า run batch ใหญ่แล้วมี partial failure ควร review log ก่อนกดซ้ำ

## การตรวจสอบในเครื่อง

รัน tests:

```bash
python3 -m unittest discover -s tests -v
```

รัน syntax check:

```bash
python3 -m py_compile sac_role_core.py app.py
```

## License

repo นี้แจกฟรีสำหรับการใช้งานส่วนตัว การเรียนรู้ และการใช้งานภายในองค์กรแบบไม่เชิงพาณิชย์เท่านั้น

- ไม่มีการรับประกันการทำงาน
- ใช้งานด้วยความเสี่ยงของผู้ใช้เอง
- ผู้จัดทำไม่รับผิดชอบต่อความเสียหายหรือผลกระทบจากการใช้งาน
- หากจะนำไปใช้เชิงพาณิชย์ ต้องขออนุญาตแยกต่างหาก

ดูรายละเอียดเพิ่มเติมที่ [LICENSE.md](LICENSE.md)
