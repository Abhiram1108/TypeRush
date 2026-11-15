import docx
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc_paths = [
    'TypeRush_Final_Project_Report.docx',
    'report/TypeRush_Final_Project_Report.docx',
    'report/TypeRush_Project_Report_APP.docx'
]

new_text = (
    "The TypeRush interface is engineered around the 'Midnight Minimal' dark theme (#0B0D12 foundational background), "
    "emphasizing visual contrast, clear visual hierarchy, and zero clutter. The main dashboard window is organized into "
    "five core functional regions, illustrated in Figure 5.2: "
    "(1) Navigation Sidebar providing instantaneous switching between Home, Typing Test, History, and Settings; "
    "(2) Quick-Start Configuration Card containing interactive difficulty (Easy, Medium, Hard, Expert) and duration "
    "(15s, 30s, 60s, 120s) selectors; "
    "(3) Primary Action Button (CTA) providing a prominent, high-contrast trigger to initialize the typing engine; "
    "(4) Performance Metrics Overview showcasing lifetime telemetry including Personal Best WPM, Average Speed, "
    "Precision Accuracy, and Total Tests Completed; and "
    "(5) Progression & Activity Timeline featuring the interactive velocity spline curve and chronological recent session history."
)

for doc_path in doc_paths:
    try:
        doc = docx.Document(doc_path)
        # Find 5.2 paragraph
        found_p = False
        for i, p in enumerate(doc.paragraphs):
            if "The TypeRush interface is engineered around" in p.text:
                p.text = new_text
                found_p = True
                print(f"Updated description in {doc_path} at paragraph {i}")
                break
        
        # Update Table 4 (Layout figure table)
        if len(doc.tables) > 4:
            cell_t4 = doc.tables[4].cell(0, 0)
            cell_t4.text = ""
            p_t4 = cell_t4.paragraphs[0]
            p_t4.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_t4.add_run().add_picture("report/.build/figure_5_2_layout.png", width=Inches(5.8))
            print(f"Updated Figure 5.2 image in {doc_path} Table 4")

        doc.save(doc_path)
        print(f"Successfully saved {doc_path}")
    except Exception as e:
        print(f"Error updating {doc_path}: {e}")
