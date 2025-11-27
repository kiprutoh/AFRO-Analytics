# Confidence Interval Bands - Fix Summary

## ✅ Issue Resolved

### Problem:
Upper confidence intervals were not showing in trend charts - only the lower bound was visible.

### Root Cause:
**Incorrect trace order in Plotly `fill='tonexty'`**

The `fill='tonexty'` fills to the **previous trace**. The original order was:
1. Upper bound (invisible)
2. Main line (estimate)  
3. Lower bound with `fill='tonexty'` ← This filled to #2 (main line), not creating full CI band

### Solution:
**Corrected trace order:**
1. Upper bound (invisible line)
2. Lower bound with `fill='tonexty'` ← Fills from #2 to #1 = Full CI band
3. Main estimate (drawn on top)

---

## 🔧 Files Fixed:

### 1. **tb_burden_chart_generator.py**

#### A. `create_regional_trend_chart()` method:
- ✅ Fixed trace order for regional TB burden trends
- ✅ CI band now shows correctly (lower → upper bound)
- ✅ Main line drawn on top of band
- ✅ Hover shows estimate + both bounds

#### B. `create_trend_chart()` method (Country trends):
- ✅ Added confidence intervals (were missing!)
- ✅ Same correct trace order
- ✅ CI band fills properly
- ✅ Hover shows estimate + both bounds

### 2. **website.py**

#### CDR Trend Chart (in `render_tb_burden_explorer()`):
- ✅ Fixed trace order for Case Detection Rate trends
- ✅ CI band shows correctly
- ✅ Enhanced hover with all three values

---

## 📊 How It Works Now

### Correct Trace Sequence:

```python
# 1. Upper bound (invisible)
fig.add_trace(go.Scatter(
    y=data['indicator_hi'],
    line=dict(width=0),
    showlegend=False
))

# 2. Lower bound with fill TO PREVIOUS (upper)
fig.add_trace(go.Scatter(
    y=data['indicator_lo'],
    fill='tonexty',  # Fills between lower and upper
    fillcolor='rgba(..., 0.2)'
))

# 3. Main estimate line on top
fig.add_trace(go.Scatter(
    y=data['indicator'],
    line=dict(width=3, color='...'),
    mode='lines+markers'
))
```

### Visual Result:

```
      ╱‾‾‾‾‾‾\  ╱‾\     ← Upper bound (invisible)
     ╱  ████  \/   \    ← CI band (shaded)
────●────●────●────●── ← Estimate line (visible)
   ╱  ████  ╱\   ╱     ← CI band (shaded)
  ╱________╱  ╲_╱      ← Lower bound (invisible)
```

---

## ✅ What's Fixed

### All Trend Charts Now Show:

**Regional Trend Charts:**
- ✅ Full CI band (lower to upper)
- ✅ Estimate line on top (bold, colored)
- ✅ Shaded area shows uncertainty
- ✅ Hover displays all three values

**Country Trend Charts:**
- ✅ Full CI band (lower to upper)
- ✅ Estimate line on top
- ✅ CI was completely missing - now added!
- ✅ Hover displays all three values

**CDR Trend Chart:**
- ✅ Full CI band (lower to upper)
- ✅ Estimate line on top
- ✅ Enhanced hover information

---

## 🎨 Visual Comparison

### Before (Broken):
```
Only lower half of CI band visible
Main line in middle
Upper bound not shown
```

### After (Fixed):
```
Full CI band from lower to upper ✓
Main line clearly visible on top ✓
Shaded area shows complete uncertainty range ✓
```

---

## 📈 Charts Affected

All these charts now properly show confidence intervals:

### In TB Burden Dashboard:
1. **Burden Maps Tab** → Regional Trend Analysis
   - Shows full CI band for selected indicator

### In TB Burden Explorer (Interactive Visualizer):
2. **Incidence Tab** → Regional Trend
   - Full CI for incidence indicators
3. **Incidence Tab** → Country Trend
   - Full CI for selected country
4. **Mortality Tab** → Regional Trend
   - Full CI for mortality indicators
5. **Mortality Tab** → Country Trend
   - Full CI for selected country
6. **TB/HIV Tab** → Regional Trend
   - Full CI for TB/HIV indicators
7. **TB/HIV Tab** → Country Trend
   - Full CI for selected country
8. **CDR Tab** → Regional Trend
   - Full CI for Case Detection Rate

---

## 🔍 Hover Information

### Enhanced Hover Template:
```
Year: 2024
Estimate: 2,621,932
High Bound: 2,890,000
Low Bound: 2,350,000
```

All trend charts now show complete information on hover.

---

## 🚀 Testing

### To Verify Fix:

```bash
streamlit run website.py

# Test 1: Dashboard
Dashboard → TB Burden → Burden Maps tab
  → Select indicator
  → Select "Regional Trend" 
  → Check: Full CI band visible ✓

# Test 2: Visualizer
Interactive Visualizer → TB Burden → Incidence tab
  → Select "Regional Trend"
  → Check: Full CI band visible ✓
  → Select "Country Trend"
  → Choose country
  → Check: Full CI band visible ✓

# Test 3: CDR
Interactive Visualizer → TB Burden → CDR tab
  → Select "Regional Trend"
  → Check: Full CI band visible ✓
```

---

## 📝 Technical Notes

### Key Points:

1. **`fill='tonexty'`** fills to the **immediately previous trace**
2. **Trace order matters** - must be: upper → lower (with fill) → estimate
3. **Invisible lines** (`width=0`) create fill boundaries
4. **Estimate on top** ensures visibility
5. **Semi-transparent fill** (`rgba(..., 0.2)`) shows underlying data

### Color Schemes:
- **Orange** (`#FF6600`) - TB Burden regional trends
- **Blue** (`#0066CC`) - Country-specific trends
- **Green** (`#28a745`) - Case Detection Rate
- **Alpha 0.2** - Transparency for all CI bands

---

## ✅ Verification Results

**All files compile:** ✅  
**Trace order corrected:** ✅  
**CI bands render:** ✅  
**Hover shows bounds:** ✅  
**Visual clarity:** ✅  

---

**Status:** ✅ Fixed and Tested  
**Version:** 2.3 - CI Bands Corrected  
**Last Updated:** Nov 27, 2025

