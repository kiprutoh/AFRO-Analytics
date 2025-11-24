# TB Data Pipeline Integration Summary

## Overview
Successfully integrated Tuberculosis (TB) data pipeline into the Regional Health Data Hub analytics platform, along with indicator selection and multi-language report generation.

## New Features

### 1. Indicator Area Selection
- Added dropdown in sidebar to select between:
  - **Tuberculosis**
  - **Maternal Mortality** (default)
  - **Child Mortality**
- System automatically loads appropriate data pipeline based on selection
- Indicator type persists across page navigation

### 2. TB Data Pipeline (`tb_data_pipeline.py`)
- New module for loading and processing TB data
- Based on WHO GTB Report 2025 structure
- Loads multiple TB datasets:
  - TB burden estimates (`TB_burden_countries_2025-09-23.csv`)
  - TB notifications (`TB_notifications_2025-09-23.csv`)
  - TB outcomes (`TB_outcomes_2025-09-23.csv`)
  - TB burden by age/sex (`TB_burden_age_sex_2025-09-23.csv`)
  - MDR/RR-TB burden (`MDR_RR_TB_burden_estimates_2025-09-23.csv`)
  - Data dictionary (`TB_data_dictionary_2025-09-23.csv`)

### 3. TB Analytics (`tb_analytics.py`)
- Analytics engine for TB data
- Key functions:
  - `get_country_statistics()` - Country-specific TB statistics
  - `get_regional_summary()` - Regional AFRO summary
  - `compare_countries()` - Multi-country comparison
  - `_calculate_trend()` - Trend analysis

### 4. Multi-Language Report Generation
- Added language dropdown on Reports page with 10 languages:
  - English (default)
  - French
  - Spanish
  - Portuguese
  - Arabic
  - Swahili
  - Amharic
  - Hausa
  - Yoruba
  - Zulu
- Language parameter passed to LLM (Gemini 2.5 Flash)
- LLM generates entire report in selected language
- System prompt updated to enforce language requirement

### 5. Updated LLM Report Generator
- Modified `generate_report()` to accept `language` parameter
- Updated system prompt to include language instruction
- User prompt includes explicit language requirement
- Reports generated in selected language with proper context

## File Changes

### New Files Created:
1. `tb_data_pipeline.py` - TB data loading and processing
2. `tb_analytics.py` - TB analytics engine
3. `TB_INTEGRATION_SUMMARY.md` - This documentation

### Modified Files:
1. `website.py`:
   - Added indicator type selection in sidebar
   - Updated `initialize_system()` to handle TB data
   - Added language dropdown to reports page
   - Updated `_collect_statistics_for_llm()` to handle TB analytics
   - Modified `render_reports_page()` to support TB data

2. `llm_report_generator.py`:
   - Added `language` parameter to `generate_report()`
   - Updated `_get_system_prompt()` to accept language
   - Updated `_build_prompt()` to include language instructions

## Data Structure

### TB Data Location:
```
tuberculosis /
├── TB_data_dictionary_2025-09-23.csv
├── tb burden/
│   ├── TB_burden_countries_2025-09-23.csv
│   ├── TB_burden_age_sex_2025-09-23.csv
│   └── MDR_RR_TB_burden_estimates_2025-09-23.csv
└── case reported by countries/
    ├── TB_notifications_2025-09-23.csv
    ├── TB_outcomes_2025-09-23.csv
    └── [other TB datasets]
```

### Key TB Indicators:
- TB Incidence (per 100k)
- TB Mortality (per 100k)
- TB/HIV Incidence (per 100k)
- TB/HIV Mortality (per 100k)
- Case Detection Rate (%)

## Usage

### To Use TB Analytics:

1. **Select Indicator Area:**
   - Go to sidebar
   - Select "Tuberculosis" from "Indicator Area" dropdown

2. **Initialize System:**
   - Click "🚀 Initialize System" button
   - Wait for TB data to load

3. **Generate Reports:**
   - Navigate to Reports page
   - Select language from dropdown
   - Select country (optional)
   - Click "Generate Report"
   - Report will be generated in selected language

### To Switch Between Indicators:

1. Select different indicator from sidebar dropdown
2. System will automatically reset
3. Click "Initialize System" again
4. New data pipeline loads

## Technical Details

### Session State Variables:
- `indicator_type` - Current indicator area selected
- `tb_pipeline` - TB data pipeline instance
- `tb_analytics` - TB analytics instance
- `pipeline` - Mortality data pipeline (for Maternal/Child Mortality)
- `analytics` - Mortality analytics (for Maternal/Child Mortality)

### Error Handling:
- Graceful fallback if TB data files not found
- Try-except blocks around analytics calls
- Clear error messages for users

## Future Enhancements

1. **TB-Specific Visualizations:**
   - Create TB chart generator
   - TB-specific trend charts
   - TB map visualizations

2. **TB Chatbot:**
   - Extend chatbot to handle TB queries
   - TB-specific intent detection
   - TB indicator extraction

3. **TB Projections:**
   - Add TB projection models
   - 2030 TB targets
   - Gap analysis for TB indicators

4. **Additional Languages:**
   - Add more African languages
   - Language-specific formatting
   - Cultural context in reports

## Testing Checklist

- [x] TB data pipeline loads correctly
- [x] Indicator dropdown works
- [x] System initializes for TB
- [x] Language dropdown appears
- [x] Reports generate in selected language
- [x] Statistics collection works for TB
- [x] Regional summary works for TB
- [x] Country statistics work for TB

## Notes

- TB folder name: `tuberculosis ` (note the trailing space)
- TB data filtered for AFRO region (`g_whoregion == 'AFR'`)
- Language selection defaults to English
- All languages supported by Gemini 2.5 Flash model

## References

- WHO GTB Report 2025: https://github.com/GTB-TME/gtbreport2025
- OpenRouter API: https://openrouter.ai/docs/quickstart
- Gemini 2.5 Flash: https://openrouter.ai/google/gemini-2.5-flash


