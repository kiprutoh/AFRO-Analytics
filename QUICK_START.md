# Quick Start Guide - TB Subcategory Selection

## ✅ What's New

**TB Dashboard now starts with TB Burden and has subcategory selection throughout!**

---

## 🚀 Quick Start (5 Steps)

```bash
1. streamlit run website.py
2. Sidebar → Select "Tuberculosis"
3. Sidebar → Click "🚀 Initialize System"
4. Sidebar → Click "📊 Dashboard"
5. See TB Burden section (DEFAULT/FIRST) ✨
```

---

## 📊 TB Dashboard Structure

### Three Category Buttons (Top of page):

```
┌──────────────┬─────────────────┬─────────────┐
│ 📉 TB Burden │ 📊 TB           │ ✅ TB       │
│  (PRIMARY)   │  Notifications  │  Outcomes   │
└──────────────┴─────────────────┴─────────────┘
```

**Click any button to switch categories instantly!**

### What Each Category Shows:

**📉 TB Burden (Default)**
- WHO burden estimates (2000-2024)
- Incidence, mortality, TB/HIV data
- High/low burden countries
- Maps and equity analysis

**📊 TB Notifications**
- Reported TB cases
- Age distribution
- Notification types
- Temporal trends

**✅ TB Outcomes**
- Treatment success rates
- Cure/failure/death rates
- Country performance
- Outcomes breakdown

---

## 📋 Generate Focused Reports

### New Feature: Select Category & Indicators

```
Reports Page:
1. Choose TB Category: [TB Burden ▼]
2. Select: ⚪ All Indicators  ⚫ Select Specific
3. Pick indicators (if specific)
4. Generate focused report
```

**Categories Available:**
- All TB Data
- TB Burden only
- TB Notifications only
- TB Outcomes only

---

## 📈 Create Category-Specific Visualizations

### Interactive Visualizer with Category Selection

```
Visualizer Page:
1. Click category button (Burden/Notifications/Outcomes)
2. See category-specific indicator options
3. Create custom charts
4. Switch categories anytime
```

---

## 💡 Key Benefits

✅ **TB Burden First**: Most comprehensive data shown by default
✅ **Easy Switching**: One-click category changes
✅ **Focused Reports**: Generate reports for specific TB aspects
✅ **Better Navigation**: Clear separation of data types
✅ **Flexible Analysis**: Choose relevant indicators only

---

## 🎯 Common Use Cases

### 1. Assess Regional TB Burden
```
Dashboard → TB Burden (default)
View: Regional overview + high burden countries
Action: Generate burden-specific report
```

### 2. Analyze Treatment Outcomes
```
Dashboard → TB Outcomes button
View: Success rates + country performance
Action: Create outcomes-focused visualizations
```

### 3. Study Case Notifications
```
Dashboard → TB Notifications button
View: Case trends + age distribution
Action: Generate notifications report with selected indicators
```

---

## 📁 Documentation

- **Full Details**: `TB_SUBCATEGORY_SELECTION_SUMMARY.md`
- **TB Burden Info**: `TB_BURDEN_INTEGRATED.md`
- **Quick TB Burden**: `TB_BURDEN_QUICK_START.md`

---

## ✅ Verification

**Check these when running:**
- [ ] TB Burden appears first on dashboard
- [ ] Three category buttons visible and working
- [ ] Reports page has category/indicator selection
- [ ] Visualizer has category buttons
- [ ] Switching categories works smoothly

---

## 🆘 Troubleshooting

**If subcategory buttons don't appear:**
- Ensure "Tuberculosis" is selected as Health Topic
- System must be initialized
- Refresh page if needed

**If TB Burden doesn't show:**
- Check sidebar for "TB Burden Records: 1,164"
- Look for initialization success message
- Data files must be present

---

**Status**: ✅ Ready to Use
**Version**: 2.0
**Last Updated**: Nov 27, 2025

