import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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

def format_table(table, col_widths=None):
    header_row = table.rows[0]
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

def integrate_contributions():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    report_docx = os.path.join(root_dir, "report", "TypeRush_Project_Report_APP.docx")
    out_final_root = os.path.join(root_dir, "TypeRush_Final_Project_Report.docx")
    out_final_report = os.path.join(root_dir, "report", "TypeRush_Final_Project_Report.docx")

    doc = docx.Document(report_docx)

    # 1. Update existing sections: Section 8 -> Section 9, Section 9 -> Section 10
    target_conclusion_p = None
    for p in doc.paragraphs:
        if p.text.startswith("8. Conclusion and Future Scope"):
            p.text = "9. Conclusion and Future Scope"
            target_conclusion_p = p
        elif p.text.startswith("9. References"):
            p.text = "10. References"

    if not target_conclusion_p:
        raise RuntimeError("Could not locate '8. Conclusion and Future Scope' in document!")

    # Helper function to insert paragraph before target_conclusion_p
    def insert_p(text="", style="Normal", space_before=0, space_after=5, bold_prefix=None):
        new_p = target_conclusion_p.insert_paragraph_before(style=style)
        new_p.paragraph_format.space_before = Pt(space_before)
        new_p.paragraph_format.space_after = Pt(space_after)
        new_p.paragraph_format.line_spacing = 1.15
        new_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            r_pre = new_p.add_run(bold_prefix)
            r_pre.font.name = "Segoe UI"
            r_pre.font.bold = True
            r_pre.font.color.rgb = RGBColor(0x00, 0x2B, 0x49)
        if text:
            r_txt = new_p.add_run(text)
            r_txt.font.name = "Segoe UI"
            r_txt.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        return new_p

    def insert_heading(title, level=1):
        style_name = "Heading 1" if level == 1 else ("Heading 2" if level == 2 else "Heading 3")
        new_p = target_conclusion_p.insert_paragraph_before(style=style_name)
        new_p.paragraph_format.space_before = Pt(14 if level == 1 else (10 if level == 2 else 7))
        new_p.paragraph_format.space_after = Pt(4 if level == 1 else 3)
        new_p.paragraph_format.keep_with_next = True
        r = new_p.add_run(title)
        r.font.name = "Segoe UI"
        r.font.bold = True
        if level == 1:
            r.font.size = Pt(14)
            r.font.color.rgb = RGBColor(0x00, 0x2B, 0x49)
        elif level == 2:
            r.font.size = Pt(11.5)
            r.font.color.rgb = RGBColor(0x03, 0x4D, 0xA1)
        else:
            r.font.size = Pt(10.5)
            r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        return new_p

    def insert_table(num_rows, num_cols):
        tbl = doc.add_table(rows=num_rows, cols=num_cols)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        target_conclusion_p._p.addprevious(tbl._tbl)
        return tbl

    # ==========================================================================
    # INSERT SECTION 8: TEAM MEMBERS AND INDIVIDUAL CONTRIBUTIONS
    # ==========================================================================
    insert_heading("8. Team Members and Individual Contributions", level=1)
    insert_p(
        "TypeRush 2.1 was designed and developed collaboratively by a team of three undergraduate software engineers "
        "for the Advanced Programming Practice (21CSC203P) laboratory curriculum at SRM Institute of Science and Technology. "
        "To achieve modularity, architectural cleanliness, and strict adherence to standard library Python without external web bloat, "
        "responsibilities were divided across three specialized domains: (1) Core Algorithmic Typing Engine, (2) Backend Data Persistence "
        "& Analytics, and (3) Frontend Architecture & UI/UX Design. The following subsections detail the team composition, verified "
        "source code ownership, individual technical contributions, and inter-module integration."
    )

    # --------------------------------------------------------------------------
    # 8.1 Team Composition
    # --------------------------------------------------------------------------
    insert_heading("8.1 Team Composition", level=2)
    insert_p(
        "The project engineering roles were established based on algorithmic, persistence, and interface specializations. "
        "Table 8.1 summarizes the team members, assigned engineering roles, and major functional areas."
    )

    t_comp = insert_table(num_rows=4, num_cols=4)
    comp_data = [
        ["S. No.", "Team Member & Registration No.", "Assigned Engineering Role", "Major Functional Responsibility"],
        ["1", "Boddupalli Phani Venkata Sri Abhiram\n(RA2511026010355)", "Core Typing Engine & Algorithm Development", "Core typing loop, Levenshtein word alignment, cascade immunity, gross/net WPM equations, live character tagging, and native caret synchronization."],
        ["2", "Biswa Prakash Rout\n(RA2511026010339)", "Backend Development, Data Management & Analytics", "Atomic JSON persistence, session history management, results telemetry, velocity spline graph, CSV export, audio engine, and standalone executable packaging."],
        ["3", "Shivansh Bansal\n(RA2511026010332)", "Frontend Development, UI/UX Design & Architecture", "Midnight Minimal design system, application shell controller, Windows High-DPI scaling bootstrap, reusable canvas widget library, animation scheduler, and visual verification."]
    ]
    for r_idx, row in enumerate(t_comp.rows):
        for c_idx, val in enumerate(comp_data[r_idx]):
            row.cells[c_idx].paragraphs[0].text = val
    format_table(t_comp, [0.6, 2.0, 1.8, 2.1])
    insert_p(space_after=4)

    # --------------------------------------------------------------------------
    # 8.2 Individual Contributions
    # --------------------------------------------------------------------------
    insert_heading("8.2 Individual Contributions & Technical Responsibilities", level=2)

    # 8.2.1 Abhiram
    insert_heading("8.2.1 Boddupalli Phani Venkata Sri Abhiram – Core Typing Engine and Algorithm Development", level=3)
    insert_p("Core Typing Engine, Algorithm Development and Real-Time Typing Interaction", bold_prefix="Assigned Role: ")
    insert_p(
        "Boddupalli Phani Venkata Sri Abhiram led the design and implementation of TypeRush's core algorithmic and interaction engine. "
        "His primary objective was to eliminate the notorious 'cascade failure' bug inherent to naive typing testers, formulate mathematically "
        "accurate typing telemetry, and maintain sub-millisecond keystroke responsiveness across intensive typing sessions."
    )
    insert_p("Technical Responsibilities & Implemented Features:", bold_prefix="Detailed Technical Responsibilities:\n")
    abhiram_bullets = [
        "Architected the single authoritative continuous text stream widget in `ui/screens/typing_screen.py`.",
        "Engineered the `TypingAlignmentEngine` in `ui/alignment.py` to tokenize target and input passages into exact character bounds.",
        "Implemented the dynamic programming Levenshtein distance matrix algorithm to classify typographical discrepancies into substitutions, omissions, and insertions.",
        "Developed cascade-resistant word-level segmentation: typos in word N are strictly contained and never invalidate word N+1.",
        "Engineered case-insensitive character matching logic: accepts standard casing variants while strictly enforcing punctuation verification.",
        "Formulated standardized Gross Words Per Minute: Gross WPM = (total_keystrokes / 5.0) / elapsed_minutes.",
        "Formulated standardized Net Words Per Minute with error penalties: Net WPM = max(0, Gross WPM - (errors / elapsed_minutes)).",
        "Formulated character precision accuracy: Accuracy % = (correct_characters / total_keystrokes) * 100.",
        "Formulated rhythm consistency metrics using standard deviation (σ) and coefficient of variation of interval velocities.",
        "Implemented non-blocking Tkinter `<Key>` keystroke event listeners with sub-millisecond evaluation latency.",
        "Built protected `<space>` word commitment logic: commits active words, validates spelling, advances pointer, and ignores empty spaces.",
        "Implemented within-word `<BackSpace>` editing: allows typists to correct typos before committing without pointer desynchronization.",
        "Engineered real-time visual character coloring (`correct`, `incorrect`, `untyped`, `active_bg`) directly on the `tk.Text` rendering pipeline.",
        "Implemented native vertical insertion caret tracking positioned dynamically via font bounding-box metrics (`text_display.bbox()`).",
        "Curated 140+ coherent sentences across four vocabulary tiers (Easy, Medium, Hard, Expert) with rolling exclusion decks in `ui/content_generator.py`.",
        "Authored automated typing rebuild test suites in `tests/test_v21_typing_rebuild.py` and `tests/run_v21_typing_rebuild_demo.py`."
    ]
    for b in abhiram_bullets:
        insert_p(b, bold_prefix="•  ", space_after=2)

    insert_p("`ui/alignment.py`, `ui/scoring.py`, `ui/content_generator.py`, `ui/screens/typing_screen.py`, `tests/test_v21_typing_rebuild.py`, `tests/run_v21_typing_rebuild_demo.py`.", bold_prefix="Verified Source Modules: ")
    insert_p(
        "Abhiram's work provides the foundational computational engine of TypeRush. Without his cascade-immune alignment algorithm "
        "and real-time keystroke processing pipeline, the application could not function as an accurate or fair benchmarking tool.",
        bold_prefix="Contribution to Overall Application: "
    )

    # 8.2.2 Biswa
    insert_heading("8.2.2 Biswa Prakash Rout – Backend Development, Data Management and Performance Analytics", level=3)
    insert_p("Backend Development, Data Management and Performance Analytics", bold_prefix="Assigned Role: ")
    insert_p(
        "Biswa Prakash Rout designed and constructed the persistence architecture, analytical telemetry dashboards, historical session "
        "archive, offline audio synthesis, and deployment toolchain. His primary objective was to guarantee 100% data integrity, ensure that "
        "historical session records cannot be lost or corrupted by application interruptions, and provide comprehensive post-test diagnostics."
    )
    insert_p("Technical Responsibilities & Implemented Features:", bold_prefix="Detailed Technical Responsibilities:\n")
    biswa_bullets = [
        "Architected the local data persistence layer in `ui/storage.py` utilizing atomic file operations (`.tmp` write and `os.replace`).",
        "Engineered safe file recovery protocols: automatically recovers from missing, blank, or corrupted JSON files without crashing.",
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
    for b in biswa_bullets:
        insert_p(b, bold_prefix="•  ", space_after=2)

    insert_p("`ui/storage.py`, `ui/audio_manager.py`, `ui/screens/results_screen.py`, `ui/screens/history_screen.py`, `ui/screens/settings_screen.py`, `build_exe.py`, `tests/test_v21_improvements.py`.", bold_prefix="Verified Source Modules: ")
    insert_p(
        "Biswa's backend infrastructure transforms TypeRush from a simple typing test into an analytical productivity tool. His atomic persistence "
        "guarantees personal data security, while the diagnostic charts and CSV export empower typists to track progress over time.",
        bold_prefix="Contribution to Overall Application: "
    )

    # 8.2.3 Shivansh
    insert_heading("8.2.3 Shivansh Bansal – Frontend Development, UI/UX Design and Application Architecture", level=3)
    insert_p("Frontend Development, UI/UX Design and Application Architecture", bold_prefix="Assigned Role: ")
    insert_p(
        "Shivansh Bansal architected the overall graphical interface, the 'Midnight Minimal' visual identity, the custom canvas widget component "
        "library, screen navigation routing, and Windows high-DPI display scaling. His primary objective was to deliver a cohesive, modern dark-themed "
        "desktop interface that operates at 60 FPS without graphical lag or cognitive distraction."
    )
    insert_p("Technical Responsibilities & Implemented Features:", bold_prefix="Detailed Technical Responsibilities:\n")
    shivansh_bullets = [
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
    for b in shivansh_bullets:
        insert_p(b, bold_prefix="•  ", space_after=2)

    insert_p("`ui/app.py`, `ui/theme.py`, `ui/backgrounds.py`, `ui/components.py`, `ui/animations.py`, `ui/screens/base_screen.py`, `ui/screens/home_screen.py`, `main.py`, `capture_v21_visuals.py`, `tests/test_v21_redesign.py`.", bold_prefix="Verified Source Modules: ")
    insert_p(
        "Shivansh's frontend architecture gives TypeRush its identity and desktop responsiveness. His high-DPI bootstrap ensures razor-sharp typography, "
        "while the custom canvas components provide a premium, modern feel without relying on bloated external UI libraries.",
        bold_prefix="Contribution to Overall Application: "
    )

    # --------------------------------------------------------------------------
    # 8.3 Collaboration and Module Integration
    # --------------------------------------------------------------------------
    insert_heading("8.3 Collaboration and Module Integration", level=2)
    insert_p(
        "Rather than operating as three disparate utilities, the contributions of all three team members unite into a synchronized, "
        "interconnected operational pipeline. Figure 8.1 and the subsequent description illustrate how data and execution flow across the application:"
    )

    pipeline_steps = [
        ("1. Interface Presentation (Shivansh): ",
         "The user launches the application. Shivansh's high-DPI bootstrap configures crisp rendering, and `TypeRushApp` displays the Home Dashboard. "
         "The user selects a difficulty level (Easy–Expert) and test duration (15s–120s) through Shivansh's custom dropdown and card components."),
        ("2. Interactive Typing Loop & Telemetry (Abhiram): ",
         "When the user initiates the test, `TypingScreen` fetches a curated text passage from Abhiram's `ContentDeckGenerator`. "
         "As the typist enters characters, Abhiram's `TypingAlignmentEngine` evaluates keystrokes in real time, applies green/red text highlights, "
         "synchronizes the native insertion caret, and computes Gross/Net WPM telemetry. Pressing spacebar commits each word without cascading errors."),
        ("3. Session Persistence & Analytics Processing (Biswa): ",
         "Upon test completion or countdown expiration, Abhiram's typing loop packages the session metrics into a structured data payload. "
         "Biswa's `StorageManager` atomically commits the record to `data/history.json`, updates user all-time personal bests, and triggers completion audio."),
        ("4. Results Presentation & Longitudinal Archiving (Integrated System): ",
         "`TypeRushApp` routes to `ResultsScreen`, where Biswa's 8-metric telemetry card, velocity progression spline graph, and Levenshtein mistake table "
         "are rendered inside Shivansh's Midnight Minimal card containers. The typist can subsequently explore historical trends or export data to CSV.")
    ]
    for bold_txt, norm_txt in pipeline_steps:
        insert_p(norm_txt, bold_prefix=bold_txt, space_after=3)

    # Embed Architecture Diagram
    workflow_img_path = os.path.join(os.path.dirname(__file__), "contribution_workflow.png")
    if os.path.exists(workflow_img_path):
        p_img = target_conclusion_p.insert_paragraph_before()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(workflow_img_path, width=Inches(6.2))

        p_cap = target_conclusion_p.insert_paragraph_before()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        run_cap = p_cap.add_run("Figure 8.1: Multi-tier architectural integration and module collaboration flow in TypeRush 2.1.")
        run_cap.font.name = "Segoe UI"
        run_cap.font.size = Pt(8.5)
        run_cap.font.italic = True
        run_cap.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Division of Responsibilities Matrix Table
    insert_heading("8.4 Division of Responsibilities Matrix", level=2)
    insert_p(
        "Table 8.2 provides an exhaustive subsystem comparison showing primary lead ownership, secondary collaboration, and the scope of integration."
    )

    t_matrix = insert_table(num_rows=21, num_cols=4)
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
    for r_idx, row in enumerate(t_matrix.rows):
        for c_idx, val in enumerate(matrix_data[r_idx]):
            row.cells[c_idx].paragraphs[0].text = val
    format_table(t_matrix, [1.8, 1.4, 1.3, 2.0])
    insert_p(space_after=8)

    # Save documents
    doc.save(out_final_root)
    doc.save(out_final_report)
    print("=" * 80)
    print(f"SUCCESSFULLY GENERATED FINAL PROJECT REPORT:")
    print(f"  1. {out_final_root}")
    print(f"  2. {out_final_report}")
    print("=" * 80)

if __name__ == "__main__":
    integrate_contributions()
