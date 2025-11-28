# Quick Installation Guide

## 🚀 New Features Added

1. **LLM Reports with Dashboard Integration** - Uses actual dashboard data and interactive charts
2. **Chart Selection Interface** - Choose which dashboard charts to include in reports
3. **Strict Indicator Constraints** - LLM focuses only on selected indicators
4. **Chart Preview** - See dashboard charts before generating report
5. **Word/PDF Export** - Professional exports with embedded dashboard charts
6. **Homepage Cards** - Beautiful vibrant gradients with automatic year ranges
7. **All Features** - Fully integrated and ready to use!

---

## 📦 Install New Dependencies

Run this command to install all required packages:

```bash
pip install -r requirements.txt
```

### Or install individually:

```bash
pip install python-docx markdown kaleido requests
```

### New Packages:
- **python-docx** - Word document export
- **markdown** - Markdown to HTML conversion
- **kaleido** - Chart image export (for Word/PDF)
- **requests** - Already installed (for auto-translation)

---

## ⚙️ Setup API Key

Make sure your `.env` file has:

```
OPENROUTER_API_KEY=your_key_here
```

This is needed for:
- LLM report generation
- Automatic translation

---

## ✅ Verify Installation

Run this to test:

```bash
python3 -c "import docx; import markdown; import kaleido; print('✅ All packages installed!')"
```

---

## 🎯 What's Ready

### 1. Beautiful Homepage Cards
- **Automatic:** Just run the app!
- **Year ranges:** Pull from data automatically (1980-2024)
- **Colors:** 4 vibrant gradients (purple, pink, blue, green)
- **Contrast:** White text on colorful backgrounds

### 2. Enhanced LLM Reports
**How to use:**
1. Go to **Reports** page
2. Select **TB Category** (Burden/Notifications/Outcomes)
3. Select **Specific Indicators** (e.g., incidence, mortality)
4. Click **"Generate Report"**
5. Report will:
   - Focus ONLY on selected indicators ✅
   - Include embedded charts ✅
   - Have 3 download buttons (Text/Word/PDF) ✅

**Downloads:**
- 📄 **Text** - Markdown format
- 📘 **Word** - Formatted document with chart images
- 📕 **PDF** - Styled document with chart images

---

## 🏃 Run the App

```bash
streamlit run website.py
```

---

## 🧪 Test the Features

### Test 1: Homepage Cards
1. Open homepage
2. Select any health topic
3. Click "Initialize System"
4. See beautiful gradient cards with white text
5. Card 4 shows year range (e.g., "1980-2024")

### Test 2: LLM Reports with Dashboard Integration
1. Go to **Dashboard** page first
   - Select Tuberculosis → TB Burden
   - Note the Regional Trend chart
   - Note the Top 10 High Burden chart
   - Remember the styling and values

2. Go to **Reports** page
3. Select **"Tuberculosis"**
4. Select **"TB Burden"**
5. Select indicators:
   - ☑️ e_inc_num (TB Incidence Cases)
   - ☑️ e_mort_num (TB Mortality Cases)
6. Select chart types:
   - ☑️ Regional Trend
   - ☑️ Top 10 High Burden
7. Click "Preview Charts" (expandable)
   - Charts should match dashboard EXACTLY
   - Same styling, same data
8. Generate report
9. Verify:
   - Report mentions ONLY incidence and mortality ✅
   - Dashboard charts embedded in report ✅
   - LLM references dashboard charts ✅
   - 3 download buttons available ✅
10. Download Word version
11. Open in Microsoft Word
12. See embedded dashboard chart images!
13. Compare to dashboard - should match exactly ✅

---

## ❓ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'docx'"
**Fix:** Install python-docx
```bash
pip install python-docx
```

### Issue: "ModuleNotFoundError: No module named 'kaleido'"
**Fix:** Install kaleido
```bash
pip install kaleido
```

### Issue: Charts not appearing in Word
**Fix:** Make sure kaleido is installed (handles chart→image conversion)

### Issue: PDF not working
**Note:** PDF uses HTML fallback. For full PDF support, additional setup needed.
Word export works perfectly!

---

## 📊 Expected Results

### Homepage Cards:

**Card 1 (Purple):**
- Background: Purple gradient
- Text: White "47"
- Label: White "AFRO COUNTRIES"

**Card 2 (Pink/Red):**
- Background: Pink to red gradient
- Text: White indicator count
- Label: White "TB INDICATORS"

**Card 3 (Blue/Cyan):**
- Background: Blue to cyan gradient
- Text: White record count
- Label: White "RECORDS"

**Card 4 (Green/Teal):**
- Background: Green to teal gradient
- Text: White "1980-2024" (or current range)
- Label: White "YEAR RANGE"

### LLM Reports:

**Generated Report:**
```markdown
## Executive Summary
Analysis of TB Incidence and Mortality...

## TB Incidence Analysis
[Details about incidence ONLY]

[CHART: e_inc_num (TB Incidence Cases)]
← Chart appears here!

## TB Mortality Analysis
[Details about mortality ONLY]

[CHART: e_mort_num (TB Mortality Cases)]
← Chart appears here!
```

**Word Download:**
- Professional formatting
- Charts embedded as images
- Editable in Word
- Ready for official use

---

## ✅ Success Indicators

You'll know it's working when:

### Homepage:
- ✅ Cards have vibrant gradient backgrounds
- ✅ Text is white and easy to read
- ✅ Card 4 shows "1980-2024" or similar
- ✅ Smooth hover animations

### Reports:
- ✅ Report focuses ONLY on selected indicators
- ✅ Charts display in report body
- ✅ 3 download buttons appear (Text, Word, PDF)
- ✅ Word download includes chart images
- ✅ Success message shows chart count

---

## 🎉 You're All Set!

**Everything is ready to use:**
- Beautiful homepage with automatic year ranges ✅
- LLM reports with strict indicator focus ✅
- Charts embedded in reports ✅
- Professional Word/PDF exports ✅

**Enjoy your enhanced AFRO Analytics platform!** 🚀📊

---

## 📖 More Info

- **Full LLM Report Details:** See `LLM_REPORTS_ENHANCED.md`
- **Translation System:** See `AUTO_TRANSLATION_GUIDE.md`
- **TB Analytics:** See dashboard tabs for all features

---

**Status:** ✅ Ready for Production!

