import asyncio
from app.core.database import connect_to_mongo
from app.models.medical_report import MedicalReport
from app.services.ollama_service import analyse_report_text

async def main():
    await connect_to_mongo()
    reports = await MedicalReport.find_all().to_list()
    if not reports:
        print("No reports found")
        return
    report = reports[-1]
    
    if not report.extracted_text:
        print("Report has no text")
        return
        
    print(f"Testing with report {report.id}")
    try:
        res = await analyse_report_text(report.extracted_text)
        print("Success:", res)
    except Exception as e:
        print("Error during analysis:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
