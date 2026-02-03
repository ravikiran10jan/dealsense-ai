# DealSense AI - Installation & Setup Guide

## ⚠️ Prerequisites

Before running this project, you need to install **Node.js and npm**.

### Step 1: Install Node.js

1. **Download Node.js** from: https://nodejs.org/
   - Download **LTS (Long Term Support) version** (recommended)
   - Version 16+ or higher required

2. **Install Node.js**
   - Run the installer and follow the prompts
   - Accept default settings
   - npm will be installed automatically with Node.js

3. **Verify Installation**
   - Open PowerShell or Command Prompt
   - Run: `node --version` (should show v16+ or higher)
   - Run: `npm --version` (should show 7+ or higher)

## 📦 Installation Steps

### Step 2: Navigate to Project Directory

```powershell
cd "c:\D\LUXOFT-DXC\2026\OFFICE\HACKTHON\workspace\dealsense-ai\ui\seller_panel\trial-1"
```

### Step 3: Install Dependencies

```powershell
npm install
```

This will install:
- React 18
- React DOM 18
- Express.js (Node server)
- Vite (Build tool)
- All required dev dependencies

**Installation time**: 2-5 minutes depending on internet speed

## 🚀 Running the Application

### Development Mode

```powershell
npm run build
npm run dev
```

Then open your browser and navigate to: **http://localhost:3000**

The server will display:
```
========================================
DealSense AI - Sales Intelligence UI
========================================
Server running at http://localhost:3000
========================================
```

### Production Build

```powershell
npm run build
npm run start
```

## 🎯 What You'll See

When you open http://localhost:3000 in your browser:

1. **Header**: DealSense AI branding with navigation info
2. **Tab Navigation**: Three tabs - Before Call | During Call | After Call
3. **Content Area**: Active tab content (starts on Before Call)

### Before Call Tab
- File upload section (single file or directory)
- SharePoint link input
- Top 5 deals cards with expandable details
- PDF download button

### During Call Tab
- Deal selector dropdown (left panel)
- Deal details with highlights and risks (left panel)
- Live notes textarea (right panel)
- Save notes button

### After Call Tab
- Deal title selector
- Final highlights textarea
- Risks textarea
- Call outcome dropdown (Won/Lost/Follow-up)
- Generate report button
- Download summary button

## 🏗️ Project Structure Summary

```
trial-1/
├── src/
│   ├── components/
│   │   ├── Header/              # App header
│   │   ├── Navigation/          # Tab navigation
│   │   ├── BeforeCall/          # Pre-call components
│   │   ├── DuringCall/          # Live call components
│   │   └── AfterCall/           # Post-call components
│   ├── data/
│   │   └── mockData.js          # 5 realistic deals
│   ├── styles/
│   │   └── globals.css          # Design system & theme
│   ├── App.jsx                  # Main app component
│   └── main.jsx                 # React entry point
├── server.js                    # Express server
├── index.html                   # HTML template
├── vite.config.js              # Vite configuration
├── package.json                # Dependencies
└── README.md                   # Full documentation
```

## 🎨 Design Theme

- **Colors**: Banking Blue (#003366), Professional Gray, Clean White
- **Styling**: CSS Modules (scoped, no conflicts)
- **Layout**: Responsive (desktop-first, mobile-friendly)
- **Components**: Cards, tabs, modals with subtle shadows

## 📊 Mock Data Included

5 enterprise sales deals with realistic data:
1. Global Banking Platform Migration - $2.4M
2. Insurance Claims Processing Automation - $1.8M
3. Customer Data Platform Implementation - $2.1M
4. Supply Chain Visibility Network - $2.8M
5. Healthcare Patient Management System - $3.2M

## ⚙️ Troubleshooting

### "npm: The term 'npm' is not recognized"
- **Solution**: Install Node.js from nodejs.org
- After installation, restart PowerShell/Command Prompt

### "Cannot find module 'react'"
- **Solution**: Run `npm install` in the project directory
- Wait for installation to complete

### "Port 3000 already in use"
- **Solution**: Either:
  - Kill the process using port 3000
  - Change PORT in server.js to another port (3001, 3002, etc.)

### Browser shows "Cannot GET /"
- **Solution**: 
  - Make sure you ran `npm run build` first
  - Check that server is running (look for success message in terminal)
  - Try refreshing the page

## 🔧 Available Commands

```bash
npm install      # Install all dependencies
npm run build    # Build React app with Vite
npm run dev      # Start Express server (after build)
npm run start    # Same as dev
npm run preview  # Preview production build
```

## 📝 Important Notes

- **No Backend Logic**: All features are client-side and use mock data
- **No Authentication**: This is a UI-only demo
- **No Database**: Data is not persisted
- **File Operations**: Upload/download are simulated
- **SharePoint**: Link input is accepted but not processed

## 🎯 Next Steps After Installation

1. Explore all three tabs
2. Try clicking "View Details" on deals in Before Call tab
3. Select different deals in During Call dropdown
4. Take notes in the Live Notes textarea
5. Fill out and submit the After Call summary
6. Try all the mock download/generate buttons

## 📞 Support

For issues or questions about the setup:
1. Check this guide again
2. Verify Node.js is installed correctly
3. Ensure you're in the correct project directory
4. Check that all files were created (see README.md for file list)

---

**Happy Selling! 🎯**
