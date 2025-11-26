import asyncio
import json
from app.services.pdf_parser import PDFParserService
from app.services.extraction_pipeline import ExtractionPipeline


async def main():
    # Parse PDF
    parser = PDFParserService()
    # result = await parser.parse_document("../Dushyant-Mahajan-Resume.pdf")
    result = await parser.parse_document("../Sample Resume 2.pdf")

    print("=" * 60)
    print("RAW TEXT FROM PDF:")
    print("=" * 60)
    print(result.content)

    # Extract structured data
    print("\n" + "=" * 60)
    print("EXTRACTED DATA:")
    print("=" * 60)

    pipeline = ExtractionPipeline()
    extracted = pipeline.extract(result.content)

    # Print contact info
    print("\n📋 CONTACT INFO:")
    print(f"  Name: {extracted.contact.first_name} {extracted.contact.last_name}")
    print(f"  Email: {extracted.contact.email}")
    print(f"  Phone: {extracted.contact.phone}")
    print(f"  Location: {extracted.contact.city}, {extracted.contact.state}")

    # Print education
    print(f"\n🎓 EDUCATION ({len(extracted.education)} entries):")
    for i, edu in enumerate(extracted.education, 1):
        print(f"  {i}. {edu.degree} - {edu.institution} ({edu.graduation_year})")

    # Print work experience
    print(f"\n💼 WORK EXPERIENCE ({len(extracted.work_experience)} entries):")
    for i, exp in enumerate(extracted.work_experience, 1):
        print(f"  {i}. {exp.job_title} at {exp.company}")
        print(f"     {exp.start_date} - {exp.end_date}")
        if exp.description:
            for desc in exp.description[:2]:  # Show first 2 bullets
                print(f"     • {desc[:80]}...")

    # Print skills
    print(f"\n🛠️ SKILLS ({len(extracted.skills)} found):")
    print(f"  {', '.join(extracted.skills)}")

    # Print as JSON
    print("\n" + "=" * 60)
    print("JSON OUTPUT:")
    print("=" * 60)
    print(json.dumps(extracted.model_dump(exclude={"raw_text"}), indent=2))


asyncio.run(main())