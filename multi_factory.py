
import json
import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---------------------------------------------------------
# CONSTANTS & CONFIG
# ---------------------------------------------------------
DATA_FILE = "data.json"
OUTPUT_DIR = "Output"

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def add_toc_field(paragraph):
    """
    Inserts a Word Table of Contents (TOC) field into a paragraph.
    Note: The user must right-click > Update Field in Word to populate it.
    """
    run = paragraph.add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar)

    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    # TOC with levels 1-3, hyperlinks, outline levels
    instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
    run._r.append(instrText)

    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'separate')
    run._r.append(fldChar)

    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar)

def configure_styles(doc, font_data, line_spacing):
    """
    Configures the base styles (Normal, Headings) to match requirements.
    This avoids manual formatting on paragraphs.
    """
    styles = doc.styles
    font_name = font_data.get("name", "Times New Roman")
    font_size = font_data.get("size", 12)

    # 1. Normal Style
    style_normal = styles['Normal']
    font = style_normal.font
    font.name = font_name
    font.size = Pt(font_size)
    
    # Paragraph format
    pf = style_normal.paragraph_format
    if line_spacing == 1.5:
        # 1.5 lines is approx 240/240 * 1.5 in Word logic or use specialized setting
        # python-docx allows direct float for line_spacing based on lines
        pf.line_spacing = 1.5
    elif line_spacing == 2.0:
        pf.line_spacing = 2.0
    else:
        pf.line_spacing = 1.0 # Default fallback

    # 2. Heading 1 (Chapter Level)
    style_h1 = styles['Heading 1']
    h1_font = style_h1.font
    h1_font.name = font_name
    h1_font.size = Pt(16)
    h1_font.bold = True
    h1_font.color.rgb = RGBColor(0, 0, 0) # Force Black
    style_h1.paragraph_format.space_before = Pt(24)
    style_h1.paragraph_format.space_after = Pt(12)

    # 3. Heading 2 (Section Level)
    style_h2 = styles['Heading 2']
    h2_font = style_h2.font
    h2_font.name = font_name
    h2_font.size = Pt(14)
    h2_font.bold = True
    h2_font.color.rgb = RGBColor(0, 0, 0)
    style_h2.paragraph_format.space_before = Pt(18)
    style_h2.paragraph_format.space_after = Pt(6)

    # 4. Heading 3 (Subsection Level)
    style_h3 = styles['Heading 3']
    h3_font = style_h3.font
    h3_font.name = font_name
    h3_font.size = Pt(12)
    h3_font.bold = True
    h3_font.color.rgb = RGBColor(0, 0, 0)
    style_h3.paragraph_format.space_before = Pt(12)
    style_h3.paragraph_format.space_after = Pt(6)
    
    # 5. Caption Style
    if 'Caption' in styles:
        style_caption = styles['Caption']
        c_font = style_caption.font
        c_font.name = font_name
        c_font.size = Pt(10)
        c_font.italic = True
        c_font.color.rgb = RGBColor(0, 0, 0)


def setup_margins(doc, margins):
    """Applies margin settings to the first section."""
    section = doc.sections[0]
    section.left_margin = Inches(margins.get("left", 1.0))
    section.right_margin = Inches(margins.get("right", 1.0))
    section.top_margin = Inches(margins.get("top", 1.0))
    section.bottom_margin = Inches(margins.get("bottom", 1.0))
    
    # Mirror margins logic if needed (requires OXML, simplifying to standard setup here as python-docx basic support is for single section props)
    # mirroring can be set via mirror_margins property if supported, else default to standard binding gutter logic

def add_simple_page_numbers(doc):
    """Adds a basic page number in the footer."""
    # This is complex in pure python-docx without OXML. 
    # We will trigger the Footer editing but might leave exact numbering to Word's auto features 
    # if OXML is too risky. However, let's try a safe OXML insertion for "Page <Nb>".
    section = doc.sections[0]
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar1)
    
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = "PAGE"
    run._r.append(instrText)
    
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    run._r.append(fldChar2)
    
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar3)

# ---------------------------------------------------------
# MAIN GENERATOR
# ---------------------------------------------------------

