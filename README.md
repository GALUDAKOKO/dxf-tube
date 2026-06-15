# DXF Tube — เว็บแอปนับ tube จากแบบไฟฟ้า

อัปโหลดไฟล์ `.dxf` (AutoCAD Electrical) → กด Export → ได้ Excel ตารางพิมพ์ tube
และรายชื่ออุปกรณ์ ใช้ engine เดียวกับ skill `dxf-tube` (ทดสอบแล้ว)

## ติดตั้ง (ครั้งเดียว)
ต้องมี Python 3.10+ ในเครื่อง
```bash
pip install -r requirements.txt
```

## รันใช้งาน
```bash
python app/server.py
```
เปิดเบราว์เซอร์ไปที่ http://127.0.0.1:8000
ลากไฟล์ .dxf ลงไป แล้วกด **Export Excel** ไฟล์จะดาวน์โหลดอัตโนมัติ

## โครงสร้าง
```
dxf-tube-app/
├── requirements.txt
├── README.md
└── app/
    ├── server.py     FastAPI: เสิร์ฟหน้าเว็บ + endpoint /export
    ├── index.html    หน้าอัปโหลด/export
    └── dxf_tube.py   engine นับ tube (เหมือน skill)
```

## หมายเหตุการนับ
- สายแนวตั้ง device-to-device → นับ tube อัตโนมัติ (= 2 × จุดเชื่อม)
- bus rail (220V, N) และเส้นแตกสาขา → เว้นว่าง + ไฮไลต์สีส้มใน Excel
  ให้กรอกเองจากแบบ (ระบบไม่ใส่เลขที่ไม่แน่ใจ)
- ไฟล์ไม่ถูกเก็บบน server — parse ในหน่วยความจำแล้วส่งกลับทันที

## deploy ให้ทีมเล็กใช้ (ภายหลัง ถ้าต้องการ)
รันบนเครื่องในวงแลนแล้วเปลี่ยน host เป็น 0.0.0.0 —
แก้บรรทัดท้าย `app/server.py` เป็น `uvicorn.run(app, host="0.0.0.0", port=8000)`
เพื่อนในวงแลนเข้าผ่าน `http://<ip-เครื่องคุณ>:8000`
