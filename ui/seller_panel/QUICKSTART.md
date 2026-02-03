# 🚀 DealSense AI - Quick Start Guide

## ⚡ 5-Minute Setup (After Installing Node.js)

### Step 1: Open PowerShell/Terminal
```powershell
# Navigate to project folder
cd "c:\D\LUXOFT-DXC\2026\OFFICE\HACKTHON\workspace\dealsense-ai\ui\seller_panel\trial-1"
```

### Step 2: Install Dependencies
```powershell
npm install
```
**Wait time**: 2-3 minutes

### Step 3: Build React App
```powershell
npm run build
```
**Wait time**: 30-60 seconds

### Step 4: Start Server
```powershell
npm run dev
```

You should see:
```
========================================
DealSense AI - Sales Intelligence UI
========================================
Server running at http://localhost:3000
========================================
```

### Step 5: Open Browser
Visit: **http://localhost:3000**

---

## 🎯 What You'll See

### Tab 1: Before Call (Default)
- **File Upload**: Drag & drop area
- **SharePoint Link**: Link input field  
- **Top 5 Deals**: Card grid showing deals
  - Click "View Details" to expand
  - See case study, highlights, risks
- **Download Button**: Mock PDF download

### Tab 2: During Call
- **Left**: Deal selector + deal details
- **Right**: Live notes textarea
- Select different deals to see details change
- Type notes and save

### Tab 3: After Call
- **Form Fields**: Summary, risks, outcome
- **Dropdown**: Choose call outcome (Won/Lost/Follow-up)
- **Buttons**: Generate report, download summary
- **Status**: Shows colored outcome indicator

---

## 🎨 Features to Try

### Before Call
1. Click "Choose File" button
2. Click "View Details" on first deal card
3. Click "Download Summary" button

### During Call
1. Open dropdown and select different deals
2. Notice details panel updates
3. Type in notes textarea
4. Click "Save Notes"

### After Call
1. Fill in highlights field
2. Fill in risks field
3. Select outcome from dropdown
4. Watch indicator appear at bottom
5. Click "Generate Final Report"

---

## 🔧 Troubleshooting

### "npm is not recognized"
→ Install Node.js from nodejs.org
→ Restart PowerShell after installing

### "Port 3000 already in use"
→ Edit server.js, change `const PORT = 3000` to `3001`

### "Cannot find module"
→ Run `npm install` again

### Blank page in browser
→ Make sure you ran `npm run build` first

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **README.md** | Full project documentation |
| **SETUP.md** | Detailed installation guide |
| **UI_UX_OVERVIEW.md** | Visual flow & design details |
| **PROJECT_DELIVERY.md** | Complete feature breakdown |
| **PROJECT_INDEX.md** | File listing & checklist |
| **QUICKSTART.md** | This file (5-min setup) |

---

## 💡 How It Works

1. **Frontend**: React app in `/src/`
2. **Build**: Vite compiles to `/dist/`
3. **Server**: Express serves `/dist/` files
4. **Data**: Mock data in `/src/data/`
5. **Styles**: CSS Modules, no conflicts

---

## 🎁 What's Included

✅ 5 Realistic Enterprise Deals
✅ 15 React Components
✅ 15 CSS Modules
✅ Responsive Design
✅ Banking Color Theme
✅ Mock Data
✅ Full Documentation
✅ No Backend Logic Needed

---

## 📱 Responsive Design

- **Desktop** (1024px+): Full layout
- **Tablet** (768-1023px): Optimized
- **Mobile** (<768px): Stacked

Try resizing your browser!

---

## 🎯 Next Steps

1. Explore all 3 tabs
2. Try all interactive features
3. Read the documentation
4. Customize colors in `src/styles/globals.css`
5. Add your own data to mockData.js
6. Deploy to production

---

## 📞 Quick Reference

```bash
npm install     # Install dependencies
npm run build   # Build React app
npm run dev     # Start server
npm run start   # Same as dev
```

---

## ✅ All Set!

Your enterprise sales intelligence app is now running.

**Visit**: http://localhost:3000

Enjoy! 🎉
