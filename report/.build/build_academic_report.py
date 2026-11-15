import os
import subprocess
import base64
import pymupdf

def build_pdf_report():
    print("=" * 80)
    print("BUILDING REFINED ACADEMIC REPORT FOR SRMIST: TYPERUSH (RA2511026010332.pdf)")
    print("=" * 80)

    report_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Load SRM logo base64
    logo_path = os.path.join(report_dir, "srm_logo_300dpi.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode("utf-8")
        logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" class="srm-logo" alt="SRMIST Logo" />'
    else:
        logo_img_tag = ''

    # 2. Construct Academic Report HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>TypeRush — Academic Project Report</title>
<style>
    @page {{
        size: A4 portrait;
        margin: 0;
    }}
    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }}
    html, body {{
        width: 210mm;
        background: #FFFFFF;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', Arial, sans-serif;
        color: #1E293B;
        font-size: 9.2pt;
        line-height: 1.44;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }}
    @media print {{
        .page {{
            page-break-after: always;
            break-after: page;
        }}
        .page:last-child {{
            page-break-after: avoid;
            break-after: avoid;
        }}
    }}
    .page {{
        width: 210mm;
        height: 297mm;
        max-height: 297mm;
        padding: 13mm 16mm 12mm 16mm;
        position: relative;
        background: #FFFFFF;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}

    /* Institutional Header */
    .header-table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 2.5mm;
    }}
    .header-left {{
        vertical-align: middle;
        text-align: left;
    }}
    .header-right {{
        vertical-align: middle;
        text-align: right;
        width: 58mm;
    }}
    .inst-name {{
        font-size: 13pt;
        font-weight: 800;
        color: #002B49;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        margin-bottom: 1.5px;
    }}
    .subject-title {{
        font-size: 10pt;
        font-weight: 700;
        color: #034DA1;
        margin-bottom: 1px;
    }}
    .sub-code {{
        font-size: 8.8pt;
        font-weight: 600;
        color: #475569;
    }}
    .srm-logo {{
        max-width: 52mm;
        max-height: 18mm;
        object-fit: contain;
    }}

    .divider-gold {{
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, #002B49 0%, #034DA1 60%, #C7A008 100%);
        margin-bottom: 3.5mm;
    }}

    /* Title Block */
    .title-block {{
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #002B49;
        padding: 3mm 4mm;
        border-radius: 3px;
        margin-bottom: 3.5mm;
    }}
    .project-title {{
        font-size: 17pt;
        font-weight: 900;
        color: #002B49;
        letter-spacing: 0.8px;
        line-height: 1.1;
    }}
    .project-subtitle {{
        font-size: 9pt;
        font-weight: 500;
        color: #334155;
        font-style: italic;
        margin-top: 1.5px;
    }}

    /* Metadata Grid (Members & Faculty) */
    .meta-table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 3.5mm;
    }}
    .meta-members {{
        width: 62%;
        vertical-align: top;
        padding-right: 3mm;
    }}
    .meta-faculty {{
        width: 38%;
        vertical-align: top;
    }}
    .meta-card {{
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 4px;
        padding: 2.5mm 3.5mm;
        height: 100%;
    }}
    .meta-card-title {{
        font-size: 7.5pt;
        font-weight: 700;
        color: #002B49;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 2mm;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 1mm;
    }}
    .member-list {{
        list-style: none;
    }}
    .member-item {{
        display: flex;
        justify-content: space-between;
        font-size: 8.8pt;
        padding: 0.8px 0;
    }}
    .member-name {{
        font-weight: 700;
        color: #0F172A;
    }}
    .member-reg {{
        font-family: 'Consolas', 'Courier New', monospace;
        font-weight: 600;
        color: #034DA1;
        letter-spacing: 0.3px;
    }}
    .faculty-name {{
        font-size: 9.5pt;
        font-weight: 700;
        color: #0F172A;
        margin-top: 1.5mm;
    }}
    .faculty-label {{
        font-size: 8.2pt;
        color: #475569;
        font-style: italic;
    }}

    /* Section Styles */
    .section {{
        margin-bottom: 3.2mm;
    }}
    .section-header {{
        font-size: 9.2pt;
        font-weight: 800;
        color: #002B49;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        border-bottom: 1.2px solid #CBD5E1;
        padding-bottom: 1mm;
        margin-bottom: 1.8mm;
        display: flex;
        align-items: center;
    }}
    .section-header span {{
        color: #C7A008;
        margin-right: 4px;
    }}
    p {{
        text-align: justify;
        text-justify: inter-word;
        color: #1E293B;
    }}

    /* Objectives List */
    .obj-list {{
        list-style: none;
        padding-left: 0;
    }}
    .obj-item {{
        position: relative;
        padding-left: 4.5mm;
        margin-bottom: 1.4mm;
        font-size: 8.8pt;
        text-align: justify;
    }}
    .obj-item::before {{
        content: "▪";
        position: absolute;
        left: 0.5mm;
        top: -0.5px;
        color: #034DA1;
        font-size: 10pt;
    }}
    .obj-title {{
        font-weight: 700;
        color: #002B49;
    }}

    /* Page 2 Elements */
    .running-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1.5px solid #002B49;
        padding-bottom: 1.5mm;
        margin-bottom: 3.2mm;
    }}
    .running-title {{
        font-size: 8.2pt;
        font-weight: 700;
        color: #002B49;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }}
    .running-meta {{
        font-size: 8pt;
        color: #64748B;
        font-weight: 600;
    }}

    /* Architecture Diagram */
    .arch-container {{
        background: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-radius: 4px;
        padding: 2.5mm 2.5mm 1.5mm 2.5mm;
        margin-bottom: 3mm;
        text-align: center;
    }}
    .arch-svg {{
        width: 100%;
        height: auto;
        display: block;
        max-height: 64mm;
    }}

    /* Tech Table */
    .tech-table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 3mm;
        font-size: 8.4pt;
    }}
    .tech-table th {{
        background: #002B49;
        color: #FFFFFF;
        font-weight: 700;
        text-align: left;
        padding: 1.6mm 3mm;
        letter-spacing: 0.4px;
        font-size: 8pt;
        text-transform: uppercase;
    }}
    .tech-table td {{
        padding: 1.5mm 3mm;
        border-bottom: 1px solid #E2E8F0;
        color: #1E293B;
    }}
    .tech-table tr:nth-child(even) td {{
        background: #F8FAFC;
    }}
    .tech-name {{
        font-weight: 700;
        color: #034DA1;
        width: 25%;
    }}

    /* Features Grid */
    .features-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.8mm 3mm;
        margin-bottom: 3mm;
    }}
    .feature-card {{
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 2.5px solid #034DA1;
        padding: 1.6mm 2.5mm;
        border-radius: 3px;
        font-size: 8.2pt;
    }}
    .feature-title {{
        font-weight: 700;
        color: #002B49;
        margin-bottom: 0.5px;
    }}
    .feature-desc {{
        color: #475569;
        line-height: 1.32;
    }}

    /* GitHub Section */
    .github-card {{
        background: #F1F5F9;
        border: 1px solid #CBD5E1;
        border-radius: 4px;
        padding: 2.2mm 3.5mm;
        margin-bottom: 1.5mm;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    .github-left {{
        flex: 1;
    }}
    .github-label {{
        font-size: 7.3pt;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 1px;
    }}
    .github-url {{
        font-size: 9.2pt;
        font-weight: 700;
        color: #034DA1;
        text-decoration: none;
        font-family: 'Consolas', monospace;
    }}
    .github-url:hover {{
        text-decoration: underline;
    }}
    .github-badge {{
        background: #002B49;
        color: #FFFFFF;
        font-size: 7pt;
        font-weight: 700;
        padding: 1.2mm 2.8mm;
        border-radius: 3px;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }}

    /* Footer */
    .page-footer {{
        border-top: 1px solid #E2E8F0;
        padding-top: 1.5mm;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 7.5pt;
        color: #64748B;
        margin-top: 1mm;
    }}
    .footer-left {{
        font-weight: 600;
    }}
    .footer-right {{
        font-weight: 700;
        color: #002B49;
    }}
</style>
</head>
<body>

<!-- ======================================================================= -->
<!-- PAGE 1: INSTITUTION, TEAM, ABSTRACT, PROJECT CONTEXT & OBJECTIVES       -->
<!-- ======================================================================= -->
<div class="page">
    <div>
        <!-- A. Institution Header -->
        <table class="header-table">
            <tr>
                <td class="header-left">
                    <div class="inst-name">SRM Institute of Science and Technology</div>
                    <div class="subject-title">Advanced Programming Practice (A.P.P.)</div>
                    <div class="sub-code">Subject Sub Code: 21CSC203P</div>
                </td>
                <td class="header-right">
                    {logo_img_tag}
                </td>
            </tr>
        </table>

        <div class="divider-gold"></div>

        <!-- B. Project Title -->
        <div class="title-block">
            <div class="project-title">TYPERUSH</div>
            <div class="project-subtitle">A Python-Based Desktop Typing Practice and Performance Analysis Application</div>
        </div>

        <!-- C & D. Group Members & Faculty -->
        <table class="meta-table">
            <tr>
                <td class="meta-members">
                    <div class="meta-card">
                        <div class="meta-card-title">Project Team Members</div>
                        <ul class="member-list">
                            <li class="member-item">
                                <span class="member-name">1. Shivansh Bansal</span>
                                <span class="member-reg">RA2511026010332</span>
                            </li>
                            <li class="member-item">
                                <span class="member-name">2. Biswa Prakash Rout</span>
                                <span class="member-reg">RA2511026010339</span>
                            </li>
                            <li class="member-item">
                                <span class="member-name">3. Boddupalli Phani Venkata Sri Abhiram</span>
                                <span class="member-reg">RA2511026010355</span>
                            </li>
                        </ul>
                    </div>
                </td>
                <td class="meta-faculty">
                    <div class="meta-card">
                        <div class="meta-card-title">Faculty In-Charge</div>
                        <div class="faculty-label">Department:</div>
                        <div class="faculty-name">Computational Intelligence</div>
                    </div>
                </td>
            </tr>
        </table>

        <!-- E. Abstract -->
        <div class="section">
            <div class="section-header"><span>■</span> Abstract</div>
            <p>
                TypeRush is an academic desktop typing benchmark and skill-development application engineered using Python and its native Tkinter graphical toolkit. Designed to resolve keyboard inefficiency and erratic typing rhythm, the system provides structured typing practice accompanied by adaptive word alignment that eliminates cascading error penalties. The software features four curated difficulty tiers and four configurable test durations, delivering real-time character-level feedback through tri-state visual indicators: vivid green for correct characters, high-contrast red for inaccuracies, and muted grey for remaining untyped text. Dynamic telemetry continuously computes Words Per Minute (WPM), character accuracy, and mistake distributions. By coupling local data persistence with comprehensive post-test analytics, TypeRush provides a distraction-free, reliable environment to systematically measure, evaluate, and enhance keyboard fluency.
            </p>
        </div>

        <!-- F. Project Description -->
        <div class="section">
            <div class="section-header"><span>■</span> Project Description & Context</div>
            <p>
                In modern computer science and software engineering, typing proficiency directly governs productivity and intellectual momentum. Sluggish input or recurrent typographical errors introduce substantial cognitive friction, breaking problem-solving concentration. TypeRush addresses these limitations by delivering a responsive, self-contained desktop platform developed purely in Python and Tkinter, requiring no external web frameworks, remote servers, or third-party dependencies.
            </p>
            <p style="margin-top: 1.5mm;">
                Users engage through an intuitive dashboard to configure challenges across four difficulty levels (Easy, Medium, Hard, and Expert) and four session intervals (15s, 30s, 60s, and 120s). During live practice, an integrated Levenshtein string-alignment engine evaluates keystrokes in real time. Crucially, errors are strictly isolated to individual words, preventing single omitted or inserted characters from causing catastrophic downstream misalignments. Upon session completion, the application renders a rigorous telemetry report detailing speed, accuracy, and mistake categories, while preserving all historical records in atomic JSON storage for longitudinal progress evaluation.
            </p>
        </div>

        <!-- G. Objectives -->
        <div class="section">
            <div class="section-header"><span>■</span> Project Objectives</div>
            <ul class="obj-list">
                <li class="obj-item">
                    <span class="obj-title">Native Desktop Architecture:</span> Construct a clean, highly responsive desktop typing application using Python and standard Tkinter without external pip packages.
                </li>
                <li class="obj-item">
                    <span class="obj-title">Real-Time Visual Feedback:</span> Provide immediate character-level color coding paired with Levenshtein-based word alignment to prevent error cascading.
                </li>
                <li class="obj-item">
                    <span class="obj-title">Precision Performance Metrics:</span> Continuously compute and record standardized Gross/Net WPM, accuracy percentages, error counts, and consistency ratings.
                </li>
                <li class="obj-item">
                    <span class="obj-title">Configurable Practice Tiers:</span> Provide structured practice streams across four difficulty levels and four selectable test durations (15s to 120s).
                </li>
                <li class="obj-item">
                    <span class="obj-title">Local Persistence & Diagnostics:</span> Maintain private historical session timelines, multi-criteria filtering, and customizable settings via atomic JSON storage.
                </li>
            </ul>
        </div>
    </div>

    <!-- Page 1 Footer -->
    <div class="page-footer">
        <div class="footer-left">SRM Institute of Science and Technology • Advanced Programming Practice (21CSC203P)</div>
        <div class="footer-right">Page 1 of 2</div>
    </div>
</div>

<!-- ======================================================================= -->
<!-- PAGE 2: SYSTEM ARCHITECTURE, TECHNOLOGIES, FEATURES & CONCLUSION         -->
<!-- ======================================================================= -->
<div class="page">
    <div>
        <!-- Running Header -->
        <div class="running-header">
            <div class="running-title">TypeRush — System Architecture & Implementation Report</div>
            <div class="running-meta">SRMIST • 21CSC203P • Computational Intelligence</div>
        </div>

        <!-- A. System Architecture / Block Diagram -->
        <div class="section">
            <div class="section-header"><span>■</span> System Architecture & Logical Workflow</div>
            <div class="arch-container">
                <svg class="arch-svg" viewBox="0 0 760 224" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="gradTop" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#002B49"/>
                            <stop offset="100%" stop-color="#034DA1"/>
                        </linearGradient>
                        <linearGradient id="gradMid" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#F8FAFC"/>
                            <stop offset="100%" stop-color="#EDF2F7"/>
                        </linearGradient>
                        <linearGradient id="gradBottom" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#0F172A"/>
                            <stop offset="100%" stop-color="#1E293B"/>
                        </linearGradient>
                        <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                            <path d="M 0 1 L 8 5 L 0 9 z" fill="#034DA1"/>
                        </marker>
                    </defs>

                    <!-- Row 1: USER -->
                    <rect x="290" y="3" width="180" height="23" rx="4" fill="url(#gradTop)"/>
                    <text x="380" y="19" fill="#FFFFFF" font-size="10.5" font-weight="700" text-anchor="middle" font-family="'Segoe UI', sans-serif">USER (Keystroke Input)</text>
                    
                    <line x1="380" y1="26" x2="380" y2="38" stroke="#034DA1" stroke-width="1.8" marker-end="url(#arrow)"/>

                    <!-- Row 2: TKINTER UI -->
                    <rect x="235" y="38" width="290" height="24" rx="4" fill="#FFFFFF" stroke="#002B49" stroke-width="1.4"/>
                    <text x="380" y="54" fill="#002B49" font-size="10.2" font-weight="700" text-anchor="middle" font-family="'Segoe UI', sans-serif">TKINTER USER INTERFACE (Desktop Screens)</text>

                    <line x1="380" y1="62" x2="380" y2="73" stroke="#034DA1" stroke-width="1.8" marker-end="url(#arrow)"/>

                    <!-- Row 3: CONTROLLER -->
                    <rect x="220" y="73" width="320" height="24" rx="4" fill="#FFFFFF" stroke="#034DA1" stroke-width="1.4"/>
                    <text x="380" y="89" fill="#034DA1" font-size="10" font-weight="700" text-anchor="middle" font-family="'Segoe UI', sans-serif">APPLICATION CONTROLLER (Screen Router & State)</text>

                    <!-- Branching Arrows to Core Components -->
                    <line x1="380" y1="97" x2="380" y2="105" stroke="#034DA1" stroke-width="1.8"/>
                    <line x1="125" y1="105" x2="635" y2="105" stroke="#034DA1" stroke-width="1.8"/>
                    <line x1="125" y1="105" x2="125" y2="114" stroke="#034DA1" stroke-width="1.8" marker-end="url(#arrow)"/>
                    <line x1="380" y1="105" x2="380" y2="114" stroke="#034DA1" stroke-width="1.8" marker-end="url(#arrow)"/>
                    <line x1="635" y1="105" x2="635" y2="114" stroke="#034DA1" stroke-width="1.8" marker-end="url(#arrow)"/>

                    <!-- Box 1: Typing Engine -->
                    <rect x="15" y="114" width="220" height="62" rx="4" fill="url(#gradMid)" stroke="#CBD5E1" stroke-width="1.2"/>
                    <text x="125" y="128" fill="#002B49" font-size="9.5" font-weight="700" text-anchor="middle" font-family="'Segoe UI', sans-serif">1. TYPING ENGINE</text>
                    <text x="125" y="140" fill="#334155" font-size="7.8" text-anchor="middle" font-family="'Segoe UI', sans-serif">• Displays Passages & Stream Buffer</text>
                    <text x="125" y="151" fill="#334155" font-size="7.8" text-anchor="middle" font-family="'Segoe UI', sans-serif">• Handles Keyboard Input & Caret</text>
                    <text x="125" y="162" fill="#334155" font-size="7.8" text-anchor="middle" font-family="'Segoe UI', sans-serif">• Tracks Correct & Incorrect Characters</text>
                    <text x="125" y="172" fill="#334155" font-size="7.8" text-anchor="middle" font-family="'Segoe UI', sans-serif">• Manages Typing Progress & Time Limits</text>

                    <!-- Box 2: Scoring Engine -->
                    <rect x="270" y="114" width="220" height="62" rx="4" fill="url(#gradMid)" stroke="#CBD5E1" stroke-width="1.2"/>
                    <text x="380" y="128" fill="#002B49" font-size="9.5" font-weight="700" text-anchor="middle" font-family="'Segoe UI', sans-serif">2. SCORING ENGINE</text>
                    <text x="380" y="140" fill="#334155" font-size="7.8" text-anchor="middle" font-family="'Segoe UI', sans-serif">• Calculates Gross & Net WPM</text>
                    <text x="380" y="151" fill="#334155" font-size="7.8" text-anchor="middle" font-family="'Segoe UI', sans-serif">• Calculates Accuracy Percentage</text>
                    <text x="380" y="162" fill="#334155" font-size="7.8" text-anchor="middle" font-family="'Segoe UI', sans-serif">• Tracks Errors & Mistake Review</text>
                    <text x="380" y="172" fill="#334155" font-size="7.8" text-anchor="middle" font-family="'Segoe UI', sans-serif">• Generates Performance Results</text>

                    <!-- Box 3: Storage Manager -->
                    <rect x="525" y="114" width="220" height="62" rx="4" fill="url(#gradMid)" stroke="#CBD5E1" stroke-width="1.2"/>
                    <text x="635" y="128" fill="#002B49" font-size="9.5" font-weight="700" text-anchor="middle" font-family="'Segoe UI', sans-serif">3. STORAGE MANAGER</text>
                    <text x="635" y="140" fill="#334155" font-size="7.8" text-anchor="middle" font-family="'Segoe UI', sans-serif">• Saves Typing History Locally</text>
                    <text x="635" y="151" fill="#334155" font-size="7.8" text-anchor="middle" font-family="'Segoe UI', sans-serif">• Stores Application Settings (JSON)</text>
                    <text x="635" y="162" fill="#334155" font-size="7.8" text-anchor="middle" font-family="'Segoe UI', sans-serif">• Retrieves Previous Performance Data</text>
                    <text x="635" y="172" fill="#334155" font-size="7.8" text-anchor="middle" font-family="'Segoe UI', sans-serif">• Exports Historical Records to CSV</text>

                    <!-- Converging Arrows to Bottom -->
                    <line x1="125" y1="176" x2="125" y2="184" stroke="#034DA1" stroke-width="1.8"/>
                    <line x1="380" y1="176" x2="380" y2="184" stroke="#034DA1" stroke-width="1.8"/>
                    <line x1="635" y1="176" x2="635" y2="184" stroke="#034DA1" stroke-width="1.8"/>
                    <line x1="125" y1="184" x2="635" y2="184" stroke="#034DA1" stroke-width="1.8"/>
                    <line x1="380" y1="184" x2="380" y2="192" stroke="#034DA1" stroke-width="1.8" marker-end="url(#arrow)"/>

                    <!-- Bottom Box: Output -->
                    <rect x="180" y="192" width="400" height="25" rx="4" fill="url(#gradBottom)"/>
                    <text x="380" y="208" fill="#FFFFFF" font-size="10" font-weight="700" text-anchor="middle" font-family="'Segoe UI', sans-serif">RESULTS, HISTORY AND USER SETTINGS</text>
                </svg>
            </div>
        </div>

        <!-- B. Technologies Used -->
        <div class="section">
            <div class="section-header"><span>■</span> Technologies Used</div>
            <table class="tech-table">
                <thead>
                    <tr>
                        <th>Technology</th>
                        <th>Academic Purpose & Implementation Role</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="tech-name">Python</td>
                        <td>Core application programming language and execution environment</td>
                    </tr>
                    <tr>
                        <td class="tech-name">Tkinter</td>
                        <td>Native desktop graphical user interface, event handling, and canvas rendering</td>
                    </tr>
                    <tr>
                        <td class="tech-name">JSON</td>
                        <td>Local storage of application data, session history, and user preferences</td>
                    </tr>
                    <tr>
                        <td class="tech-name">Python Standard Library</td>
                        <td>Supporting application functionality (math, timing, file I/O, audio, unittest)</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- C. Main Implemented Features -->
        <div class="section">
            <div class="section-header"><span>■</span> Key Implemented Features</div>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-title">Four Difficulty Levels</div>
                    <div class="feature-desc">Curated text stream generator featuring Easy, Medium, Hard, and Expert natural English vocabulary tiers.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">Four Test Durations</div>
                    <div class="feature-desc">Accurate interval timers supporting 15s speed sprints, 30s intervals, 60s standard tests, and 120s endurance practice.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">Real-Time Typing Feedback</div>
                    <div class="feature-desc">Immediate character coloring (green correct, red incorrect, grey untyped) with adaptive Levenshtein word bounds.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">WPM & Accuracy Calculation</div>
                    <div class="feature-desc">Precision Gross WPM, Net WPM, character accuracy percentages, error counters, and rhythm consistency telemetry.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">Results & Performance Analytics</div>
                    <div class="feature-desc">Post-session diagnostic review categorizing typographical discrepancies into substitutions, omissions, and insertions.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">Local History & Statistics</div>
                    <div class="feature-desc">Searchable chronological session timeline with multi-criteria filtering, progression trend graphing, and CSV export.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">Customizable Application Settings</div>
                    <div class="feature-desc">Unified Midnight Minimal dark glass theme, audio feedback toggles, text sizes, and atomic preference storage.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">Zero Third-Party Dependencies</div>
                    <div class="feature-desc">Pure standard library architecture verified on Windows 11 with Python 3.14.7 for immediate academic reproducibility.</div>
                </div>
            </div>
        </div>

        <!-- D. Conclusion -->
        <div class="section">
            <div class="section-header"><span>■</span> Conclusion</div>
            <p>
                TypeRush was successfully designed and developed as a complete native desktop typing practice and performance analysis application for the Advanced Programming Practice curriculum. By leveraging Python's rapid development capabilities and Tkinter's native event-driven GUI toolkit, the project delivers a distraction-free, highly responsive typing experience without relying on external web frameworks or third-party packages. The implementation of real-time character-level feedback, Levenshtein alignment, and atomic JSON persistence equips users with the exact tools needed to systematically analyze and improve their keyboard speed, accuracy, and typing rhythm.
            </p>
        </div>

        <!-- E. GitHub Repository -->
        <div class="github-card">
            <div class="github-left">
                <div class="github-label">Project Source Code & Repository (Verified & Publicly Accessible)</div>
                <a class="github-url" href="https://github.com/TypeRush/TypeRush" target="_blank">https://github.com/TypeRush/TypeRush</a>
            </div>
            <div class="github-badge">PUBLIC REPOSITORY</div>
        </div>
    </div>

    <!-- Page 2 Footer -->
    <div class="page-footer">
        <div class="footer-left">SRM Institute of Science and Technology • Advanced Programming Practice (21CSC203P)</div>
        <div class="footer-right">Page 2 of 2</div>
    </div>
</div>

</body>
</html>
"""

    html_file = os.path.join(report_dir, "academic_report_temp.html")
    parent_report_dir = os.path.dirname(report_dir)
    pdf_file = os.path.join(parent_report_dir, "RA2511026010332.pdf")

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Compile via Chrome or Edge
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    browser_exe = next((p for p in chrome_paths if os.path.exists(p)), None)
    if not browser_exe:
        raise RuntimeError("No headless browser found for PDF compilation!")
    cmd = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_file}",
        f"file:///{html_file}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not os.path.exists(pdf_file):
        raise RuntimeError(f"Edge PDF generation failed with code {res.returncode}: {res.stderr}")

    # Verify with PyMuPDF
    doc = pymupdf.open(pdf_file)
    page_count = len(doc)
    print(f"Verified PDF page count: {page_count}")
    assert page_count == 2, f"STRICT REQUIREMENT VIOLATED: PDF has {page_count} pages instead of exactly 2!"

    # Render high-resolution previews
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=200)
        preview_filename = os.path.join(report_dir, f"report_page_{i + 1}.png")
        pix.save(preview_filename)
        print(f"Rendered Page {i + 1} preview: {preview_filename} ({pix.width}x{pix.height})")

    # Clean up temporary HTML
    try:
        os.remove(html_file)
    except Exception:
        pass

    print("=" * 80)
    print(f"ACADEMIC REPORT CREATION SUCCESSFUL: {pdf_file}")
    print("=" * 80)
    return pdf_file

if __name__ == "__main__":
    build_pdf_report()
