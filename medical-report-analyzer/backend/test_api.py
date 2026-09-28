import httpx
import asyncio
import time

async def run_upload_check():
    print("Testing API Upload endpoint...")
    async with httpx.AsyncClient(timeout=300) as client:
        # 1. Login to get token
        print("Logging in as lakshya123@gmail.com...")
        login_res = await client.post("http://127.0.0.1:8000/auth/login", data={"username": "lakshya123@gmail.com", "password": "password123"})
        if login_res.status_code != 200:
            print("Login failed:", login_res.text)
            return
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Upload file
        print("Uploading test_report_subhayu.pdf...")
        with open("../test_report_subhayu.pdf", "rb") as f:
            files = {"file": ("test_report_subhayu.pdf", f, "application/pdf")}
            upload_res = await client.post("http://127.0.0.1:8000/reports/upload", files=files, headers=headers)
        
        if upload_res.status_code != 201:
            print("Upload failed:", upload_res.text)
            return
        
        report_id = upload_res.json()["id"]
        print(f"Uploaded successfully. Report ID: {report_id}")
        
        # 3. Trigger Analysis
        print("Triggering analysis... (This might take a few minutes)")
        start_time = time.time()
        try:
            analysis_res = await client.post(f"http://127.0.0.1:8000/analysis/{report_id}", headers=headers, timeout=300)
            elapsed = time.time() - start_time
            print(f"Analysis completed in {elapsed:.2f} seconds!")
            print(f"Status Code: {analysis_res.status_code}")
            print(f"Response: {analysis_res.text}")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"Failed after {elapsed:.2f} seconds.")
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_upload_check())
