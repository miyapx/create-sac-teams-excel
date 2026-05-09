# Bulk Create SAC Teams from Excel

## Summary

การสร้าง SAC Team ทีละรายการใน UI ทำได้ แต่จะเริ่มเสียเวลามากเมื่อจำนวนทีมเพิ่มขึ้น

repo นี้เปลี่ยน flow ให้เป็นแบบ upload tool:

1. เตรียม Excel workbook ไฟล์เดียว
2. อัปโหลดเข้า local Streamlit tool
3. validate workbook
4. เลือกสั่ง create team, assign role, และ assign user จากหน้าจอเดียว

ข้อสำคัญ: tool นี้เป็น **implementation ของเราเอง** ไม่ใช่ SAP sample code
และถ้าจะอธิบายให้ตรงที่สุด ควรเรียกว่า free source-available toolkit มากกว่า open-source เพราะ license ปัจจุบันยังจำกัดการใช้งานเชิงพาณิชย์

## ทำไมเวอร์ชันนี้ใช้ง่ายกว่า

แอปถูกออกแบบให้ใช้งาน local ได้ตรงๆ:

- ใช้ light theme เสมอ
- เปิดแอปได้แม้ยังไม่มี `config.ini`
- กรอก connection จาก UI ได้
- sample workbook มีไว้ให้โหลด ไม่ได้ถูก auto-load
- summary หลังอัปโหลดแสดงแบบสั้น ไม่โชว์ข้อมูลยาวเกินจำเป็น

## Workbook Contract

เครื่องมือนี้ยึดไฟล์หลัก:

`data/sac_team_data.xlsx`

sheet ที่รองรับ:

- `Create_Teams`
- `Assign_Roles`
- `Users`

คอลัมน์ที่ต้องมี:

- `Create_Teams`: `Team ID`, `Team Description`
- `Assign_Roles`: `TeamID`, `RoleID`
- `Users`: `UserName`, `TeamID`

## Flow ในแอป

### Step 1: โหลด Excel template ถ้าต้องการ template

sample file มีไว้เป็นตัวอย่างเท่านั้น
จะไม่ถูกใช้เป็น default ตอนเปิดแอป

### Step 2: อัปโหลด workbook ของเรา

เมื่ออัปโหลดแล้ว แอปจะเริ่มตรวจโครงสร้าง workbook

### Step 3: เปิด Connection Settings

กรอก:

- `tenant_url`
- `token_url`
- `client_id`
- `client_secret`

ถ้าต้องการใช้ซ้ำในรอบถัดไป ก็สามารถ save config locally ได้

### Step 4: กด `Validate & Preview`

ปุ่มนี้ยังไม่ยิง SAC
ใช้เพื่อเช็ก workbook และดู planned actions ก่อน

### Step 5: เลือก action ที่ต้องการ

เลือก task จาก dropdown แล้วค่อยกด `Run`

task ที่มี:

- `Validate & Preview`
- `Create Teams`
- `Assign Roles`
- `Assign Users`
- `Run All`

## Summary แบบสั้นในหน้าแอป

หลังอัปโหลดแล้ว UI จะแสดงสรุปสั้นๆ เท่านั้น:

- มี record สำหรับสร้าง team กี่รายการ
- มี record สำหรับ assign role กี่รายการ
- มี record สำหรับ assign user กี่รายการ

ทำให้หน้าจอยังอ่านง่าย แม้ workbook จะมีข้อมูลจำนวนมาก

## หมายเหตุการเผยแพร่

repo snapshot นี้จัดไว้ตาม workflow ปัจจุบัน ณ วันที่ **9 May 2026**

## License Note

repo นี้แจกฟรีสำหรับการใช้งานส่วนตัว การเรียนรู้ และการใช้งานภายในองค์กรแบบไม่เชิงพาณิชย์เท่านั้น โดยไม่มี warranty และไม่รับผิดชอบความเสียหาย ดูเพิ่มเติมใน `LICENSE.md`
