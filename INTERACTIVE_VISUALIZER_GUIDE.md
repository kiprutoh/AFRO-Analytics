# Interactive Visualizer Guide

## 🎯 New Features Added

### ✅ User-Controlled Chart Customization

Users now have full control over visualizations with:

1. **Country Selection** - Choose any single country
2. **Indicator Selection** - Select from all available indicators
3. **Prediction Method Selection** - Choose from 4 methods:
   - **Linear** - Straight line projection
   - **Exponential** - Exponential growth/decay projection
   - **Polynomial** - Curved projection (degree 2)
   - **Moving Average** - Based on recent trend
4. **Chart Type Selection** - Choose between:
   - **Chart** - Line chart with projections
   - **Map** - Choropleth map visualization
5. **Year Range Control**:
   - **Observed Data**: 2000-2023 (customizable start year)
   - **Projections**: 2024-2030 (customizable end year)
6. **Projection Shading** - Light orange shading for projected period

## 📊 Chart Features

### Observed Data (2000-2023)
- **Blue solid line** with markers
- Shows actual historical data
- Customizable start year (2000-2023)

### Projected Data (2024-2030)
- **Orange dashed line** with markers
- Light orange shaded area underneath
- Based on selected prediction method
- Customizable end year (2024-2030)

### SDG Target Lines
- Red dotted line showing 2030 targets
- Automatically displayed for relevant indicators:
  - MMR: <70 per 100,000
  - Under-five: <25 per 1,000
  - Neonatal: <12 per 1,000

### Visual Separator
- Gray dotted line at 2023.5 separating observed from projected

## 🗺️ Map Visualization

### Features:
- Choropleth map of Africa
- Color-coded by indicator value
- Hover for country details
- Year selection slider (2000-2023)
- Darker colors = Higher values

## 🎨 How to Use

### Step 1: Navigate to Interactive Charts
- Click **"📈 Interactive Charts"** in the sidebar

### Step 2: Configure Chart
1. **Select Country** - Choose from dropdown
2. **Select Indicator** - Choose mortality indicator
3. **Choose Visualization Type**:
   - **Chart** - For trend analysis with projections
   - **Map** - For geographic visualization
4. **If Chart selected**:
   - Choose **Prediction Method**
   - Toggle **Show Projections**
   - Set **Start Year** (observed data)
   - Set **End Year** (projections)

### Step 3: View Results
- Chart/map displays automatically
- Adjust controls to see changes in real-time

### Step 4: Multi-Country Comparison
- Scroll down to "Multi-Country Comparison"
- Select multiple countries
- See all trends on one chart

## 📈 Prediction Methods Explained

### Linear
- **Best for:** Steady trends
- **Method:** Straight line projection
- **Use when:** Trend is consistent

### Exponential
- **Best for:** Rapid changes
- **Method:** Exponential curve
- **Use when:** Values changing rapidly

### Polynomial
- **Best for:** Curved trends
- **Method:** Polynomial curve (degree 2)
- **Use when:** Trend has curvature

### Moving Average
- **Best for:** Recent trends
- **Method:** Based on last 3 years average
- **Use when:** Recent data is most relevant

## 🎯 Example Use Cases

### 1. Single Country Trend Analysis
```
Country: Kenya
Indicator: Under-five mortality rate
Type: Chart
Method: Linear
Show Projections: Yes
Result: Blue line (2000-2023) + Orange dashed line (2024-2030) with shading
```

### 2. Geographic Comparison
```
Indicator: MMR
Type: Map
Year: 2023
Result: Color-coded map showing MMR across Africa
```

### 3. Multi-Country Comparison
```
Countries: Kenya, Uganda, Tanzania
Indicator: Neonatal mortality rate
Result: Multiple lines showing trends for all countries
```

## 🔧 Technical Details

### New Files:
- `interactive_visualizer.py` - Visualization engine

### Updated Files:
- `website.py` - Added new page and navigation
- `requirements.txt` - Added scikit-learn and scipy

### Dependencies Added:
- `scikit-learn>=1.3.0` - For prediction methods
- `scipy>=1.11.0` - For statistical functions

## ✨ Key Features

✅ **Full User Control** - Choose everything
✅ **Multiple Prediction Methods** - 4 different approaches
✅ **Chart or Map** - Two visualization types
✅ **Custom Year Ranges** - Control observed and projected periods
✅ **Light Shading** - Visual distinction for projections
✅ **Multi-Country** - Compare multiple countries
✅ **Interactive** - Real-time updates

## 🚀 Next Steps

1. **Deploy updated code** to GitHub
2. **Redeploy on Streamlit Cloud**
3. **Test the new features**
4. **Share with users!**

The interactive visualizer gives users complete control over their analytics! 📊🎨

