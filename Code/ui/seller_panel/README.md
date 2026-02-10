# DealSense AI - Sales Intelligence Platform

Enterprise-grade web application UI for sales teams to prepare, assist, and summarize sales calls using insights from Top 5 past business deals.

## 🎯 Application Purpose

The DealSense AI platform supports sales teams across three critical phases:

- **Before Call**: Prepare with data upload and insights from successful deals
- **During Call**: Real-time deal reference and note-taking assistance
- **After Call**: Finalize outcomes and generate comprehensive reports

## 🏗️ Project Structure

```
src/
├── components/
│   ├── Header/                 # Application header with branding
│   ├── Navigation/
│   │   └── TabNavigation      # 3-tab navigation (Before/During/After)
│   ├── BeforeCall/            # Pre-sales preparation components
│   │   ├── FileUpload
│   │   ├── SharePointLinkInput
│   │   └── PreCallSummary
│   ├── DuringCall/            # Live call assistance components
│   │   ├── DealSelector
│   │   ├── DealDetailsPanel
│   │   └── LiveNotes
│   └── AfterCall/             # Post-call summary components
│       └── AfterCall
├── data/
│   └── mockData.js            # Static Top 5 deals + templates
├── styles/
│   └── globals.css            # Global CSS variables & theme
├── App.jsx                    # Main app orchestrator
├── main.jsx                   # React entry point
└── index.html                 # HTML root

server.js                      # Express server (serves React build)
package.json                   # Dependencies and scripts
vite.config.js                # Vite build configuration
```

## 🎨 Design & Theme

- **Color Palette**: Banking Blue, Professional Gray, Clean White
- **Typography**: Clear, readable, enterprise-grade
- **Components**: Cards, Tabs, Modals with subtle shadows
- **Responsive**: Desktop-first, mobile-optimized
- **Accessibility**: High contrast, proper semantic HTML

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation

```bash
npm install
```

### Development

```bash
npm run build
npm run dev
```

Visit `http://localhost:3000` in your browser.

The development server will serve the React app with hot reload capabilities.

### Production Build

```bash
npm run build
npm run start
```

## 📋 Features Implemented

### Before Call Tab
- ✅ File upload (single file and directory)
- ✅ SharePoint link integration input
- ✅ Top 5 deals display with summary cards
- ✅ Deal details expandable sections
- ✅ PDF download simulation
- ✅ Deal benchmarking information

### During Call Tab
- ✅ Deal selector dropdown
- ✅ Comprehensive deal details panel
- ✅ Key highlights and deal breakers reference
- ✅ Live call notes textarea
- ✅ Auto-save indicator
- ✅ Real-time word count

### After Call Tab
- ✅ Editable post-call summary form
- ✅ Call outcome tracking (Won/Lost/Follow-up)
- ✅ Final highlights and risks input
- ✅ Next steps documentation
- ✅ Generate final report button
- ✅ PDF download simulation
- ✅ Outcome status indicator

## 📊 Mock Data

The application includes 5 realistic enterprise deals:

1. **Global Banking Platform Migration** - $2.4M, 18 months
2. **Insurance Claims Processing Automation** - $1.8M, 14 months
3. **Customer Data Platform Implementation** - $2.1M, 16 months
4. **Supply Chain Visibility Network** - $2.8M, 20 months
5. **Healthcare Patient Management System** - $3.2M, 22 months

Each deal includes:
- Case study overview
- Key highlights and metrics
- Deal breakers and risks
- Success criteria
- Timeline and team composition

## 🔧 Technology Stack

- **Frontend**: React 18 (Functional Components)
- **Styling**: CSS Modules with global theme variables
- **Build Tool**: Vite (for fast development and optimized builds)
- **Server**: Node.js + Express (simple static file serving)
- **No Backend Logic**: All features use mock data and UI simulation

## 📱 Responsive Design

- **Desktop**: Full layout with side-by-side panels
- **Tablet**: Optimized grid layouts
- **Mobile**: Single-column layout with touch-friendly controls

## 🎓 Code Organization

- **Functional Components Only**: Modern React patterns
- **CSS Modules**: Scoped styling to prevent conflicts
- **Global Theme**: CSS variables for consistent design system
- **Inline Comments**: Every component includes flow documentation
- **Mock Data**: Realistic enterprise sales data for testing

## ⚠️ Important Notes

- **No Authentication**: Mock implementation only
- **No Backend Logic**: All operations are UI/client-side
- **No AI/ML**: Insights are from static mock data
- **No Database**: No persistent storage
- **UI Simulation Only**: File uploads, PDF downloads, SharePoint links are mocked

## 🔄 Workflow

1. **Prepare** (Before Call)
   - Upload customer data or SharePoint links
   - Review insights from successful past deals
   - Download pre-call summary

2. **Execute** (During Call)
   - Select relevant deal reference
   - Review case studies and highlights
   - Take real-time notes
   - Reference deal breakers and success criteria

3. **Finalize** (After Call)
   - Document final highlights and outcomes
   - Record risks and next steps
   - Generate comprehensive report
   - Download summary for records

## 📝 License

MIT © 2026 DealSense AI

---

**Built for Enterprise Sales Excellence** 🎯
