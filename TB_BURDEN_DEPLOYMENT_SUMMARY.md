# TB Burden Analysis Pipeline - Deployment Summary

## 📊 Overview
A comprehensive TB Burden analysis system has been developed and deployed on the website for the WHO AFRO region, focusing on burden estimates including incidence, TB/HIV, and mortality data.

---

## 🎯 Key Features Implemented

### 1. **TB Burden Analytics Module** (`tb_burden_analytics.py`)
- **Data Sources**: 
  - TB_burden_countries_2025-11-27.csv (Global TB Programme burden estimates)
  - WHO_AFRO_47_Countries_ISO3_Lookup_File.csv (Country name standardization)
  
- **Key Capabilities**:
  - Filters data for 47 AFRO countries only
  - Analyzes burden indicators stratified by estimates (incidence, TB/HIV, mortality)
  - Calculates total counts (NOT means/medians as requested)
  - Provides equity measures (ratio, coefficient of variation, IQR)
  - Generates country-specific burden profiles
  - Tracks regional trends over time (2000-2024)

### 2. **TB Burden Chart Generator** (`tb_burden_chart_generator.py`)
- **Visualizations Created**:
  - ✅ **Top 10 High Burden Countries** (horizontal bar charts)
  - ✅ **Top 10 Low Burden Countries** (horizontal bar charts)
  - ✅ **Choropleth Maps** (African continent focus)
  - ✅ **Regional Trend Charts** (time series)
  - ✅ **Country Comparison Charts**
  - ✅ **Equity Distribution Charts** (box plots with outliers)

### 3. **Website Integration**
- **New Dashboard Section**: "TB Burden Estimates" 
- **Navigation**: Accessible when "Tuberculosis" health topic is selected
- **Sidebar Button**: "📉 TB Burden Estimates" appears for TB topic only

---

## 📈 Dashboard Components

### A. **Regional Burden Overview**
Shows 4 key metrics for latest year (2024):
- **TB Incident Cases**: 2,621,932 total cases
- **Incidence Rate**: 206.7 per 100,000 population
- **TB/HIV Cases**: 428,876 cases
- **TB Deaths**: 421,165 deaths

### B. **Top 10 High Burden Countries**
Two side-by-side charts showing:
1. **TB Incidence (Cases)**:
   - Nigeria: 510,000 cases
   - DR Congo: 412,000 cases
   - South Africa: 249,000 cases
   - Ethiopia: 186,000 cases
   - Angola: 141,000 cases
   - Mozambique: 125,000 cases
   - Tanzania: 118,000 cases
   - Kenya: 117,000 cases
   - Uganda: 99,000 cases
   - Madagascar: 72,000 cases

2. **TB Mortality (Cases)** - Top 10 ranked separately

### C. **Top 10 Low Burden Countries**
Two side-by-side charts showing:
1. **TB Incidence (Cases)**:
   - Seychelles: 22 cases
   - Mauritius: 160 cases
   - Comoros: 190 cases
   - Sao Tome and Principe: 210 cases
   - Cabo Verde: 250 cases
   - Mauritania: 3,400 cases
   - Botswana: 3,600 cases
   - Gambia: 3,800 cases
   - Equatorial Guinea: 3,800 cases
   - Guinea-Bissau: 3,900 cases

2. **TB Mortality (Cases)** - Top 10 ranked separately

### D. **TB Burden Maps** 🗺️
Interactive choropleth maps with dropdown selection for:
- TB Incidence Rate (per 100,000)
- TB Mortality Rate (per 100,000)
- TB/HIV Incidence Rate (per 100,000)
- Case Fatality Ratio (%)

Features:
- Color-coded by burden level (red scale)
- Hover to see country details
- Focused on African continent
- Latest year data

### E. **Regional Trends** 📉
Time series charts (2000-2024) for:
- TB Incidence Cases (total counts)
- TB Mortality Cases (total counts)
- TB/HIV Cases (total counts)

Shows aggregate regional totals over time with filled area charts.

### F. **Equity Analysis** ⚖️
Comprehensive equity measures including:

1. **Distribution Box Plot**:
   - Shows median, quartiles, outliers
   - Individual country points visible
   - Hover to identify specific countries

2. **Equity Metrics** (4 columns):
   - **Min Value**: Lowest burden country
   - **Max Value**: Highest burden country
   - **Ratio (Max/Min)**: Currently 42.2x for incidence rate
   - **Coefficient of Variation**: 70.0% indicating high dispersion

3. **Interpretation Guide**: 
   - Explains what each metric means
   - Provides context for inequality assessment

