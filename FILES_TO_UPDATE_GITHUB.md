# Files to Update on GitHub

## ✅ Botpress Chatbot Updated

The chatbot has been updated to use script-based integration instead of iframe.

---

## 📋 Files Modified (Must Update)

### 1. **Core Application Files**
- ✅ `website.py` - Updated Botpress integration (script tags instead of iframe)
- ✅ `mortality_analytics.py` - Added projection methods and UN IGME support
- ✅ `requirements.txt` - Check if scipy/sklearn are needed (optional dependencies)

### 2. **Data Files (New/Optimized)**
- ✅ `UN IGME 2024.csv` - **NEW** Optimized file (2.9 MB, ready for GitHub)
- ⚠️ `UN IGME 2024_backup.csv` - **DO NOT UPLOAD** (180 MB, too large)
- ✅ `Child Mortality.csv` - Already optimized (6.62 MB)

### 3. **Documentation Files (New)**
- ✅ `UN_IGME_OPTIMIZATION_AND_PROJECTIONS.md` - **NEW** Documentation for projections
- ✅ `BOTPRESS_INTEGRATION_SUMMARY.md` - Botpress integration details

---

## 📁 Files to Commit (Recommended)

### **Priority 1: Essential Files**
```
website.py
mortality_analytics.py
UN IGME 2024.csv
requirements.txt
```

### **Priority 2: Documentation**
```
UN_IGME_OPTIMIZATION_AND_PROJECTIONS.md
BOTPRESS_INTEGRATION_SUMMARY.md
FILES_TO_UPDATE_GITHUB.md (this file)
```

### **Priority 3: Supporting Files (if changed)**
```
mortality_charts.py (if updated for projections)
translations.py (if new translations added)
```

---

## 🚫 Files to EXCLUDE from GitHub

### **Large Backup Files**
- ❌ `UN IGME 2024_backup.csv` (180 MB - too large)
- ❌ `Child Mortality_backup.csv` (if exists, too large)

### **Temporary/Optimization Scripts**
- ❌ `optimize_un_igme.py` (already deleted, was temporary)

### **Cache/Python Files**
- ❌ `__pycache__/` directories
- ❌ `*.pyc` files
- ❌ `.DS_Store` files (Mac)

---

## 📝 Git Commands (If Using Git)

### **Check Status**
```bash
git status
```

### **Add Modified Files**
```bash
# Core files
git add website.py
git add mortality_analytics.py
git add "UN IGME 2024.csv"
git add requirements.txt

# Documentation
git add UN_IGME_OPTIMIZATION_AND_PROJECTIONS.md
git add BOTPRESS_INTEGRATION_SUMMARY.md
git add FILES_TO_UPDATE_GITHUB.md
```

### **Commit**
```bash
git commit -m "Update: Botpress chatbot scripts + UN IGME 2024 optimization + SDG 2030 projections"
```

### **Push**
```bash
git push origin main
```

---

## 🔍 Key Changes Summary

### **1. Botpress Chatbot**
- **Changed from**: iframe embed
- **Changed to**: Script-based integration
- **Scripts**:
  - `https://cdn.botpress.cloud/webchat/v3.4/inject.js`
  - `https://files.bpcontent.cloud/2025/11/09/06/20251109063717-8SHN5C4I.js`

### **2. UN IGME 2024 Data**
- **Optimized**: 180 MB → 2.9 MB (98.4% reduction)
- **Filtered**: AFRO countries only
- **Indicators**: SDG-relevant only
- **Years**: 2000-2030

### **3. SDG 2030 Projections**
- **New Tab**: "🎯 SDG 2030 Projections"
- **Methods**: Linear, Exponential, Log-Linear (AARR)
- **Features**: Gap analysis, required AARR, on-track status

---

## ✅ Verification Checklist

Before pushing to GitHub:

- [ ] `website.py` compiles without errors
- [ ] `mortality_analytics.py` compiles without errors
- [ ] `UN IGME 2024.csv` is under 25MB (✅ 2.9 MB)
- [ ] Backup files are NOT included
- [ ] All new documentation files are included
- [ ] Botpress scripts are correctly updated
- [ ] No sensitive data in files
- [ ] `.gitignore` excludes large files and cache

---

## 📊 File Sizes (For Reference)

| File | Size | Status |
|------|------|--------|
| `UN IGME 2024.csv` | 2.9 MB | ✅ Ready |
| `UN IGME 2024_backup.csv` | 180 MB | ❌ Exclude |
| `Child Mortality.csv` | 6.62 MB | ✅ Ready |
| `website.py` | ~500 KB | ✅ Ready |
| `mortality_analytics.py` | ~50 KB | ✅ Ready |

---

## 🎯 Quick Update Command

If you want to update just the essential files:

```bash
git add website.py mortality_analytics.py "UN IGME 2024.csv" requirements.txt
git add UN_IGME_OPTIMIZATION_AND_PROJECTIONS.md BOTPRESS_INTEGRATION_SUMMARY.md
git commit -m "Update: Botpress scripts + UN IGME optimization + SDG projections"
git push
```

---

**Last Updated**: After Botpress script update
**Status**: ✅ Ready for GitHub

