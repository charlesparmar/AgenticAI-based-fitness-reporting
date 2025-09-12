import React from 'react';
import { motion } from 'framer-motion';
import { scenarios } from '../data/scenarios';
import './ScenarioControls.css';

const ScenarioControls = ({ 
  selectedScenario, 
  onScenarioSelect, 
  isPlaying, 
  onPlay, 
  onPause, 
  onReset,
  currentStepIndex,
  totalSteps
}) => {
  const getScenarioButtonStyle = (scenarioId) => {
    const baseStyle = {
      border: '2px solid transparent',
      transition: 'all 0.3s ease'
    };

    if (selectedScenario?.id === scenarioId) {
      return {
        ...baseStyle,
        borderColor: scenarios[scenarioId].color,
        backgroundColor: `${scenarios[scenarioId].color}15`,
        transform: 'scale(1.02)'
      };
    }

    return baseStyle;
  };

  const getProgressPercentage = () => {
    if (!selectedScenario || totalSteps === 0) return 0;
    return (currentStepIndex / totalSteps) * 100;
  };

  return (
    <div className="scenario-controls">
      <div className="controls-header">
        <h2>Interactive Workflow Scenarios</h2>
        <p>Select a scenario to see the workflow in action with animated flow progression</p>
      </div>

      <div className="scenarios-grid">
        {Object.values(scenarios).map((scenario) => (
          <motion.button
            key={scenario.id}
            className="scenario-button"
            style={getScenarioButtonStyle(scenario.id)}
            onClick={() => onScenarioSelect(scenario)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={isPlaying}
          >
            <div className="scenario-icon">
              {scenario.finalStatus === 'success' ? '✅' : '❌'}
            </div>
            <div className="scenario-content">
              <h3>{scenario.name}</h3>
              <p>{scenario.description}</p>
              <div className="scenario-meta">
                <span className="feedback-loops">
                  🔄 {scenario.feedbackLoops} feedback loop{scenario.feedbackLoops !== 1 ? 's' : ''}
                </span>
                <span className="total-steps">
                  📊 {scenario.steps.length} steps
                </span>
              </div>
            </div>
          </motion.button>
        ))}
      </div>

      {selectedScenario && (
        <motion.div 
          className="playback-controls"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="selected-scenario-info">
            <h3>Selected: {selectedScenario.name}</h3>
            <p>{selectedScenario.description}</p>
          </div>

          <div className="control-buttons">
            <motion.button
              className="control-btn play-btn"
              onClick={isPlaying ? onPause : onPlay}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              disabled={!selectedScenario}
            >
              {isPlaying ? '⏸️ Pause' : '▶️ Play'}
            </motion.button>

            <motion.button
              className="control-btn reset-btn"
              onClick={onReset}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              disabled={!selectedScenario || isPlaying}
            >
              🔄 Reset
            </motion.button>
          </div>

          <div className="progress-container">
            <div className="progress-info">
              <span>Step {currentStepIndex + 1} of {totalSteps}</span>
              <span>{Math.round(getProgressPercentage())}% Complete</span>
            </div>
            <div className="progress-bar">
              <motion.div
                className="progress-fill"
                initial={{ width: 0 }}
                animate={{ width: `${getProgressPercentage()}%` }}
                transition={{ duration: 0.3 }}
                style={{ backgroundColor: selectedScenario.color }}
              />
            </div>
          </div>

          <div className="scenario-stats">
            <div className="stat-item">
              <strong>Total Steps:</strong> {selectedScenario.steps.length}
            </div>
            <div className="stat-item">
              <strong>Feedback Loops:</strong> {selectedScenario.feedbackLoops}
            </div>
            <div className="stat-item">
              <strong>Final Status:</strong> 
              <span className={`status-indicator ${selectedScenario.finalStatus}`}>
                {selectedScenario.finalStatus.toUpperCase()}
              </span>
            </div>
            <div className="stat-item">
              <strong>Estimated Duration:</strong> 
              {Math.round(selectedScenario.steps.reduce((sum, step) => sum + step.duration, 0) / 1000)}s
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default ScenarioControls;