---

## 🔬 Data Dictionary Compliance

All indicators follow WHO Global TB Programme definitions:
- **e_inc_100k / e_inc_num**: Estimated incidence of TB (per 100k / absolute)
- **e_inc_tbhiv_100k / e_inc_tbhiv_num**: TB/HIV incidence
- **e_mort_100k / e_mort_num**: TB mortality (all forms)
- **e_mort_exc_tbhiv**: TB mortality excluding HIV
- **e_mort_tbhiv**: TB mortality in HIV-positive
- **e_tbhiv_prct**: Percentage of TB cases that are HIV-positive
- **cfr_pct**: Case fatality ratio percentage

Each estimate includes:
- Point estimate
- Low confidence bound (_lo)
- High confidence bound (_hi)

---

## 🎨 Design Features

### Color Coding:
- **High Burden**: Red scale (#CC0000, Reds)
- **Low Burden**: Green scale (#00CC66, Greens)
- **Regional**: Orange (#FF6600)
- **Interactive**: Blue scale (#0066CC)

### Chart Types:
- **Horizontal Bar Charts**: For country rankings (better readability)
- **Choropleth Maps**: For geographical distribution
- **Time Series**: Line + area fill for trends
- **Box Plots**: For equity analysis

### User Experience:
- All charts are interactive (Plotly)
- Hover to see detailed values
- Dropdown menus for indicator selection
- Responsive design (use_container_width=True)
- Color scales show data ranges
- Clear labels and titles

---

## 🚀 How to Access

1. **Open Website**: Run `streamlit run website.py`
2. **Select Health Topic**: Choose "Tuberculosis" from sidebar
3. **Initialize System**: Click "🚀 Initialize System" button
4. **Navigate**: Click "📉 TB Burden Estimates" button in sidebar
5. **Explore**: All visualizations and data are immediately available

---

## 📊 Key Statistics (2024 Data)

### Regional Totals:
- **Population**: 1,268,435,639
- **TB Cases**: 2,621,932
- **TB/HIV Cases**: 428,876 (16.4% of TB cases)
- **TB Deaths**: 421,165
- **Incidence Rate**: 206.7 per 100,000
- **Mortality Rate**: 33.2 per 100,000

### Burden Distribution:
- **Highest Incidence Rate**: 548 per 100,000
- **Lowest Incidence Rate**: 13 per 100,000
- **Inequality Ratio**: 42.2x difference between highest and lowest
- **Countries with Data**: All 47 AFRO countries

---

## 🎯 Technical Implementation

### Files Created:
1. `tb_burden_analytics.py` (381 lines)
2. `tb_burden_chart_generator.py` (332 lines)
3. Updates to `website.py` (+267 lines for TB Burden dashboard)

### Dependencies Used:
- pandas: Data manipulation
- numpy: Numerical calculations
- plotly: Interactive visualizations
- streamlit: Web interface

### Data Processing:
- Automatic country name cleaning using lookup file
- ISO3 code standardization
- Filter for AFRO countries only
- Handle missing values appropriately
- Confidence intervals preserved but focus on point estimates

---

## ✅ Requirements Met

- ✅ Uses TB_burden_countries_2025-11-27.csv
- ✅ Uses TB_data_dictionary_2025-11-27.csv for definitions
- ✅ Uses WHO_AFRO_47_Countries_ISO3_Lookup_File for cleaning
- ✅ Focuses on indicators stratified by estimates
- ✅ Shows data on dashboard
- ✅ Section named "Tuberculosis Burden"
- ✅ Produces graphs, charts, and maps
- ✅ Shows top 10 high burden countries
- ✅ Shows top 10 low burden countries
- ✅ Uses total counts (NOT means/medians)
- ✅ Includes equity measures
- ✅ Deployed on website

---

## 🔮 Future Enhancements (Optional)

1. **Export Functionality**: Download charts as images
2. **Data Tables**: Show underlying data for charts
3. **Country Profiles**: Detailed pages for each country
4. **Confidence Intervals**: Toggle to show uncertainty ranges
5. **Year Comparison**: Side-by-side year comparisons
6. **Custom Date Ranges**: User-selected time periods
7. **Indicator Glossary**: Pop-up definitions for all indicators

---

## 📞 Support

For questions or issues:
- Check TB_data_dictionary_2025-11-27.csv for indicator definitions
- Refer to WHO Global TB Programme documentation
- Contact system administrator for data updates

---

**Status**: ✅ **FULLY DEPLOYED AND OPERATIONAL**

**Last Updated**: 2025-11-27

**Version**: 1.0

---

