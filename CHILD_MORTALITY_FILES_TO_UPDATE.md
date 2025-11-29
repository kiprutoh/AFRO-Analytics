# Files to Update for Child Mortality Data

## 📋 Summary
This document lists all files that need to be updated when working with Child Mortality data from `Child Mortality.csv`.

---

## 🔧 Core Data Processing Files

### 1. `mortality_analytics.py` ⭐ **PRIMARY FILE**
**Purpose**: Contains the data loading pipeline and analytics for Child Mortality
**Key Classes**:
- `MortalityDataPipeline`: Loads and processes `Child Mortality.csv`
- `ChildMortalityAnalytics`: Analytics methods for child mortality indicators

**What to update**:
- Indicator name mappings (e.g., "Child Mortality rate age 1-4" → "Child mortality rate (aged 1-4 years)")
- Data filtering logic (AFRO countries, years 2000-2024)
- Indicator definitions and calculations

**Status**: ✅ **UPDATED** - Fixed indicator name mapping

---

### 2. `mortality_charts.py`
**Purpose**: Generates charts and visualizations for Child Mortality data
**Key Classes**:
- `ChildMortalityChartGenerator`: Chart generation methods

**What to update**:
- Chart methods to use correct indicator names
- Visualization logic for child mortality indicators
- Chart titles and labels

**Status**: ⚠️ **NEEDS REVIEW** - Verify indicator names match

---

## 🌐 Main Application Files

### 3. `website.py` ⭐ **PRIMARY FILE**
**Purpose**: Main Streamlit application that displays Child Mortality dashboard
**Key Functions**:
- `initialize_system()`: Loads Child Mortality data (lines ~866-930)
- `render_child_mortality_section()`: Displays Child Mortality dashboard (lines ~2645-2850)
- `render_mortality_dashboard()`: Main mortality dashboard with tabs
- `render_mortality_visualizer()`: Interactive visualizer for Child Mortality

**What to update**:
- Data initialization logic
- Dashboard display logic
- Indicator selection dropdowns
- Chart rendering calls

**Status**: ✅ **UPDATED** - Error handling and data validation added

---

## 🤖 Chatbot Integration

### 4. `rdhub_chatbot.py`
**Purpose**: Pydantic AI chatbot that can answer questions about Child Mortality
**Key Components**:
- `RDHUBDependencies`: Includes `child_analytics`
- `get_mortality_country_data()`: Tool for accessing child mortality data

**What to update**:
- Indicator name references in tool descriptions
- Data access methods

**Status**: ⚠️ **NEEDS REVIEW** - Verify indicator names in tool descriptions

---

## 📊 Data Files

### 5. `Child Mortality.csv` ⭐ **DATA FILE**
**Purpose**: Source data file for Child Mortality
**Format**: Clean format with columns: `iso`, `country`, `indicator`, `sex`, `year`, `value`, `Lower Bound`, `Upper Bound`

**What to know**:
- File size: 6.62 MB (optimized from 80.82 MB)
- Contains data for 25 AFRO countries
- Years: 2000-2024
- Key indicators:
  - "Under-five mortality rate" ✅
  - "Infant mortality rate" ✅
  - "Child Mortality rate age 1-4" (maps to "Child mortality rate (aged 1-4 years)")

**Status**: ✅ **OPTIMIZED** - Reduced to 6.62 MB

---

### 6. `look up file WHO_AFRO_47_Countries_ISO3_Lookup_File.csv`
**Purpose**: Lookup file for AFRO country ISO3 codes
**Used by**: `MortalityDataPipeline` to filter Child Mortality data to AFRO countries only

**Status**: ✅ **REQUIRED** - Must be present

---

## 🔍 Report Generation

### 7. `llm_report_generator.py`
**Purpose**: Generates LLM-powered reports for Child Mortality
**What to update**:
- Indicator name references in prompts
- Report generation logic for child mortality

**Status**: ⚠️ **NEEDS REVIEW** - Verify indicator names in report templates

---

## 📝 Translation Files

### 8. `translations.py`
**Purpose**: Multilingual translations for the website
**What to update**:
- Child Mortality related translations
- Indicator name translations

**Status**: ⚠️ **MAY NEED UPDATE** - If indicator names change

---

## 🎯 Quick Reference: Indicator Name Mapping

| Data File Name | Code Expects | Status |
|---------------|--------------|--------|
| "Under-five mortality rate" | "Under-five mortality rate" | ✅ Match |
| "Infant mortality rate" | "Infant mortality rate" | ✅ Match |
| "Child Mortality rate age 1-4" | "Child mortality rate (aged 1-4 years)" | ✅ **FIXED** - Now mapped |

---

## ✅ Files Already Updated

1. ✅ `mortality_analytics.py` - Fixed indicator name mapping
2. ✅ `website.py` - Added error handling and data validation
3. ✅ `Child Mortality.csv` - Optimized to 6.62 MB

---

## ⚠️ Files That May Need Updates

1. ⚠️ `mortality_charts.py` - Verify chart methods use correct indicator names
2. ⚠️ `rdhub_chatbot.py` - Verify tool descriptions match indicator names
3. ⚠️ `llm_report_generator.py` - Verify report templates use correct indicator names

---

## 🚀 Next Steps

1. Test Child Mortality dashboard with updated indicator mapping
2. Verify all charts display correctly
3. Test chatbot queries about Child Mortality
4. Verify LLM reports generate correctly for Child Mortality

---

## 📌 Key Indicator Names in Data

- ✅ "Under-five mortality rate" - **Matches code**
- ✅ "Infant mortality rate" - **Matches code**
- ✅ "Child Mortality rate age 1-4" - **Now mapped to "Child mortality rate (aged 1-4 years)"**

---

**Last Updated**: After fixing indicator name mapping issue
**Issue Fixed**: "Child Mortality rate age 1-4" now correctly mapped to "Child mortality rate (aged 1-4 years)"