def process_university(uni_data):
    uni_id = uni_data.get("id", "UNKNOWN")
    uni_name = uni_data.get("uni_name", "University")
    course = uni_data.get("course_name", "Thesis")
    
    # Path setup
    target_dir = os.path.join(OUTPUT_DIR, uni_id)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    doc_path = os.path.join(target_dir, "Template.docx")
    readme_path = os.path.join(target_dir, "README.md")
    
    # 1. Initialize Document
    doc = Document()
    
    # 2. Setup Page Layout (Margins)
    setup_margins(doc, uni_data.get("margins", {}))
    
    # 3. Setup Styles (Fonts)
    configure_styles(doc, uni_data.get("font", {}), uni_data.get("line_spacing", 1.5))
    
    # 4. Preliminary Pages
    prelims = uni_data.get("preliminary_order", [])
    
    # Title Page (Manual formatting permissible here for Title look, but trying to use styles)
    # But usually Title page has no style. We will use Normal centered.
    doc.add_heading(uni_name, 0)
    p = doc.add_paragraph(f"{course} Thesis Template")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("\n\n\n[STUDENT NAME]\n[ID NUMBER]\n\n\n[MONTH, YEAR]", style='Normal').alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()
    
    for page_title in prelims:
        if page_title == "Title Page": 
            continue # Already done
        
        # If it's TOC, handle specially
        if page_title == "Table of Contents":
            doc.add_heading("Table of Contents", level=1)
            p = doc.add_paragraph()
            add_toc_field(p)
            doc.add_page_break()
            continue

        doc.add_heading(page_title, level=1)
        doc.add_paragraph(f"[{page_title} Content Goes Here]", style='Normal')
        doc.add_page_break()
        
    # 5. Core Chapters (Dummy Content)
    chapters = ["Introduction", "Literature Review", "Methodology", "Results & Discussion", "Conclusion"]
    
    for i, chapter in enumerate(chapters, 1):
        doc.add_heading(f"Chapter {i}: {chapter}", level=1)
        doc.add_paragraph(f"This is the start of the {chapter}. The formatting below demonstrates subhearings.", style='Normal')
        
        doc.add_heading("Section 1.1: Context", level=2)
        doc.add_paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", style='Normal')
        
        doc.add_heading("Subsection 1.1.1: Detail", level=3)
        doc.add_paragraph("Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", style='Normal')
        
        # Add a placeholder figure/table
        if i == 3:
            doc.add_paragraph("[Figure 1: Conceptual Framework]", style='Caption')
            
        doc.add_page_break()

    # 6. References
    doc.add_heading("References", level=1)
    doc.add_paragraph(f"[{uni_data.get('reference_style', 'APA')} Style References List]", style='Normal')
    
    # 7. Add Page Numbers
    add_simple_page_numbers(doc)
    
    # Save
    doc.save(doc_path)
    
    # 8. Generate README
    generate_readme(readme_path, uni_data)
    
    print(f"✅ Generated {uni_name} - {course}")

def generate_readme(path, data):
    content = f"""# {data['uni_name']} - {data['course_name']} Thesis Template

**Year:** {data['year']}
**Reference Style:** {data.get('reference_style', 'Standard')}

## ⚠️ Disclaimer
This template is generated programmatically based on publicly available guidelines. 
ALWAYS verify with your specific department before final submission.

## Compliance Details
- **Font:** {data['font']['name']} ({data['font']['size']}pt)
- **Margins:** Top {data['margins']['top']}", Bottom {data['margins']['bottom']}", Left {data['margins']['left']}", Right {data['margins']['right']}"
- **Spacing:** {data['line_spacing']} lines

## How to Use
1. Open `Template.docx`
2. Update the **Title Page** with your details.
3. Use the **Styles Pane** in Word:
   - Use `Heading 1` for Chapters
   - Use `Heading 2` for Sections
   - Use `Normal` for body text
4. **Table of Contents**: Right-click the TOC and select "Update Field" to refresh page numbers.

## Preliminary Pages included:
{', '.join(['- ' + p for p in data['preliminary_order']])}

---
*Generated by ThesisFactory Automation*
"""
    with open(path, 'w') as f:
        f.write(content)


# ---------------------------------------------------------
# WEB GENERATOR (SEO & SEARCH)
# ---------------------------------------------------------

