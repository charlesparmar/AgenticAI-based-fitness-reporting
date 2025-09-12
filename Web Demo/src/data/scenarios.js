// Scenario definitions for the interactive workflow demo
export const scenarios = {
  happyPath: {
    id: 'happyPath',
    name: 'Scenario 1: Happy Path',
    description: 'All steps complete successfully on first attempt',
    color: '#4CAF50',
    steps: [
      { node: 'model_config_validation', duration: 1000, status: 'success' },
      { node: 'fetch_email', duration: 1500, status: 'success' },
      { node: 'fetch_database', duration: 800, status: 'success' },
      { node: 'reconcile_data', duration: 1200, status: 'success' },
      { node: 'validate_data', duration: 1000, status: 'success' },
      { node: 'supabase_entry', duration: 1500, status: 'success' },
      { node: 'report_drafter', duration: 2000, status: 'success' },
      { node: 'email_evaluation', duration: 1000, status: 'success' },
      { node: 'send_final_email', duration: 1500, status: 'success' },
      { node: 'cleanup', duration: 800, status: 'success' }
    ],
    feedbackLoops: 0,
    finalStatus: 'success'
  },

  feedbackLoopTwice: {
    id: 'feedbackLoopTwice',
    name: 'Scenario 2: Feedback Loop (2 iterations)',
    description: 'Email needs 2 iterations to be approved',
    color: '#FF9800',
    steps: [
      { node: 'model_config_validation', duration: 1000, status: 'success' },
      { node: 'fetch_email', duration: 1500, status: 'success' },
      { node: 'fetch_database', duration: 800, status: 'success' },
      { node: 'reconcile_data', duration: 1200, status: 'success' },
      { node: 'validate_data', duration: 1000, status: 'success' },
      { node: 'supabase_entry', duration: 1500, status: 'success' },
      { node: 'report_drafter', duration: 2000, status: 'success' },
      { node: 'email_evaluation', duration: 1000, status: 'needs_revision' },
      { node: 'feedback_loop', duration: 500, status: 'success' },
      { node: 'report_drafter', duration: 2000, status: 'success' },
      { node: 'email_evaluation', duration: 1000, status: 'needs_revision' },
      { node: 'feedback_loop', duration: 500, status: 'success' },
      { node: 'report_drafter', duration: 2000, status: 'success' },
      { node: 'email_evaluation', duration: 1000, status: 'success' },
      { node: 'send_final_email', duration: 1500, status: 'success' },
      { node: 'cleanup', duration: 800, status: 'success' }
    ],
    feedbackLoops: 2,
    finalStatus: 'success'
  },

  feedbackLoopThree: {
    id: 'feedbackLoopThree',
    name: 'Scenario 3: Feedback Loop (3 iterations)',
    description: 'Email needs all 3 iterations, then forced approval',
    color: '#E91E63',
    steps: [
      { node: 'model_config_validation', duration: 1000, status: 'success' },
      { node: 'fetch_email', duration: 1500, status: 'success' },
      { node: 'fetch_database', duration: 800, status: 'success' },
      { node: 'reconcile_data', duration: 1200, status: 'success' },
      { node: 'validate_data', duration: 1000, status: 'success' },
      { node: 'supabase_entry', duration: 1500, status: 'success' },
      { node: 'report_drafter', duration: 2000, status: 'success' },
      { node: 'email_evaluation', duration: 1000, status: 'needs_revision' },
      { node: 'feedback_loop', duration: 500, status: 'success' },
      { node: 'report_drafter', duration: 2000, status: 'success' },
      { node: 'email_evaluation', duration: 1000, status: 'needs_revision' },
      { node: 'feedback_loop', duration: 500, status: 'success' },
      { node: 'report_drafter', duration: 2000, status: 'success' },
      { node: 'email_evaluation', duration: 1000, status: 'needs_revision' },
      { node: 'feedback_loop', duration: 500, status: 'success' },
      { node: 'report_drafter', duration: 2000, status: 'success' },
      { node: 'email_evaluation', duration: 1000, status: 'forced_approval' },
      { node: 'send_final_email', duration: 1500, status: 'success' },
      { node: 'cleanup', duration: 800, status: 'success' }
    ],
    feedbackLoops: 3,
    finalStatus: 'success'
  },

  validationFailure: {
    id: 'validationFailure',
    name: 'Scenario 4: Validation Failure',
    description: 'Data validation fails, workflow terminates early',
    color: '#F44336',
    steps: [
      { node: 'model_config_validation', duration: 1000, status: 'success' },
      { node: 'fetch_email', duration: 1500, status: 'success' },
      { node: 'fetch_database', duration: 800, status: 'success' },
      { node: 'reconcile_data', duration: 1200, status: 'success' },
      { node: 'validate_data', duration: 1000, status: 'failure' },
      { node: 'end_workflow', duration: 500, status: 'failure' }
    ],
    feedbackLoops: 0,
    finalStatus: 'failure'
  },

  reconFailure: {
    id: 'reconFailure',
    name: 'Scenario 5: Reconciliation Failure',
    description: 'Data reconciliation fails, workflow terminates early',
    color: '#9C27B0',
    steps: [
      { node: 'model_config_validation', duration: 1000, status: 'success' },
      { node: 'fetch_email', duration: 1500, status: 'success' },
      { node: 'fetch_database', duration: 800, status: 'success' },
      { node: 'reconcile_data', duration: 1200, status: 'failure' },
      { node: 'end_workflow', duration: 500, status: 'failure' }
    ],
    feedbackLoops: 0,
    finalStatus: 'failure'
  }
};

// Node definitions for the Mermaid diagram
export const nodes = {
  model_config_validation: { id: 'A', label: 'START: model_config_validation', style: 'fill:#e1f5fe' },
  fetch_email: { id: 'B', label: 'fetch_email', style: 'fill:#e1f5fe' },
  fetch_database: { id: 'C', label: 'fetch_database', style: 'fill:#e1f5fe' },
  reconcile_data: { id: 'D', label: 'reconcile_data', style: 'fill:#e1f5fe' },
  validate_data: { id: 'E', label: 'validate_data', style: 'fill:#e1f5fe' },
  supabase_entry: { id: 'G', label: 'supabase_entry', style: 'fill:#e1f5fe' },
  report_drafter: { id: 'I', label: 'report_drafter', style: 'fill:#e1f5fe' },
  email_evaluation: { id: 'J', label: 'email_evaluation', style: 'fill:#e1f5fe' },
  feedback_decision: { id: 'K', label: 'feedback_decision', style: 'fill:#e1f5fe' },
  feedback_loop: { id: 'O', label: 'feedback_loop', style: 'fill:#e1f5fe' },
  send_final_email: { id: 'M', label: 'send_final_email', style: 'fill:#fff3e0' },
  cleanup: { id: 'P', label: 'cleanup', style: 'fill:#f3e5f5' },
  end_workflow: { id: 'Q', label: 'END: Workflow Complete', style: 'fill:#c8e6c9' },
  end_validation_failed: { id: 'Z', label: 'END: Validation Failed', style: 'fill:#ffcdd2' }
};

// Status colors for different states
export const statusColors = {
  pending: '#9E9E9E',
  active: '#2196F3',
  success: '#4CAF50',
  failure: '#F44336',
  needs_revision: '#FF9800',
  forced_approval: '#E91E63'
};
