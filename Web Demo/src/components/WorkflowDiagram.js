import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { motion } from 'framer-motion';
import './WorkflowDiagram.css';

// Initialize Mermaid
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  securityLevel: 'loose',
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'step',
    rankSpacing: 80,
    nodeSpacing: 60,
    padding: 25,
    diagramPadding: 20,
    nodeAlignment: 'center'
  }
});

const WorkflowDiagram = ({ currentStep, scenario, isPlaying, onStepComplete }) => {
  const diagramRef = useRef(null);
  const [diagramSvg, setDiagramSvg] = useState('');
  const [currentNode, setCurrentNode] = useState(null);

  // Mermaid diagram definition - Simplified horizontal flow with corner connections
  const mermaidDiagram = `
    graph LR
        %% Simplified flow with explicit positioning for corner connections
        A[START] --> B[Fetch Email]
        B --> C[Validate data]
        C --> D{Validation Success?}
        
        %% Decision paths with corner connections
        D -->|No| E[Validation Failed]
        D -->|Yes| F[Supabase Entry]
        
        %% Second decision point with corner connections
        F --> G{Entry Success?}
        G -->|No| E
        G -->|Yes| H[Next Action]
        
        %% End points
        E --> I[END]
        H --> I
        
        %% Styling for professional appearance
        style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#0d47a1
        style I fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
        style E fill:#ffebee,stroke:#d32f2f,stroke-width:2px,color:#b71c1c
        
        %% Decision boxes styling - Professional diamond appearance
        style D fill:#fff8e1,stroke:#fbc02d,stroke-width:2px,color:#f57f17
        style G fill:#fff8e1,stroke:#fbc02d,stroke-width:2px,color:#f57f17
        
        %% Process boxes styling - Clean rectangular appearance
        style B fill:#f1f8e9,stroke:#689f38,stroke-width:1px,color:#33691e
        style C fill:#f1f8e9,stroke:#689f38,stroke-width:1px,color:#33691e
        style F fill:#f1f8e9,stroke:#689f38,stroke-width:1px,color:#33691e
        style H fill:#f1f8e9,stroke:#689f38,stroke-width:1px,color:#33691e
        
        %% Link styling for professional appearance
        linkStyle default stroke:#666,stroke-width:2px,fill:none
  `;

  useEffect(() => {
    const renderDiagram = async () => {
      try {
        const { svg } = await mermaid.render('workflow-diagram', mermaidDiagram);
        setDiagramSvg(svg);
      } catch (error) {
        console.error('Error rendering diagram:', error);
      }
    };

    renderDiagram();
  }, []);

  useEffect(() => {
    if (currentStep && diagramSvg) {
      highlightCurrentNode(currentStep);
    }
  }, [currentStep, diagramSvg]);

  const highlightCurrentNode = (step) => {
    if (!diagramRef.current) return;

    // Remove previous highlights
    const allNodes = diagramRef.current.querySelectorAll('.node');
    allNodes.forEach(node => {
      node.classList.remove('active', 'success', 'failure', 'needs-revision');
    });

    // Add highlight to current node
    const currentNodeElement = diagramRef.current.querySelector(`[id*="${step.node}"]`);
    if (currentNodeElement) {
      const nodeElement = currentNodeElement.closest('.node') || currentNodeElement;
      nodeElement.classList.add('active');
      
      // Add status-specific styling
      if (step.status === 'success') {
        nodeElement.classList.add('success');
      } else if (step.status === 'failure') {
        nodeElement.classList.add('failure');
      } else if (step.status === 'needs_revision') {
        nodeElement.classList.add('needs-revision');
      }
    }

    setCurrentNode(step);
  };

  const getStepDescription = (step) => {
    if (!step) return '';
    
    const descriptions = {
      START: 'Starting the workflow...',
      'Fetch Email': 'Fetching latest fitness email from Gmail...',
      'Validate data': 'Validating fitness data against historical trends...',
      'Validation Success?': 'Checking if validation was successful...',
      'Validation Failed': 'Validation failed - workflow terminated',
      'Supabase Entry': 'Entering data into Supabase...',
      'Entry Success?': 'Checking if Supabase entry was successful...',
      'Next Action': 'Proceeding to next action...',
      END: 'Workflow completed successfully!'
    };

    return descriptions[step.node] || `Processing ${step.node}...`;
  };

  return (
    <div className="workflow-diagram-container">
      <div className="diagram-header">
        <h2>LangGraph Workflow Flow Diagram</h2>
        {currentNode && (
          <div className="current-step-info">
            <div className="step-name">{currentNode.node.replace(/_/g, ' ').toUpperCase()}</div>
            <div className="step-description">{getStepDescription(currentNode)}</div>
            <div className={`step-status ${currentNode.status}`}>
              Status: {currentNode.status.replace('_', ' ').toUpperCase()}
            </div>
          </div>
        )}
      </div>

      <div className="diagram-wrapper">
        <div 
          ref={diagramRef}
          className="mermaid-diagram"
          dangerouslySetInnerHTML={{ __html: diagramSvg }}
        />
        
        {isPlaying && (
          <div className="playback-overlay">
            <div className="playback-indicator">
              <div className="pulse-dot"></div>
              <span>Playing Scenario: {scenario?.name}</span>
            </div>
          </div>
        )}
      </div>

      {currentNode && (
        <motion.div 
          className="step-details"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h3>Current Step Details</h3>
          <div className="step-grid">
            <div className="step-item">
              <strong>Node:</strong> {currentNode.node}
            </div>
            <div className="step-item">
              <strong>Status:</strong> 
              <span className={`status-badge ${currentNode.status}`}>
                {currentNode.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <div className="step-item">
              <strong>Duration:</strong> {currentNode.duration}ms
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default WorkflowDiagram;
