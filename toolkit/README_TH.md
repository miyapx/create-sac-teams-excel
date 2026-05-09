# README (TH)

toolkit นี้ใช้สำหรับรัน local เพื่อจัดการ SAC Team จาก Excel workbook ไฟล์เดียว

ไฟล์สำคัญ:

- `app.py` — หน้า Streamlit
- `sac_role_core.py` — logic หลัก
- `sac_team_data.xlsx` — template สำหรับอัปโหลด
- `config.ini.example` — ตัวอย่าง config
- `requirements.txt` — dependencies
- `LICENSE.md` — เงื่อนไขการใช้งาน
- `COMMON_ERRORS.md` — รวม error ที่พบบ่อยและวิธีเช็กเบื้องต้น

วิธีรันจาก root repo:

- macOS: `./run.command`
- Windows: `run.bat`

หรือรันเอง:

```bash
python3 -m pip install -r toolkit/requirements.txt
python3 -m streamlit run toolkit/app.py
```

## SSL Certificate Requirement

tool นี้เรียก SAC ผ่าน HTTPS ดังนั้นบางเครื่อง โดยเฉพาะ Python ที่เพิ่งติดตั้งใหม่ อาจเจอ error แบบนี้:

```text
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

ถ้า `curl` เข้า `token_url` ได้ แต่ Python เข้าไม่ได้ ปัญหามักอยู่ที่ local Python certificate store

### macOS

ติดตั้ง dependency ก่อน:

```bash
python3 -m pip install -r toolkit/requirements.txt
python3 -m pip install --upgrade certifi
```

ถ้าใช้ Python จาก `python.org` ให้รันเพิ่ม:

```bash
open "/Applications/Python 3.14/Install Certificates.command"
```

ถ้ายังไม่หาย ให้ลองรัน app โดยชี้ `SSL_CERT_FILE` ไปที่ bundle ของ `certifi`:

```bash
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
python3 -m streamlit run toolkit/app.py
```

### Windows

ติดตั้ง dependency ก่อน:

```bat
py -3 -m pip install -r toolkit\requirements.txt
py -3 -m pip install --upgrade certifi
```

ถ้า Python ยังติดปัญหา HTTPS ให้ชี้ `SSL_CERT_FILE` ไปที่ CA bundle ของ `certifi` สำหรับ session นั้น:

```bat
for /f "delims=" %i in ('py -3 -c "import certifi; print(certifi.where())"') do set SSL_CERT_FILE=%i
py -3 -m streamlit run toolkit\app.py
```

### Quick Check

ใช้ 2 คำสั่งนี้เช็กเร็วว่าเป็นปัญหา auth หรือ SSL:

```bash
curl -I "YOUR_TOKEN_URL"
python3 -c "import urllib.request; print(urllib.request.urlopen('YOUR_TOKEN_URL').status)"
```

- ถ้า `curl` ผ่าน แต่ Python ไม่ผ่าน ให้แก้ที่ Python certificate
- ถ้าไม่ผ่านทั้งคู่ ให้เช็ก network, proxy, หรือ endpoint access

ข้อควรระวัง:

- `Validate & Preview` ยังไม่ยิง SAC
- task อื่นต้องใส่ connection settings ให้ครบ
- `Assign Users` ใช้กับ existing SAC users only
- ในชีต `Assign_Roles` ค่า `RoleID` ต้องตรงกับ role ID จริงใน SAC tenant ของคุณ โดย standard roles มักเป็น `PROFILE:...` แต่ custom role IDs อาจต่างออกไป
- ตอน assign roles ถ้าค่า `RoleID` ไม่ได้ขึ้นต้นด้วย `PROFILE:` app จะเติม tenant custom role prefix ให้อัตโนมัติก่อนส่ง SCIM update
- ควรทดสอบใน non-production tenant ก่อน
- ถ้าติดปัญหาระหว่างรัน ให้เปิดดู `COMMON_ERRORS.md` ควบคู่กับ `Execution Log`

Known issues:

- บาง tenant อาจยังตอบ `403 Forbidden` ตอนทำ SCIM write operation เช่น `POST /Groups` แม้จะขอ token ได้แล้ว ในกรณีนี้ควรเช็ก OAuth client ใน SAC อีกครั้ง โดยเฉพาะ `API Access`, `User Provisioning`, และ `Client Credentials`
- SAC แต่ละ environment อาจตอบรับคนละ SCIM route ตอนนี้ toolkit จะลองทั้ง `.../scim2` และ `.../api/v1/scim` ให้อัตโนมัติ แต่ฝั่ง tenant ยังสามารถ block write operation ได้
- workbook format ปัจจุบันมอง `Users` เป็น existing SAC users เท่านั้น ยังไม่ได้สร้าง user ใหม่จากไฟล์
- ถ้าต้อง debug เพิ่ม ให้ดู `Execution Log` ใน app เพราะตอนนี้จะแสดง SCIM candidates, active SCIM base URL, และ step trace ก่อนที่จะ fail

เรื่อง license:

- ใช้ได้ฟรีสำหรับ personal, learning, และ internal non-commercial use
- ไม่ควรเรียกว่า open-source แบบเต็ม เพราะ license ยังจำกัด commercial use
