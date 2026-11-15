import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner padding for a table cell (in twips: 20 twips = 1 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def add_callout_box(doc, title, text, border_color="034DA1", bg_color="F1F5F9"):
    """Create a styled academic callout box with a colored left accent border."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

    # Set left border only
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    run_t = p.add_run(f"■  {title}\n")
    run_t.font.name = "Segoe UI"
    run_t.font.size = Pt(10.5)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(0x00, 0x2B, 0x49)

    run_body = p.add_run(text)
    run_body.font.name = "Segoe UI"
    run_body.font.size = Pt(9.5)
    run_body.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def format_table_headers(table, col_widths=None):
    """Apply standard institutional styling to a table header."""
    header_row = table.rows[0]
    # Repeat header across pages
    trPr = header_row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

    for idx, cell in enumerate(header_row.cells):
        set_cell_background(cell, "002B49")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        if col_widths and idx < len(col_widths):
            cell.width = Inches(col_widths[idx])
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for r in p.runs:
                r.font.name = "Segoe UI"
                r.font.size = Pt(9.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Alternate row styling for data rows
    for r_idx, row in enumerate(table.rows[1:], start=1):
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for idx, cell in enumerate(row.cells):
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=90, bottom=90, left=140, right=140)
            if col_widths and idx < len(col_widths):
                cell.width = Inches(col_widths[idx])
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                for r in p.runs:
                    r.font.name = "Segoe UI"
                    r.font.size = Pt(9.0)
                    r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

def build_document():
    doc = docx.Document()

    # 1. Page Setup: 1 inch margins all around
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

        # Running Header
        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.text = "TypeRush 2.1 — Team Work Distribution & Technical Contributions Report"
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if p_hdr.runs:
            p_hdr.runs[0].font.name = "Segoe UI"
            p_hdr.runs[0].font.size = Pt(8.5)
            p_hdr.runs[0].font.italic = True
            p_hdr.runs[0].font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

        # Running Footer
        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.text = "Department of Computational Intelligence • SRM Institute of Science and Technology"
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if p_ftr.runs:
            p_ftr.runs[0].font.name = "Segoe UI"
            p_ftr.runs[0].font.size = Pt(8.0)
            p_ftr.runs[0].font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

    # Base Styles
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Segoe UI"
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    # --------------------------------------------------------------------------
    # COVER / HEADER BLOCK
    # --------------------------------------------------------------------------
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("SRM INSTITUTE OF SCIENCE AND TECHNOLOGY\n")
    r_inst.font.name = "Segoe UI"
    r_inst.font.size = Pt(12)
    r_inst.font.bold = True
    r_inst.font.color.rgb = RGBColor(0x00, 0x2B, 0x49)

    r_dept = p_inst.add_run("DEPARTMENT OF COMPUTATIONAL INTELLIGENCE • SCHOOL OF COMPUTING\n")
    r_dept.font.name = "Segoe UI"
    r_dept.font.size = Pt(10)
    r_dept.font.bold = True
    r_dept.font.color.rgb = RGBColor(0x03, 0x4D, 0xA1)

    r_course = p_inst.add_run("21CSC203P – ADVANCED PROGRAMMING PRACTICE (A.P.P.)\n")
    r_course.font.name = "Segoe UI"
    r_course.font.size = Pt(9.5)
    r_course.font.bold = True
    r_course.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # Gold accent line
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_after = Pt(14)
    r_line = p_line.add_run("━" * 58)
    r_line.font.color.rgb = RGBColor(0xC7, 0xA0, 0x08)
    r_line.font.bold = True

    # Report Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(4)
    r_t1 = p_title.add_run("TypeRush 2.1 — Desktop Typing Speed Test & Analytics\n")
    r_t1.font.name = "Segoe UI"
    r_t1.font.size = Pt(17)
    r_t1.font.bold = True
    r_t1.font.color.rgb = RGBColor(0x00, 0x2B, 0x49)

    r_t2 = p_title.add_run("TEAM WORK DISTRIBUTION & INDIVIDUAL CONTRIBUTIONS REPORT")
    r_t2.font.name = "Segoe UI"
    r_t2.font.size = Pt(13)
    r_t2.font.bold = True
    r_t2.font.color.rgb = RGBColor(0x03, 0x4D, 0xA1)

    # Metadata Card
    add_callout_box(
        doc,
        "ACADEMIC PROJECT METADATA",
        "Application Name: TypeRush 2.1 (Native Desktop Typing Benchmark)\n"
        "Course & Subject Code: Advanced Programming Practice (21CSC203P)\n"
        "Public GitHub Repository: https://github.com/Abhiram1108/TypeRush\n"
        "Architecture: 100% Native Python 3.12+ & Standard Tkinter GUI (Zero External Frameworks)\n"
        "Quality Assurance: 91 Automated Unit & Regression Tests (Passing status: OK)",
        border_color="034DA1",
        bg_color="F8FAFC"
    )

    def add_sec_heading(title, number):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(f"Section {number} – {title}")
        run.font.name = "Segoe UI"
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x00, 0x2B, 0x49)
        return p

    def add_sub_heading(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.font.name = "Segoe UI"
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x03, 0x4D, 0xA1)
        return p

    def add_p(text, bold_prefix=None, space_after=5):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.bold = True
            r_pre.font.color.rgb = RGBColor(0x00, 0x2B, 0x49)
        r_text = p.add_run(text)
        r_text.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        return p

    # --------------------------------------------------------------------------
    # SECTION 1 – INTRODUCTION
    # --------------------------------------------------------------------------
    add_sec_heading("Introduction", "1")
    add_p(
        "Modern software engineering and computer science curricula necessitate high typing fluency, precision, and cognitive efficiency. "
        "Typographical errors and sluggish keyboard rhythms introduce severe friction into code synthesis, debugging, and computational thinking. "
        "TypeRush 2.1 was designed and developed for the Advanced Programming Practice (21CSC203P) laboratory curriculum at SRM Institute of Science "
        "and Technology as an ultra-responsive, distraction-free desktop typing benchmark and keyboard fluency training platform. "
        "Built strictly with standard library Python and the Tkinter GUI toolkit, TypeRush eliminates the latency, security vulnerabilities, "
        "and runtime memory bloat associated with embedded web browsers (Electron, CEF, webviews) and remote cloud services."
    )
    add_p(
        "To achieve software engineering excellence and ensure clean modularization, the architectural, algorithmic, and data persistence "
        "responsibilities of TypeRush were divided among three specialized student engineers. The team adopted a strict separation of concerns (SoC) "
        "modeled after the Model-View-Presenter (MVP) and Event-Driven architecture patterns. This work distribution ensured that algorithmic string "
        "alignment, atomic local persistence, and high-DPI graphical rendering could be independently authored, rigorously unit-tested, and seamlessly integrated."
    )

    # --------------------------------------------------------------------------
    # SECTION 2 – PROJECT OVERVIEW
    # --------------------------------------------------------------------------
    add_sec_heading("Project Overview", "2")
    add_p(
        "TypeRush 2.1 is an offline-first desktop application designed around the 'Midnight Minimal' typography-first aesthetic. "
        "Unlike conventional typing testers that evaluate entire sentences with rigid character offsets—causing a single accidental omission to cascade "
        "and mark all subsequent words incorrect—TypeRush introduces an intelligent word-level string alignment engine. "
        "The application provides four curated vocabulary tiers (Easy, Medium, Hard, and Expert) and four configurable test durations (15s, 30s, 60s, and 120s)."
    )

    add_sub_heading("2.1 Core Implemented Capabilities")
    capabilities = [
        ("Continuous Text Stream: ", "Generates dynamic passages from a stateful shuffled content deck with rolling exclusion to guarantee non-repeating sentences."),
        ("Cascade-Immune Alignment: ", "Isolates errors strictly to word N. Committing an inaccurate word via spacebar advances the pointer to word N+1 without penalizing downstream words."),
        ("Real-Time Tri-State Visual Feedback: ", "Immediate character coloring: vivid green (#4ADE80) for correct keys, crimson red (#F87171) for errors, and muted slate (#858D9E) for pending glyphs."),
        ("Native Insertion Caret: ", "Synchronized fluid vertical cursor mapped dynamically through font bounding-box metrics (text_display.bbox()), eliminating visual jitter."),
        ("Standardized Telemetry: ", "Continuous computation of Gross WPM, Net WPM, accuracy percentages, rhythm consistency (standard deviation), and peak velocity."),
        ("Granular Mistake Diagnostics: ", "Post-session Levenshtein diff analysis categorizing mistakes into Substitutions, Omissions, and Insertions."),
        ("Atomic Local Persistence: ", "Thread-safe atomic JSON persistence (data/history.json) with UUID tracking, CSV export, and safe preference storage."),
        ("Windows High-DPI Scaling: ", "Per-Monitor V2 awareness bootstrap via ctypes, ensuring crisp fonts, sharp canvas curves, and clean window scaling.")
    ]
    for bold_txt, norm_txt in capabilities:
        add_p(norm_txt, bold_prefix=f"•  {bold_txt}", space_after=3)

    add_sub_heading("2.2 Architectural Layers and Inter-Module Collaboration")
    add_p(
        "The software architecture comprises five decoupled layers: (1) Presentation Shell (ui/app.py, main.py), "
        "(2) View Screen Routers (ui/screens/), (3) Algorithmic Alignment & Engine (ui/alignment.py, ui/scoring.py), "
        "(4) Content Generation & Audio (ui/content_generator.py, ui/audio_manager.py), and (5) Persistence Layer (ui/storage.py). "
        "Each layer communicates across strictly defined data contracts using Python dataclasses and primitive dictionary payloads, "
        "ensuring zero tight coupling between UI widgets and mathematical scoring algorithms."
    )

    # --------------------------------------------------------------------------
    # SECTION 3 – TEAM COMPOSITION
    # --------------------------------------------------------------------------
    add_sec_heading("Team Composition & Role Allocation", "3")
    add_p(
        "The project development responsibilities were assigned based on domain specializations across algorithms, backend persistence, "
        "and graphical user interface architecture. The official role distribution is summarized in Table 3.1."
    )

    # Table 3.1
    t3 = doc.add_table(rows=4, cols=4)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    t3_data = [
        ["S. No.", "Student Name & Reg. No.", "Assigned Engineering Role", "Major Functional Responsibility"],
        ["1", "Boddupalli Phani Venkata Sri Abhiram\n(RA2511026010355)", "Core Typing Engine & Algorithm Development", "Levenshtein alignment, cascade immunity, gross/net WPM equations, live character evaluation, and native caret synchronization."],
        ["2", "Biswa Prakash Rout\n(RA2511026010339)", "Data Management, Backend Logic & Analytics", "Atomic JSON persistence, safe recovery, session history filtering, CSV export, results dashboard telemetry, audio engine, and executable packaging."],
        ["3", "Shivansh Bansal\n(RA2511026010332)", "Frontend Development, UI/UX & Architecture", "Midnight Minimal design tokens, application shell controller, home dashboard, reusable custom canvas widgets, animation scheduler, and visual verification."]
    ]
    for r_idx, row in enumerate(t3.rows):
        for c_idx, val in enumerate(t3_data[r_idx]):
            row.cells[c_idx].paragraphs[0].text = val
    format_table_headers(t3, [0.6, 2.0, 1.8, 2.1])

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # --------------------------------------------------------------------------
    # SECTION 4 – INDIVIDUAL WORK DISTRIBUTION
    # --------------------------------------------------------------------------
    add_sec_heading("Individual Work Distribution", "4")

    # 4.1 Abhiram
    add_sub_heading("4.1 Member 1: Boddupalli Phani Venkata Sri Abhiram")
    add_p("Core Typing Engine, Algorithm Development and Real-Time Typing Interaction", bold_prefix="Assigned Role: ")
    add_p(
        "Member 1 owned the algorithmic core of TypeRush. This encompasses designing the real-time event-driven typing loop, "
        "authoring the Levenshtein-based string alignment engine, eliminating catastrophic error cascading, formulating standardized "
        "Gross/Net WPM calculations, and synchronizing the native insertion cursor with sub-millisecond responsiveness."
    )

    add_p("Specific Implementation Responsibilities:", bold_prefix="Detailed Responsibilities:\n")
    abhiram_tasks = [
        "Architected the authoritative single-widget continuous text stream in `ui/screens/typing_screen.py`.",
        "Engineered the `TypingAlignmentEngine` in `ui/alignment.py` to tokenize target and input streams into exact word character spans.",
        "Implemented the dynamic programming Levenshtein distance matrix algorithm to classify typos into substitutions, omissions, and insertions.",
        "Developed cascade-resistant word-level segmentation: typographical errors in word N are strictly contained and never shift word N+1.",
        "Engineered case-insensitive matching logic: accepts standard casing variants while rigorously verifying symbols and punctuation.",
        "Formulated standardized Gross Words Per Minute: Gross WPM = (total_keystrokes / 5.0) / elapsed_minutes.",
        "Formulated standardized Net Words Per Minute with error penalties: Net WPM = max(0, Gross WPM - (errors / elapsed_minutes)).",
        "Formulated character precision accuracy: Accuracy % = (correct_characters / total_keystrokes) * 100.",
        "Developed rhythm consistency and pacing metrics utilizing standard deviation and coefficient of variation of interval velocity.",
        "Implemented non-blocking Tkinter `<Key>` keystroke event listeners with sub-millisecond evaluation latency.",
        "Built protected `<space>` word commitment logic: commits the active word, verifies spelling, advances word pointer, and ignores empty spaces.",
        "Implemented within-word `<BackSpace>` editing: allows typists to correct typos before committing without pointer desynchronization.",
        "Created real-time text tag manipulation (`correct`, `incorrect`, `untyped`, `active_bg`) directly on the `tk.Text` rendering pipeline.",
        "Implemented native vertical insertion caret tracking positioned dynamically via font bounding-box metrics (`text_display.bbox()`).",
        "Curated 140+ sentences across four vocabulary tiers (Easy, Medium, Hard, Expert) with rolling exclusion decks in `ui/content_generator.py`.",
        "Developed automated typing rebuild verification suites in `tests/test_v21_typing_rebuild.py` and `tests/run_v21_typing_rebuild_demo.py`."
    ]
    for task in abhiram_tasks:
        add_p(task, bold_prefix="•  ", space_after=2)

    add_p("`ui/alignment.py`, `ui/scoring.py`, `ui/content_generator.py`, `ui/screens/typing_screen.py`, `tests/test_v21_typing_rebuild.py`, `tests/run_v21_typing_rebuild_demo.py`.", bold_prefix="Primary Source Modules Handled: ")
    add_p("Dynamic programming (Levenshtein distance matrix), string tokenization, finite state machines (word commitment), asynchronous event processing, linear interpolation, bounding box geometric mapping.", bold_prefix="Technical Concepts & Algorithms: ")
    add_p("A robust, lag-free typing interaction loop capable of processing rapid 120+ WPM keystroke streams with zero cascading errors, accurate character coloring, and mathematically rigorous performance telemetry.", bold_prefix="Deliverables & Contribution: ")

    # 4.2 Biswa
    add_sub_heading("4.2 Member 2: Biswa Prakash Rout")
    add_p("Data Management, Backend Logic and Performance Analytics", bold_prefix="Assigned Role: ")
    add_p(
        "Member 2 owned the backend infrastructure, local data persistence layer, post-session performance analytics, historical session "
        "filtering, offline audio synthesis, and deployment packaging. This ensured that user session telemetry is persistently recorded "
        "without race conditions, visual graphs accurately reflect user speed curves, and users can seamlessly manage settings and export data."
    )

    add_p("Specific Implementation Responsibilities:", bold_prefix="Detailed Responsibilities:\n")
    biswa_tasks = [
        "Architected the local data persistence layer in `ui/storage.py` utilizing atomic file operations (`.tmp` write and `os.replace`).",
        "Engineered safe file recovery protocols: automatically handles missing, blank, or corrupted JSON files without crashing.",
        "Structured comprehensive JSON session schemas containing unique UUIDs, ISO timestamps, difficulty tiers, durations, and metrics.",
        "Built the diagnostic Results Screen in `ui/screens/results_screen.py` featuring an 8-metric telemetry card and consistency rating.",
        "Engineered the interactive instantaneous speed progression spline graph on `tk.Canvas`, mapping speed peaks and average pace.",
        "Developed the word-by-word mistake review UI: renders an itemized table of mistyped words alongside expected spelling and error classification.",
        "Constructed the chronological History Screen in `ui/screens/history_screen.py`, grouping sessions by date with expandable details.",
        "Implemented multi-criteria search and dynamic filtering by difficulty level (All/Easy/Med/Hard/Expert) and test duration (15s–120s).",
        "Engineered one-click native CSV export: serializes session metrics into structured spreadsheet format using `tkinter.filedialog`.",
        "Constructed the 7-category preference center in `ui/screens/settings_screen.py` (`GENERAL`, `TYPING`, `APPEARANCE`, `ACCESSIBILITY`, `AUDIO`, `DATA`, `ABOUT`).",
        "Implemented safe settings reset: restores default preferences while strictly safeguarding user session history in `data/history.json`.",
        "Developed cross-platform offline audio engine in `ui/audio_manager.py` with native fallbacks (Windows `winsound`, macOS `afplay`, Linux `aplay`).",
        "Configured PyInstaller standalone executable bundling in `build_exe.py`, packaging binary assets, icons, and sounds into a single `.exe`.",
        "Developed automated backend and persistence unit tests in `tests/test_v21_improvements.py`."
    ]
    for task in biswa_tasks:
        add_p(task, bold_prefix="•  ", space_after=2)

    add_p("`ui/storage.py`, `ui/audio_manager.py`, `ui/screens/results_screen.py`, `ui/screens/history_screen.py`, `ui/screens/settings_screen.py`, `build_exe.py`, `tests/test_v21_improvements.py`.", bold_prefix="Primary Source Modules Handled: ")
    add_p("Atomic I/O file transactions, JSON schema serialization, CSV data parsing, statistical dispersion (variance, std dev, CV), spline curve interpolation, audio frequency attenuation, PyInstaller spec packaging.", bold_prefix="Technical Concepts & Algorithms: ")
    add_p("An enterprise-grade offline persistence and analytics engine that ensures 100% data integrity, provides actionable typographical feedback, and enables seamless data portability via CSV export.", bold_prefix="Deliverables & Contribution: ")

    # 4.3 Shivansh
    add_sub_heading("4.3 Member 3: Shivansh Bansal")
    add_p("Frontend Development, UI/UX Design and Application Architecture", bold_prefix="Assigned Role: ")
    add_p(
        "Member 3 owned the graphical user interface architecture, the 'Midnight Minimal' visual design system, custom canvas widget components, "
        "application lifecycle routing, high-DPI display scaling, and interface visual verification. This ensured that TypeRush presents a unified, "
        "academically rigorous, modern desktop appearance that never distracts the typist's focus."
    )

    add_p("Specific Implementation Responsibilities:", bold_prefix="Detailed Responsibilities:\n")
    shivansh_tasks = [
        "Constructed the central application controller `TypeRushApp` (`tk.Tk`) in `ui/app.py` managing window geometry, minsize, and screen routing.",
        "Engineered Windows high-DPI scaling bootstrap in `main.py` utilizing `ctypes.windll.shcore.SetProcessDpiAwareness(1)` for Per-Monitor V2 awareness.",
        "Defined the centralized 'Midnight Minimal' design system in `ui/theme.py`, standardizing palette tokens (`#0B0D12` foundation, `#181D29` surfaces).",
        "Standardized typography constants across Cascadia Code, Consolas, and Segoe UI with responsive point size tiers.",
        "Authored the custom canvas component library in `ui/components.py`, creating `RoundedButton`, `CardFrame`, `HeaderBar`, and `StatCard`.",
        "Implemented smooth hover-state transitions, active click depress visual feedback, and keyboard focus outlines on custom canvas widgets.",
        "Engineered the central `AnimationManager` in `ui/animations.py` using non-blocking `root.after()` callbacks and easing interpolation.",
        "Constructed the Home Dashboard in `ui/screens/home_screen.py` with Quick-Start challenge cards, duration selectors, and Personal Best badges.",
        "Designed the high-contrast navigation sidebar with instantaneous switching between Home, History, and Settings views.",
        "Created the abstract base screen class `BaseScreen` in `ui/screens/base_screen.py` establishing lifecycle hooks (`on_enter`, `on_leave`).",
        "Eliminated 3-edition visual clutter (Basic, Pleasant, Soundscape) to unify the entire application under the Midnight Minimal aesthetic.",
        "Constructed the wide 220px two-column settings navigation layout to eliminate label truncation across varying screen resolutions.",
        "Developed the automated headless visual capture tool `capture_v21_visuals.py` to record verified 1200x800 screenshots of all application screens.",
        "Authored UI layout and responsiveness regression tests in `tests/test_v21_redesign.py`."
    ]
    for task in shivansh_tasks:
        add_p(task, bold_prefix="•  ", space_after=2)

    add_p("`ui/app.py`, `ui/theme.py`, `ui/backgrounds.py`, `ui/components.py`, `ui/animations.py`, `ui/screens/base_screen.py`, `ui/screens/home_screen.py`, `main.py`, `capture_v21_visuals.py`, `tests/test_v21_redesign.py`.", bold_prefix="Primary Source Modules Handled: ")
    add_p("Event-driven GUI architecture, High-DPI Windows graphics API interop, Bezier curve rendering, canvas drawing primitives, animation easing curves, component-based UI design, stateful view routing.", bold_prefix="Technical Concepts & Algorithms: ")
    add_p("A modern, visually cohesive desktop interface delivering 60 FPS visual smoothness, sharp typography, intuitive navigation, and zero visual distraction during high-speed typing benchmarking.", bold_prefix="Deliverables & Contribution: ")

    # --------------------------------------------------------------------------
    # SECTION 5 – INDIVIDUAL TECHNICAL CONTRIBUTIONS
    # --------------------------------------------------------------------------
    add_sec_heading("Individual Technical Contributions", "5")
    add_p(
        "This section details the concrete technical and algorithmic implementations authored by each member, highlighting the "
        "mathematical rigor, architectural design patterns, and engineering principles realized in TypeRush 2.1."
    )

    # 5.1 Abhiram Technical
    add_sub_heading("5.1 Algorithmic Foundations & Core Typing Interaction (Abhiram)")
    add_p(
        "A central flaw in naive typing applications is the 'cascade failure' problem: comparing an input string directly against a target string "
        "using absolute character indexes causes a single omitted or inserted letter at index i to offset all subsequent characters, resulting "
        "in 0% accuracy for the remainder of the passage. Abhiram resolved this by developing a two-level alignment architecture in `ui/alignment.py`."
    )
    add_p(
        "1. Two-Level Segmentation & Spacebar Isolation: The target text and user inputs are tokenized into discrete word objects storing exact "
        "character spans. Keystrokes are strictly bound to the active word index. Pressing the spacebar evaluates and commits the active word, "
        "advancing the target word index by exactly one. An error in word N is mathematically isolated—it is impossible for a typo to shift word N+1.",
        bold_prefix="•  "
    )
    add_p(
        "2. Dynamic Programming Levenshtein Distance: To provide granular mistake diagnostics on completed words, Abhiram implemented the "
        "Wagner-Fischer dynamic programming matrix algorithm. Given target word T of length M and typed word U of length N, a matrix D is constructed "
        "where D(i, j) represents the minimum edit operations (substitutions, insertions, deletions) to transform prefix T[1..i] into U[1..j]. "
        "By backtracking through the optimal edit path, typos are precisely categorized into Substitutions (wrong key), Omissions (skipped key), "
        "and Insertions (extra key).",
        bold_prefix="•  "
    )
    add_p(
        "3. Mathematical Telemetry Formulation: In `ui/scoring.py`, Gross WPM is computed using the international standard word length of 5 keystrokes: "
        "Gross WPM = (Keystrokes / 5.0) / (Elapsed Seconds / 60.0). Net WPM enforces an error penalty: Net WPM = max(0, Gross WPM - (Uncorrected Errors / Minutes)). "
        "Live telemetry is polled asynchronously every 100ms via `root.after()`, guaranteeing sub-millisecond calculation updates.",
        bold_prefix="•  "
    )
    add_p(
        "4. Native Insertion Caret Metric Synchronization: Earlier versions of the app used an overlay `tk.Frame` that drifted and overlapped letters. "
        "Abhiram replaced this by synchronizing the native Tkinter insertion cursor directly via `text_display.bbox(f'1.0 + {cursor_pos} chars')`. "
        "The caret reads the physical font geometry from the X11/Win32 font engine, positioning the 2px purple caret cleanly between glyphs.",
        bold_prefix="•  "
    )

    # 5.2 Biswa Technical
    add_sub_heading("5.2 Data Persistence, Analytics & Backend Engineering (Biswa)")
    add_p(
        "Data integrity and statistical depth are critical for longitudinal skill development. Biswa engineered the persistence and analytics "
        "subsystems in `ui/storage.py`, `ui/screens/results_screen.py`, and `ui/audio_manager.py`."
    )
    add_p(
        "1. Atomic File Transactions: Standard file writing (`open(file, 'w')`) creates a race condition where a crash or power failure midway through "
        "writing leaves an empty or corrupt JSON file, permanently destroying user session history. Biswa implemented an atomic transaction pattern: "
        "data is serialized to a temporary file (`history.json.tmp`), flushed to disk, and then atomically swapped over the primary file using `os.replace()`. "
        "Because `os.replace()` is an atomic filesystem primitive on POSIX and NTFS, the history file is guaranteed never to become corrupted.",
        bold_prefix="•  "
    )
    add_p(
        "2. Statistical Telemetry & Consistency Modeling: Beyond basic averages, Biswa implemented rhythm consistency modeling. Typing consistency is computed "
        "via the standard deviation (σ) of interval keystroke velocity: σ = sqrt( (1/N) * Σ (w_i - mean_w)^2 ). A consistency rating (High Stability, Steady, "
        "Fluctuating) is derived from the Coefficient of Variation (CV = σ / mean_w), providing typists with objective feedback on rhythm and hesitation.",
        bold_prefix="•  "
    )
    add_p(
        "3. Dynamic Canvas Spline Graphing: In `ui/screens/results_screen.py`, Biswa created a custom Canvas spline graph that plots instantaneous velocity "
        "across 1-second intervals. The graph normalizes arbitrary data ranges, renders subtle horizontal gridlines, draws a smooth anti-aliased velocity spline, "
        "and highlights peak velocity points with coordinate callouts.",
        bold_prefix="•  "
    )
    add_p(
        "4. Cross-Platform Native Audio Architecture: In `ui/audio_manager.py`, Biswa developed an offline audio system that avoids heavyweight third-party "
        "dependencies (pygame, simpleaudio). On Windows, it leverages `winsound.PlaySound` with asynchronous flags (`SND_ASYNC | SND_FILENAME`). "
        "On macOS and Linux, it spawns background sub-processes using `afplay` or `aplay`, ensuring zero audio stutter and zero GUI thread blocking.",
        bold_prefix="•  "
    )

    # 5.3 Shivansh Technical
    add_sub_heading("5.3 Frontend Architecture, Design Tokens & Animation (Shivansh)")
    add_p(
        "Desktop productivity applications must provide responsive 60 FPS graphics, clear visual contrast, and high-DPI scaling. "
        "Shivansh engineered the graphical foundation in `ui/app.py`, `ui/theme.py`, `ui/components.py`, and `ui/animations.py`."
    )
    add_p(
        "1. Windows High-DPI Scaling Interop: Unaware Tkinter applications render blurry and pixelated on modern 1080p, 2K, and 4K displays because Windows "
        "stretches the bitmap. Shivansh resolved this in `main.py` using `ctypes` foreign function calls: `ctypes.windll.shcore.SetProcessDpiAwareness(1)` "
        "enables Per-Monitor V2 DPI awareness, instructing the operating system to render typography and canvas curves at physical hardware resolution.",
        bold_prefix="•  "
    )
    add_p(
        "2. Centralized Midnight Minimal Token System: In `ui/theme.py`, Shivansh established an atomic design token architecture. Surface colors "
        "(`BG_PRIMARY = #0B0D12`, `SURFACE_DEFAULT = #181D29`), typography scales (`FONT_FAMILY_MONO = Cascadia Code`), corner radii (`RADIUS_LG = 12px`), "
        "and semantic states (`ACCENT_PRIMARY = #38BDF8`, `TEXT_MUTED = #858D9E`) are centrally defined. Modifying a theme token propagates instantly across all screens.",
        bold_prefix="•  "
    )
    add_p(
        "3. Custom Canvas Rounded Widget Library: Tkinter standard buttons (`tk.Button`) do not support arbitrary corner radii, smooth hover transitions, "
        "or multi-line badges in dark mode. Shivansh engineered `RoundedButton`, `CardFrame`, and `StatCard` in `ui/components.py` using `tk.Canvas` drawing primitives. "
        "These widgets draw anti-aliased rounded rectangles using polygonal arcs, handle `<Enter>` and `<Leave>` hover states, and provide visual tactile feedback on click.",
        bold_prefix="•  "
    )
    add_p(
        "4. Non-Blocking Animation Scheduler: In `ui/animations.py`, Shivansh built `AnimationManager` utilizing quadratic and cubic easing functions: "
        "y = t * t * (3 - 2 * t). Transitions (screen fades, card hover expansions) interpolate properties across 16ms frames via `root.after(16, step)`. "
        "This achieves smooth 60 FPS transitions without introducing background Python threads that could destabilize Tkinter's single-threaded event loop.",
        bold_prefix="•  "
    )

    # --------------------------------------------------------------------------
    # SECTION 6 – MODULE INTERACTION AND INTEGRATION
    # --------------------------------------------------------------------------
    add_sec_heading("Module Interaction and Integration", "6")
    add_p(
        "TypeRush functions through a synchronized data flow spanning all three engineering domains. "
        "The end-to-end operational lifecycle follows an interconnected 5-step pipeline:"
    )

    flow_steps = [
        ("Step 1: Presentation Initialization (Shivansh): ",
         "The application bootstraps through `main.py`, configuring Windows High-DPI awareness, instantiating `TypeRushApp`, "
         "and loading the `HomeScreen` dashboard with Midnight Minimal theme tokens and navigation bars."),
        ("Step 2: Configuration & Content Preparation (Abhiram / Shivansh): ",
         "The typist selects Difficulty and Duration on the Quick-Start card. When 'Start Typing Test' is clicked, `TypeRushApp` "
         "swaps to `TypingScreen`, which requests a non-repeating curated text passage from Abhiram's `ContentDeckGenerator`."),
        ("Step 3: Real-Time Typing & Alignment Loop (Abhiram): ",
         "As the typist enters keystrokes, `TypingScreen` captures `<Key>` events asynchronously. Abhiram's `TypingAlignmentEngine` "
         "compares characters in real time, applies green/red text tags, positions the native caret, commits words via spacebar without cascading, "
         "and updates live Gross/Net WPM telemetry."),
        ("Step 4: Persistence & Data Logging (Biswa): ",
         "Upon timer expiry, `TypingScreen` compiles the raw metrics into a `SessionTelemetry` payload and invokes Biswa's `StorageManager`. "
         "The session is appended atomically to `data/history.json`, user personal records are recalculated, and audio triggers play completion tones."),
        ("Step 5: Diagnostic Presentation & Historical Archiving (Biswa / Shivansh): ",
         "`TypeRushApp` navigates to `ResultsScreen`, rendering Biswa's telemetry grid, mistake breakdown, and velocity spline graph within Shivansh's "
         "custom card frames. The user can review errors, export to CSV, or browse chronological timelines on `HistoryScreen`.")
    ]
    for bold_txt, norm_txt in flow_steps:
        add_p(norm_txt, bold_prefix=bold_txt, space_after=3)

    # Embed Architecture Diagram
    add_sub_heading("6.1 Multi-Tier Architecture & Data Flow Diagram")
    workflow_img_path = os.path.join(os.path.dirname(__file__), "contribution_workflow.png")
    if os.path.exists(workflow_img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(workflow_img_path, width=Inches(6.5))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        run_cap = p_cap.add_run("Figure 6.1: Multi-tier architectural integration and inter-module collaboration flow in TypeRush 2.1.")
        run_cap.font.name = "Segoe UI"
        run_cap.font.size = Pt(8.5)
        run_cap.font.italic = True
        run_cap.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # --------------------------------------------------------------------------
    # SECTION 7 – DIVISION OF RESPONSIBILITIES MATRIX
    # --------------------------------------------------------------------------
    add_sec_heading("Division of Responsibilities Matrix", "7")
    add_p(
        "Table 7.1 delineates primary feature ownership and inter-member collaboration across all major functional subsystems of TypeRush 2.1."
    )

    t7 = doc.add_table(rows=21, cols=4)
    t7.alignment = WD_TABLE_ALIGNMENT.CENTER
    matrix_data = [
        ["Subsystem / Component", "Primary Lead Owner", "Secondary Contributor", "Collaboration & Scope of Integration"],
        ["Levenshtein Distance Algorithm", "B. P. V. S. Abhiram", "Biswa Prakash Rout", "Algorithm written by Abhiram; output consumed by Biswa's mistake review table."],
        ["Cascade-Immune Word Segmentation", "B. P. V. S. Abhiram", "Shivansh Bansal", "Alignment engine built by Abhiram; integrated into Shivansh's typing screen UI."],
        ["Gross & Net WPM Formulas", "B. P. V. S. Abhiram", "Biswa Prakash Rout", "Calculations codified in scoring.py; logged and graphed in Biswa's analytics."],
        ["Typing Accuracy & Consistency", "B. P. V. S. Abhiram", "Biswa Prakash Rout", "Standard deviation formulas implemented by Abhiram; displayed in results card."],
        ["Real-Time Character Highlighting", "B. P. V. S. Abhiram", "Shivansh Bansal", "Text tagging logic designed by Abhiram; styled using Shivansh's color tokens."],
        ["Native Caret Metric Positioning", "B. P. V. S. Abhiram", "Shivansh Bansal", "Bounding-box tracking by Abhiram; integrated into canvas viewport by Shivansh."],
        ["Curated Text Deck Generator", "B. P. V. S. Abhiram", "Biswa Prakash Rout", "35+ sentence decks per tier by Abhiram; seeded from JSON storage."],
        ["Atomic JSON Persistence", "Biswa Prakash Rout", "B. P. V. S. Abhiram", "Thread-safe .tmp writing by Biswa; receives telemetry dataclass from Abhiram."],
        ["Corrupted File Auto-Recovery", "Biswa Prakash Rout", "Shivansh Bansal", "Storage recovery safeguards by Biswa; displays non-intrusive UI alerts."],
        ["Diagnostic Results Dashboard", "Biswa Prakash Rout", "Shivansh Bansal", "Telemetry logic and metrics grid by Biswa; framed inside Shivansh's card widgets."],
        ["Velocity Spline Progression Graph", "Biswa Prakash Rout", "Shivansh Bansal", "Data point plotting and curve math by Biswa; styled using Shivansh's palette."],
        ["Chronological History Archive", "Biswa Prakash Rout", "Shivansh Bansal", "Session querying & filtering by Biswa; navigation and layout by Shivansh."],
        ["One-Click Native CSV Export", "Biswa Prakash Rout", "B. P. V. S. Abhiram", "CSV serialization by Biswa; extracts standardized fields from session schema."],
        ["Offline Audio Soundscapes", "Biswa Prakash Rout", "B. P. V. S. Abhiram", "Audio architecture by Biswa; triggered on key taps and completion events by Abhiram."],
        ["7-Category Preferences Center", "Biswa Prakash Rout", "Shivansh Bansal", "Settings read/write handlers by Biswa; two-column UI layout designed by Shivansh."],
        ["Application Bootstrap & Shell", "Shivansh Bansal", "Biswa Prakash Rout", "Main window controller by Shivansh; initializes storage and audio managers."],
        ["Windows High-DPI Scaling", "Shivansh Bansal", "B. P. V. S. Abhiram", "Win32 ctypes bootstrap by Shivansh; ensures crisp font rendering for Abhiram's text."],
        ["Midnight Minimal Design Tokens", "Shivansh Bansal", "Biswa Prakash Rout", "Color and typography palette by Shivansh; applied across all screens and graphs."],
        ["Custom Canvas Widget Library", "Shivansh Bansal", "B. P. V. S. Abhiram", "RoundedButton and CardFrame by Shivansh; hosts Abhiram's typing text viewport."],
        ["Animation & Easing Scheduler", "Shivansh Bansal", "Biswa Prakash Rout", "Non-blocking after() scheduler by Shivansh; smooths screen navigation."],
        ["Standalone Executable Build", "Biswa Prakash Rout", "Shivansh Bansal", "PyInstaller spec script by Biswa; bundles Shivansh's icons and background assets."]
    ]
    for r_idx, row in enumerate(t7.rows):
        for c_idx, val in enumerate(matrix_data[r_idx]):
            row.cells[c_idx].paragraphs[0].text = val
    format_table_headers(t7, [1.8, 1.4, 1.3, 2.0])

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # --------------------------------------------------------------------------
    # SECTION 8 – TOOLS AND TECHNOLOGIES
    # --------------------------------------------------------------------------
    add_sec_heading("Tools and Technologies", "8")
    add_p(
        "TypeRush was engineered adhering strictly to standard library purity, avoiding unstable third-party packages to ensure immediate "
        "cross-platform academic reproducibility. Table 8.1 catalogs the verified tools, libraries, and runtime environments utilized."
    )

    t8 = doc.add_table(rows=9, cols=3)
    t8.alignment = WD_TABLE_ALIGNMENT.CENTER
    tools_data = [
        ["Category", "Technology / Module", "Specific Purpose in TypeRush"],
        ["Programming Language", "Python 3.12 / 3.14 (64-bit)", "Primary application runtime, object-oriented design, dynamic data typing."],
        ["Graphical User Interface", "Tkinter & ttk Standard Library", "tk.Canvas (custom widgets, graphs), tk.Text (authoritative passage), ttk.Combobox."],
        ["Data Persistence & I/O", "json, csv, os, uuid, datetime", "Atomic JSON storage, unique session UUIDs, timestamping, and native CSV export."],
        ["Mathematics & Algorithms", "math, re, custom Levenshtein", "WPM formulas, variance, standard deviation, regex tokenization, edit distance."],
        ["System & High-DPI Interop", "ctypes (windll.shcore, user32)", "Windows Per-Monitor V2 High-DPI scaling bootstrap, physical display metrics."],
        ["Audio Engine", "winsound, subprocess (afplay, aplay)", "Low-latency offline WAV sound feedback (key taps, completion, soft errors)."],
        ["Quality Assurance", "unittest Standard Library", "91 automated unit and regression tests verifying engine, scoring, and storage."],
        ["Deployment & Packaging", "PyInstaller (build_exe.py)", "Single-command bundling of scripts, audio assets, and icons into standalone .exe."]
    ]
    for r_idx, row in enumerate(t8.rows):
        for c_idx, val in enumerate(tools_data[r_idx]):
            row.cells[c_idx].paragraphs[0].text = val
    format_table_headers(t8, [1.5, 2.0, 3.0])

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # --------------------------------------------------------------------------
    # SECTION 9 – CHALLENGES AND PROBLEM SOLVING
    # --------------------------------------------------------------------------
    add_sec_heading("Technical Challenges and Problem Solving", "9")
    add_p(
        "During the development of TypeRush 2.1, the team encountered and resolved complex engineering challenges spanning algorithmic accuracy, "
        "real-time input synchronization, GUI rendering performance, and file safety. Table 9.1 highlights these challenges and their solutions."
    )

    t9 = doc.add_table(rows=7, cols=4)
    t9.alignment = WD_TABLE_ALIGNMENT.CENTER
    challenges_data = [
        ["Technical Challenge", "Impact on System", "Engineering Solution Implemented", "Lead Engineer"],
        ["Cascading Error Desynchronization", "A single skipped character caused all subsequent words to be marked 100% incorrect.", "Implemented two-level tokenization in `ui/alignment.py` with spacebar word commitment, strictly isolating errors to word N.", "B. P. V. S. Abhiram"],
        ["Caret Jitter & Glyph Overlap", "Overlay tk.Frame carets drifted during word wrapping and overlapped characters.", "Replaced overlay with Tkinter's native insertion cursor synchronized via `text_display.bbox()` physical font metrics.", "B. P. V. S. Abhiram"],
        ["Corrupted JSON on Interrupted Writes", "Application crash during file write left blank or corrupted `history.json` files.", "Implemented atomic transaction pattern in `ui/storage.py` writing to `.tmp` file and replacing atomically via `os.replace()`.", "Biswa Prakash Rout"],
        ["Audio Lag & Thread Blocking", "Playing sound effects caused micro-stutters during high-speed typing (60+ WPM).", "Utilized asynchronous flags (`SND_ASYNC`) in `winsound` and detached subprocess pipes on macOS/Linux in `ui/audio_manager.py`.", "Biswa Prakash Rout"],
        ["High-DPI Blurry Font Rendering", "Windows scaled 1080p/4K displays using bitmap stretching, blurring fonts and canvas.", "Added Per-Monitor V2 DPI awareness bootstrap in `main.py` using `ctypes.windll.shcore.SetProcessDpiAwareness(1)`.", "Shivansh Bansal"],
        ["Navigation Label Text Truncation", "Settings category titles were truncated on compact laptop resolutions.", "Re-engineered two-column settings layout in `ui/screens/settings_screen.py` with a dedicated 220px wide navigation sidebar.", "Shivansh Bansal"]
    ]
    for r_idx, row in enumerate(t9.rows):
        for c_idx, val in enumerate(challenges_data[r_idx]):
            row.cells[c_idx].paragraphs[0].text = val
    format_table_headers(t9, [1.5, 1.5, 2.3, 1.2])

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # --------------------------------------------------------------------------
    # SECTION 10 – CONCLUSION
    # --------------------------------------------------------------------------
    add_sec_heading("Conclusion", "10")
    add_p(
        "The collaborative development of TypeRush 2.1 exemplifies successful academic software engineering, demonstrating how clean modularization, "
        "rigorous separation of concerns, and mutual accountability enable three student engineers to deliver an enterprise-grade desktop productivity tool. "
        "By avoiding heavyweight web wrappers and third-party dependencies, the team authored a lean, highly responsive, distraction-free typing benchmark "
        "that executes natively on standard Python 3.12+ across Windows, macOS, and Linux."
    )
    add_p(
        "Each team member contributed vital domain expertise: Boddupalli Phani Venkata Sri Abhiram engineered the core algorithmic typing loop, "
        "cascade-immune Levenshtein alignment, and standardized performance telemetry; Biswa Prakash Rout delivered an atomic, corrupt-safe persistence "
        "layer, interactive canvas velocity graphing, session history management, and cross-platform audio; and Shivansh Bansal designed the modern "
        "'Midnight Minimal' visual system, High-DPI Windows graphics bootstrap, reusable custom canvas widgets, and application shell router. "
        "Together, these synchronized modules produce a cohesive, academically validated desktop application validated by 91 passing automated unit tests."
    )

    # Sign-off box
    add_callout_box(
        doc,
        "REPORT AUTHENTICATION & SUBMISSION APPROVAL",
        "This Work Distribution and Individual Contributions Report accurately documents the implemented source code, "
        "architectural responsibilities, and technical contributions of all three team members for TypeRush 2.1.\n\n"
        "1. Boddupalli Phani Venkata Sri Abhiram (RA2511026010355) — Core Typing Engine & Algorithms Lead\n"
        "2. Biswa Prakash Rout (RA2511026010339) — Backend, Persistence & Analytics Lead\n"
        "3. Shivansh Bansal (RA2511026010332) — Frontend Architecture & UI/UX Design Lead\n\n"
        "Verified Repository: https://github.com/Abhiram1108/TypeRush  •  SRMIST  •  November 2026",
        border_color="C7A008",
        bg_color="F8FAFC"
    )

    # Save documents
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    out_root = os.path.join(root_dir, "TypeRush_Team_Work_Distribution_and_Contributions_Report.docx")
    out_report = os.path.join(root_dir, "report", "TypeRush_Team_Work_Distribution_and_Contributions_Report.docx")

    doc.save(out_root)
    doc.save(out_report)
    print(f"Report saved to:\n  1. {out_root}\n  2. {out_report}")

if __name__ == "__main__":
    build_document()