def generate_web_page(target_dir, uni_data):
    """Generates an SEO-optimized HTML landing page for the university."""
    html_path = os.path.join(target_dir, "index.html")
    
    uni_name = uni_data.get('uni_name', 'University')
    course = uni_data.get('course_name', 'Thesis')
    doc_link = "Template.docx"
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{uni_name} {course} Thesis Template (2026) - Free Download</title>
    <meta name="description" content="Download the official 2026 compliant {course} thesis template for {uni_name}. Correct margins, fonts, and formatting styles pre-set. Free Word (docx) format.">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        .download-btn {{ display: inline-block; background-color: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }}
        .download-btn:hover {{ background-color: #0056b3; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f8f9fa; }}
        .breadcrumb {{ font-size: 0.9em; color: #666; margin-bottom: 20px; }}
        .breadcrumb a {{ color: #007bff; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="breadcrumb">
        <a href="../index.html">Home</a> &gt; {uni_name}
    </div>

    <h1>{uni_name} Thesis Template</h1>
    <p><strong>Course:</strong> {course}<br><strong>Year:</strong> {uni_data.get('year', '2026')}</p>

    <p>This is a free, automated thesis template generator compliant with the {uni_data.get('year')} {uni_name} guidelines. It uses native Word Styles for automated Table of Contents and proper formatting.</p>

    <a href="{doc_link}" class="download-btn">⬇️ Download Template (.docx)</a>

    <h2>Compliance Specifications</h2>
    <table>
        <tr><th>Parameter</th><th>Value</th></tr>
        <tr><td>Margins</td><td>Top: {uni_data['margins']['top']}", Bottom: {uni_data['margins']['bottom']}", Left: {uni_data['margins']['left']}", Right: {uni_data['margins']['right']}"</td></tr>
        <tr><td>Font</td><td>{uni_data['font']['name']} ({uni_data['font']['size']}pt)</td></tr>
        <tr><td>Line Spacing</td><td>{uni_data['line_spacing']}</td></tr>
        <tr><td>Reference Style</td><td>{uni_data.get('reference_style', 'Standard')}</td></tr>
    </table>

    <p><em>Disclaimer: Always verify with your department guidelines before final submission. Generated by ThesisFactory.</em></p>
</body>
</html>
    """
    with open(html_path, 'w') as f:
        f.write(html_content)

def generate_global_index(universities):
    """Generates the main homepage with client-side search."""
    index_path = os.path.join(OUTPUT_DIR, "index.html")
    
    # Pre-render list items for SEO, but JS will filter them
    list_items = ""
    for uni in universities:
        link = f"{uni['id']}/index.html"
        list_items += f'<li class="uni-item"><a href="{link}"><strong>{uni["uni_name"]}</strong> - {uni["course_name"]}</a></li>\n'

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ThesisFactory - Free University Thesis Templates</title>
    <meta name="description" content="Search and download free, compliant thesis templates for universities worldwide.">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
        #search {{ width: 100%; padding: 15px; font-size: 16px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 20px; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ padding: 10px; border-bottom: 1px solid #eee; }}
        li a {{ text-decoration: none; color: #007bff; display: block; }}
        li a:hover {{ background-color: #f8f9fa; }}
    </style>
</head>
<body>
    <h1>🎓 Thesis Template Factory</h1>
    <p>Search your university to download a 100% compliant Word template.</p>
    
    <input type="text" id="search" placeholder="Search by University or Course name..." onkeyup="filterList()">
    
    <ul id="uniList">
        {list_items}
    </ul>

    <script>
        function filterList() {{
            var input, filter, ul, li, a, i, txtValue;
            input = document.getElementById('search');
            filter = input.value.toUpperCase();
            ul = document.getElementById("uniList");
            li = ul.getElementsByTagName("li");
            for (i = 0; i < li.length; i++) {{
                a = li[i].getElementsByTagName("a")[0];
                txtValue = a.textContent || a.innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {{
                    li[i].style.display = "";
                }} else {{
                    li[i].style.display = "none";
                }}
            }}
        }}
    </script>
</body>
</html>
    """
    with open(index_path, 'w') as f:
        f.write(html_content)

# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    print("🏭 Starting Thesis Factory...")
    
    if not os.path.exists(DATA_FILE):
        print(f"❌ Error: {DATA_FILE} not found!")
        sys.exit(1)
        
    try:
        with open(DATA_FILE, 'r') as f:
            universities = json.load(f)
            
        for uni in universities:
            try:
                process_university(uni)
                # Build Web Page for this uni
                target_dir = os.path.join(OUTPUT_DIR, uni.get("id"))
                generate_web_page(target_dir, uni)
            except Exception as e:
                print(f"⚠️ Failed to process {uni.get('id', 'Unknown')}: {e}")
        
        # Build Global Search Index
        generate_global_index(universities)
        print("🌍 Website generated at Output/index.html")
                
        print("\n✨ All jobs completed.")
        
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON format in data.json")
    except Exception as e:
        print(f"❌ Critical Error: {e}")
