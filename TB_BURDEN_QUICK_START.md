# TB Burden - Quick Start Guide

## ✅ Status: Fully Integrated

TB Burden is now **part of** the Tuberculosis dashboard - not a separate page!

## 🚀 How to Access (5 Steps)

```bash
1. streamlit run website.py
```

Then in the browser:

```
2. Sidebar → Health Topic: Select "Tuberculosis"
3. Sidebar → Click "🚀 Initialize System" button
4. Wait for "✓ TB Burden data loaded successfully!" message
5. Sidebar → Click "📊 Dashboard" button
6. Scroll down to see "📉 TB Burden Estimates" section
```

## 📊 What You'll See

### TB Burden Section (at bottom of TB dashboard):

**Four Overview Cards:**
- TB Incident Cases
- Regional Incidence Rate (per 100,000)
- TB/HIV Cases  
- TB Deaths

**Four Interactive Tabs:**

1. **🔴 High Burden Countries**
   - Top 10 by incidence
   - Top 10 by mortality
   
2. **🟢 Low Burden Countries**
   - Bottom 10 by incidence
   - Bottom 10 by mortality
   
3. **🗺️ Burden Maps**
   - Interactive Africa maps
   - Multiple indicators
   - Regional trends 2000-2024
   
4. **⚖️ Equity Analysis**
   - Distribution plots
   - Inequality measures
   - Variation statistics

## 💡 Key Points

✅ **Integrated**: TB Burden is inside the TB dashboard, not separate
✅ **Automatic**: Loads when you initialize Tuberculosis topic
✅ **Complete**: 47 countries, 2000-2024, 1,164 records
✅ **Total Counts**: Uses sum totals, not means/medians
✅ **Equity**: Includes inequality and distribution analysis

## 📈 Data Coverage

- **Countries**: 47 WHO AFRO members
- **Time Period**: 2000 - 2024 (25 years)
- **Latest Year**: 2024
- **Total Records**: 1,164
- **Latest TB Cases**: ~2.6 million (2024)
- **Source**: WHO Global TB Programme

## ⚠️ If Not Showing

**Check these:**
- [ ] "Tuberculosis" selected as Health Topic (not Mortality)
- [ ] System initialized (click "Initialize System" button)
- [ ] Success message appeared
- [ ] On Dashboard page (not Home or Chatbot)
- [ ] Scrolled down to bottom of dashboard

**Look for in sidebar:**
```
System Status: ✓ System Ready
Health Topic: Tuberculosis
TB Burden Records: 1,164
Year Range: 2000-2024
```

## 🎯 What's Different from Notifications/Outcomes

| Data Type | What It Shows |
|-----------|---------------|
| **Notifications** | Cases reported by countries |
| **Outcomes** | Treatment results for reported cases |
| **Burden** | WHO estimates (includes unreported) |

**TB Burden = True disease burden** (accounts for under-diagnosis)

## 📝 Quick Test

```bash
# Verify data loads correctly
python3 check_tb_burden_setup.py

# Should show:
# ✓ All files present
# ✓ 47 AFRO countries
# ✓ 1,164 records
# ✓ Data loads successfully
```

## 🔗 Related Sections

When viewing TB Dashboard, you'll see:

1. **TB Notifications** (top)
2. **TB Outcomes** (middle)
3. **TB Burden Estimates** (bottom) ← NEW!

All three work together to provide complete TB picture!

---

**Need Help?**
- See full documentation: `TB_BURDEN_INTEGRATED.md`
- Run checker: `check_tb_burden_setup.py`
- Check website compiles: `python3 -m py_compile website.py`

