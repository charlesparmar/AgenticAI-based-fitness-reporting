# 🤖 LangGraph Workflow Demo

An interactive web application that demonstrates the LangGraph workflow for the Fitness Reporting System with animated flow progression and scenario testing.

## 🚀 Features

### **Interactive Workflow Visualization**
- **Real-time Mermaid.js diagrams** with animated node highlighting
- **Step-by-step progression** through the workflow
- **Visual feedback** for different node states (success, failure, needs revision)
- **Animated arrows** showing flow direction

### **5 Predefined Scenarios**
1. **Happy Path** - All steps complete successfully on first attempt
2. **Feedback Loop (2 iterations)** - Email needs 2 iterations to be approved
3. **Feedback Loop (3 iterations)** - Email needs all 3 iterations, then forced approval
4. **Validation Failure** - Data validation fails, workflow terminates early
5. **Reconciliation Failure** - Data reconciliation fails, workflow terminates early

### **Interactive Controls**
- **Scenario Selection** - Choose from 5 different workflow scenarios
- **Play/Pause Controls** - Control the animation playback
- **Progress Tracking** - Real-time progress bar and step counter
- **Reset Functionality** - Reset to initial state

### **Professional UI/UX**
- **Modern Design** - Clean, professional interface with gradient backgrounds
- **Responsive Layout** - Works on desktop, tablet, and mobile devices
- **Smooth Animations** - Framer Motion powered transitions
- **Accessibility** - Keyboard navigation and screen reader support

## 🛠 Technology Stack

- **React 18** - Modern React with hooks and functional components
- **Mermaid.js** - Dynamic flowchart rendering and manipulation
- **Framer Motion** - Smooth animations and transitions
- **CSS3** - Modern styling with gradients and animations
- **JavaScript ES6+** - Modern JavaScript features

## 📦 Installation

1. **Navigate to the Web Demo directory:**
   ```bash
   cd "Web Demo"
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

## 🎯 Usage

### **Selecting a Scenario**
1. Choose from one of the 5 scenario buttons
2. Each scenario shows:
   - Number of feedback loops
   - Total steps
   - Expected outcome (success/failure)

### **Playing the Animation**
1. Click the **"Play"** button to start the animation
2. Watch as nodes highlight and progress through the workflow
3. Use **"Pause"** to stop at any point
4. Use **"Reset"** to return to the beginning

### **Understanding the Flow**
- **Blue nodes** - Active/current step
- **Green glow** - Successful completion
- **Red glow** - Failure/error
- **Orange glow** - Needs revision
- **Animated arrows** - Flow direction

## 📊 Scenario Details

### **Scenario 1: Happy Path**
- **Steps**: 10
- **Feedback Loops**: 0
- **Outcome**: Success
- **Description**: All steps complete successfully on first attempt

### **Scenario 2: Feedback Loop (2 iterations)**
- **Steps**: 16
- **Feedback Loops**: 2
- **Outcome**: Success
- **Description**: Email needs 2 iterations to be approved

### **Scenario 3: Feedback Loop (3 iterations)**
- **Steps**: 19
- **Feedback Loops**: 3
- **Outcome**: Success (forced approval)
- **Description**: Email needs all 3 iterations, then forced approval

### **Scenario 4: Validation Failure**
- **Steps**: 6
- **Feedback Loops**: 0
- **Outcome**: Failure
- **Description**: Data validation fails, workflow terminates early

### **Scenario 5: Reconciliation Failure**
- **Steps**: 5
- **Feedback Loops**: 0
- **Outcome**: Failure
- **Description**: Data reconciliation fails, workflow terminates early

## 🎨 Customization

### **Adding New Scenarios**
Edit `src/data/scenarios.js` to add new workflow scenarios:

```javascript
newScenario: {
  id: 'newScenario',
  name: 'New Scenario Name',
  description: 'Description of the scenario',
  color: '#HEXCODE',
  steps: [
    { node: 'node_name', duration: 1000, status: 'success' },
    // ... more steps
  ],
  feedbackLoops: 0,
  finalStatus: 'success'
}
```

### **Modifying Animation Speed**
Change the interval in `src/App.js`:

```javascript
const interval = setInterval(() => {
  // ... step logic
}, 2000); // Change this value (in milliseconds)
```

### **Customizing Styles**
- **Colors**: Edit CSS variables in component files
- **Animations**: Modify Framer Motion configurations
- **Layout**: Adjust CSS Grid and Flexbox properties

## 🔧 Development

### **Project Structure**
```
Web Demo/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── WorkflowDiagram.js
│   │   ├── WorkflowDiagram.css
│   │   ├── ScenarioControls.js
│   │   └── ScenarioControls.css
│   ├── data/
│   │   └── scenarios.js
│   ├── styles/
│   │   └── index.css
│   ├── App.js
│   ├── App.css
│   └── index.js
├── package.json
└── README.md
```

### **Key Components**

#### **WorkflowDiagram.js**
- Renders the Mermaid.js flowchart
- Handles node highlighting and animations
- Manages step progression and status display

#### **ScenarioControls.js**
- Provides scenario selection interface
- Controls playback (play/pause/reset)
- Shows progress and statistics

#### **scenarios.js**
- Defines all workflow scenarios
- Contains step-by-step configurations
- Manages scenario metadata

## 🚀 Deployment

### **Build for Production**
```bash
npm run build
```

### **Deploy to GitHub Pages**
1. Add to `package.json`:
   ```json
   "homepage": "https://yourusername.github.io/repository-name",
   "scripts": {
     "predeploy": "npm run build",
     "deploy": "gh-pages -d build"
   }
   ```

2. Install gh-pages:
   ```bash
   npm install --save-dev gh-pages
   ```

3. Deploy:
   ```bash
   npm run deploy
   ```

## 🐛 Troubleshooting

### **Common Issues**

#### **Mermaid Diagram Not Rendering**
- Check browser console for errors
- Ensure all dependencies are installed
- Verify Mermaid.js initialization

#### **Animations Not Working**
- Check Framer Motion installation
- Verify React version compatibility
- Clear browser cache

#### **Responsive Issues**
- Test on different screen sizes
- Check CSS media queries
- Verify viewport meta tag

## 📝 License

This project is part of the AgenticAI-based Fitness Reporting System.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review the code comments
- Create an issue in the repository

---

**🎉 Enjoy exploring the LangGraph workflow with this interactive demo!**
