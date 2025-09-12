'use client';

import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { motion } from 'framer-motion';

// Initialize Mermaid with proper settings for corner connections
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  securityLevel: 'loose',
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'step',
    rankSpacing: 100,
    nodeSpacing: 80,
    padding: 30,
    diagramPadding: 25,
    nodeAlignment: 'center'
  }
});

interface WorkflowDiagramProps {
  currentStep?: string;
  isPlaying?: boolean;
}

const WorkflowDiagram: React.FC<WorkflowDiagramProps> = ({ 
  currentStep, 
  isPlaying = false 
}) => {
  const diagramRef = useRef<HTMLDivElement>(null);
  const [diagramSvg, setDiagramSvg] = useState<string>('');
  const [currentNode, setCurrentNode] = useState<string | null>(null);

  // Actual LangGraph workflow from LangGraph_Workflow_Flow.md with proper corner connections
  const mermaidDiagram = `
    graph LR
        %% Actual LangGraph workflow with proper corner connections
        A([START: model_config_validation]) --> B[fetch_email]
        B --> C[fetch_database]
        C --> D[reconcile_data]
        D --> E[validate_data]
        
        %% First decision point - Validation Success with corner connections
        E --> F{Validation Success?}
        F -->|No| Z([END: Validation Failed])
        F -->|Yes| G[supabase_entry]
        
        %% Second decision point - Supabase Success with corner connections
        G --> H{Supabase Success?}
        H -->|No| Z
        H -->|Yes| I[report_drafter]
        
        %% Email processing flow
        I --> J[email_evaluation]
        J --> K[feedback_decision]
        
        %% Third decision point - Email Approved
        K --> L{Email Approved?}
        L -->|Yes| M[send_final_email]
        L -->|No| N{Max Iterations?}
        
        %% Fourth decision point - Max Iterations
        N -->|No| O[feedback_loop]
        N -->|Yes| M
        
        %% Feedback loop back to report drafter
        O --> I
        
        %% Final flow
        M --> P[cleanup]
        P --> Q([END: Workflow Complete])
        
        %% Styling for professional appearance
        style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#0d47a1
        style Q fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
        style Z fill:#ffebee,stroke:#d32f2f,stroke-width:2px,color:#b71c1c
        style M fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
        style P fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
        
        %% Decision boxes styling - Professional diamond appearance
        style F fill:#fff8e1,stroke:#fbc02d,stroke-width:2px,color:#f57f17
        style H fill:#fff8e1,stroke:#fbc02d,stroke-width:2px,color:#f57f17
        style L fill:#fff8e1,stroke:#fbc02d,stroke-width:2px,color:#f57f17
        style N fill:#fff8e1,stroke:#fbc02d,stroke-width:2px,color:#f57f17
        
        %% Process boxes styling - Clean rectangular appearance
        style B fill:#f1f8e9,stroke:#689f38,stroke-width:1px,color:#33691e
        style C fill:#f1f8e9,stroke:#689f38,stroke-width:1px,color:#33691e
        style D fill:#f1f8e9,stroke:#689f38,stroke-width:1px,color:#33691e
        style E fill:#f1f8e9,stroke:#689f38,stroke-width:1px,color:#33691e
        style G fill:#f1f8e9,stroke:#689f38,stroke-width:1px,color:#33691e
        style I fill:#f1f8e9,stroke:#689f38,stroke-width:1px,color:#33691e
        style J fill:#f1f8e9,stroke:#689f38,stroke-width:1px,color:#33691e
        style K fill:#f1f8e9,stroke:#689f38,stroke-width:1px,color:#33691e
        style O fill:#f1f8e9,stroke:#689f38,stroke-width:1px,color:#33691e
        
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

  const highlightCurrentNode = (step: string) => {
    if (!diagramRef.current) return;

    // Remove previous highlights
    const allNodes = diagramRef.current.querySelectorAll('.node');
    allNodes.forEach(node => {
      node.classList.remove('active', 'success', 'failure', 'needs-revision');
    });

    // Add highlight to current node
    const currentNodeElement = diagramRef.current.querySelector(`[id*="${step}"]`);
    if (currentNodeElement) {
      const nodeElement = currentNodeElement.closest('.node') || currentNodeElement;
      nodeElement.classList.add('active');
    }

    setCurrentNode(step);
  };

  const getStepDescription = (step: string) => {
    const descriptions: Record<string, string> = {
      'model_config_validation': 'Validating LLM model configuration...',
      'fetch_email': 'Fetching latest fitness email from Gmail...',
      'fetch_database': 'Retrieving latest database entry...',
      'reconcile_data': 'Comparing email data with database...',
      'validate_data': 'Validating fitness data against historical trends...',
      'supabase_entry': 'Entering data into Supabase...',
      'report_drafter': 'Generating fitness report email...',
      'email_evaluation': 'Evaluating email quality...',
      'feedback_decision': 'Deciding on feedback loop...',
      'feedback_loop': 'Processing feedback for next iteration...',
      'send_final_email': 'Sending final approved email...',
      'cleanup': 'Cleaning up system resources...',
      'end_workflow': 'Workflow completed successfully!',
      'end_validation_failed': 'Workflow terminated due to validation failure'
    };

    return descriptions[step] || `Processing ${step}...`;
  };

  return (
    <div className="workflow-diagram-container bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
      <div className="diagram-header flex justify-between items-center mb-6 pb-4 border-b-2 border-gray-100">
        <h2 className="text-2xl font-semibold text-gray-800">
          LangGraph Workflow Flow Diagram
        </h2>
        {currentNode && (
          <div className="current-step-info text-right min-w-[300px]">
            <div className="step-name text-lg font-semibold text-blue-600 mb-1">
              {currentNode.replace(/_/g, ' ').toUpperCase()}
            </div>
            <div className="step-description text-sm text-gray-600 mb-2">
              {getStepDescription(currentNode)}
            </div>
          </div>
        )}
      </div>

      <div className="diagram-wrapper relative bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-8 min-h-[600px] flex justify-center items-center overflow-auto border border-gray-200 shadow-inner">
        <div 
          ref={diagramRef}
          className="mermaid-diagram w-full max-w-none h-auto min-w-[1200px] filter drop-shadow-lg transform scale-100 origin-center"
          dangerouslySetInnerHTML={{ __html: diagramSvg }}
        />
        
        {isPlaying && (
          <div className="playback-overlay absolute inset-0 bg-white/90 flex justify-center items-center z-10">
            <div className="playback-indicator flex items-center gap-3 bg-blue-50 px-6 py-4 rounded-lg border-2 border-blue-300">
              <div className="pulse-dot w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
              <span className="text-blue-700 font-medium">Playing Workflow Simulation</span>
            </div>
          </div>
        )}
      </div>

      {currentNode && (
        <motion.div 
          className="step-details mt-6 p-4 bg-gray-50 rounded-lg border-l-4 border-blue-500"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Current Step Details</h3>
          <div className="step-grid grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="step-item flex items-center gap-2 text-sm">
              <strong>Node:</strong> {currentNode}
            </div>
            <div className="step-item flex items-center gap-2 text-sm">
              <strong>Status:</strong> 
              <span className="status-badge px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-700">
                ACTIVE
              </span>
            </div>
            <div className="step-item flex items-center gap-2 text-sm">
              <strong>Description:</strong> {getStepDescription(currentNode)}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default WorkflowDiagram;
