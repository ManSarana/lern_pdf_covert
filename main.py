import io
import zipfile
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
import pypdfium2 as pdfium

app = FastAPI()

html_content = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>แปลง PDF เป็น PNG ฟรี - แปลงไฟล์รวดเร็ว ปลอดภัย</title>
    <!-- โหลด Tailwind CSS ผ่าน CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-slate-50 min-h-screen text-slate-800 font-sans flex flex-col justify-between">

    <!-- Header / Navbar -->
    <header class="bg-white border-b border-slate-200 py-4 shadow-sm">
        <div class="max-w-4xl mx-auto px-4 flex justify-between items-center">
            <div class="flex items-center space-x-2">
                <i class="fa-solid fa-file-pdf text-red-500 text-2xl"></i>
                <span class="text-xl font-bold text-slate-800">PDF2PNG Fast</span>
            </div>
            <span class="text-xs bg-emerald-100 text-emerald-800 px-2.5 py-1 rounded-full font-medium">100% Free & Secure</span>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-4 py-8 w-full">
        
        <!-- พื้นที่จำลองโฆษณา Google AdSense (บน) -->
        <div class="bg-slate-200 border border-dashed border-slate-300 rounded-lg p-4 text-center text-xs text-slate-400 mb-8 min-h-[90px] flex items-center justify-center">
            [ พื้นที่โฆษณา Google AdSense Banner ]
        </div>

        <!-- หัวข้อหลัก -->
        <div class="text-center mb-8">
            <h1 class="text-3xl md:text-4xl font-extrabold text-slate-900 mb-3">แปลงไฟล์ PDF เป็นรูปภาพ PNG</h1>
            <p class="text-slate-500 text-sm md:text-base">แปลงเอกสาร PDF ของคุณเป็นรูปภาพคุณภาพสูงได้ง่ายๆ ในไม่กี่วินาที ฟรี ไม่ต้องลงทะเบียน</p>
        </div>

        <!-- กล่องแปลงไฟล์ (Card) -->
        <div class="bg-white rounded-2xl shadow-lg border border-slate-100 p-6 md:p-10 mb-8">
            <form id="uploadForm" action="/convert" method="post" enctype="multipart/form-data" onsubmit="showLoading()">
                <div class="border-2 border-dashed border-indigo-200 hover:border-indigo-500 rounded-xl p-8 text-center transition-colors duration-200 bg-indigo-50/30 cursor-pointer relative">
                    <input type="file" id="fileInput" name="file" accept=".pdf" required 
                           class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                           onchange="updateFileName(this)">
                    <div class="flex flex-col items-center">
                        <i class="fa-solid fa-cloud-arrow-up text-4xl text-indigo-500 mb-3"></i>
                        <span id="fileName" class="text-base font-semibold text-slate-700 mb-1">ลากไฟล์ PDF มาวางที่นี่ หรือ คลิกเพื่อเลือกไฟล์</span>
                        <span class="text-xs text-slate-400">รองรับไฟล์ .PDF เท่านั้น</span>
                    </div>
                </div>

                <div class="mt-6 text-center">
                    <button type="submit" id="submitBtn" 
                            class="w-full md:w-auto px-8 py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-base rounded-xl shadow-md shadow-indigo-200 hover:shadow-lg transition-all duration-200 flex items-center justify-center space-x-2 mx-auto">
                        <i class="fa-solid fa-gear"></i>
                        <span>แปลงไฟล์และดาวน์โหลด (ZIP)</span>
                    </button>
                </div>
            </form>

            <!-- สถานะกำลังโหลด (แสดงตอนกดปุ่ม) -->
            <div id="loadingState" class="hidden text-center py-6">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent mb-3"></div>
                <p class="text-indigo-600 font-medium text-sm">กำลังแปลงไฟล์ PDF เป็นรูปภาพ กรุณารอสักครู่...</p>
            </div>
        </div>

        <!-- ข้อความอธิบายวิธีใช้ (สำคัญมากสำหรับการทำ SEO ให้ติดหน้าแรก Google) -->
        <div class="grid md:grid-cols-3 gap-6 mb-8 text-slate-600 text-sm">
            <div class="bg-white p-5 rounded-xl border border-slate-100 shadow-sm">
                <i class="fa-solid fa-bolt text-indigo-500 text-xl mb-2"></i>
                <h3 class="font-bold text-slate-800 mb-1">รวดเร็วทันใจ</h3>
                <p class="text-slate-500 text-xs">ระบบประมวลผลแปลงไฟล์ด้วย Python ความเร็วสูง ได้ภาพความคมชัดสูงทันที</p>
            </div>
            <div class="bg-white p-5 rounded-xl border border-slate-100 shadow-sm">
                <i class="fa-solid fa-shield-halved text-indigo-500 text-xl mb-2"></i>
                <h3 class="font-bold text-slate-800 mb-1">ปลอดภัย 100%</h3>
                <p class="text-slate-500 text-xs">ไฟล์ของคุณจะถูกประมวลผลในหน่วยความจำชั่วคราว ไม่มีการบันทึกไว้ในเซิร์ฟเวอร์</p>
            </div>
            <div class="bg-white p-5 rounded-xl border border-slate-100 shadow-sm">
                <i class="fa-solid fa-laptop text-indigo-500 text-xl mb-2"></i>
                <h3 class="font-bold text-slate-800 mb-1">ใช้งานได้ทุกอุปกรณ์</h3>
                <p class="text-slate-500 text-xs">แปลงไฟล์ได้สะดวกทั้งบนคอมพิวเตอร์ แท็บเล็ต และสมาร์ตโฟน</p>
            </div>
        </div>

        <!-- พื้นที่จำลองโฆษณา Google AdSense (ล่าง) -->
        <div class="bg-slate-200 border border-dashed border-slate-300 rounded-lg p-4 text-center text-xs text-slate-400 min-h-[90px] flex items-center justify-center">
            [ พื้นที่โฆษณา Google AdSense Banner ]
        </div>

    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-400">
        <p>© 2026 PDF2PNG Fast. All rights reserved.</p>
    </footer>

    <!-- JavaScript เล็กๆ น้อยๆ สำหรับเปลี่ยนชื่อไฟล์และแสดงสถานะโหลด -->
    <script>
        function updateFileName(input) {
            const fileNameSpan = document.getElementById('fileName');
            if (input.files && input.files[0]) {
                fileNameSpan.textContent = "เลือกไฟล์แล้ว: " + input.files[0].name;
                fileNameSpan.classList.add('text-indigo-600');
            }
        }

        function showLoading() {
            document.getElementById('uploadForm').classList.add('hidden');
            document.getElementById('loadingState').classList.remove('hidden');
            
            // คืนค่าหน้าปกติเมื่อดาวน์โหลดเสร็จ (ประมาณ 5 วินาที)
            setTimeout(() => {
                document.getElementById('uploadForm').classList.remove('hidden');
                document.getElementById('loadingState').classList.add('hidden');
            }, 5000);
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def main_page():
    return html_content

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    pdf = pdfium.PdfDocument(pdf_bytes)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for i, page in enumerate(pdf):
            image = page.render(scale=2).to_pil()
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            zip_file.writestr(f"page_{i+1}.png", img_byte_arr.getvalue())

    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer, 
        media_type="application/zip", 
        headers={"Content-Disposition": "attachment; filename=converted_images.zip"}
    )