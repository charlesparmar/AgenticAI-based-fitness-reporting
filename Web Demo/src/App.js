import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import WorkflowDiagram from './components/WorkflowDiagram';
import ScenarioControls from './components/ScenarioControls';
import './App.css';

function App() {
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [currentStep, setCurrentStep] = useState(null);
  const [playbackInterval, setPlaybackInterval] = useState(null);

  const totalSteps = selectedScenario ? selectedScenario.steps.length : 0;

  // Reset the demo
  const resetDemo = useCallback(() => {
    setIsPlaying(false);
    setCurrentStepIndex(0);
    setCurrentStep(null);
    if (playbackInterval) {
      clearInterval(playbackInterval);
      setPlaybackInterval(null);
    }
  }, [playbackInterval]);

  // Handle scenario selection
  const handleScenarioSelect = useCallback((scenario) => {
    resetDemo();
    setSelectedScenario(scenario);
  }, [resetDemo]);

  // Start playback
  const startPlayback = useCallback(() => {
    if (!selectedScenario) return;

    setIsPlaying(true);
    setCurrentStepIndex(0);
    setCurrentStep(selectedScenario.steps[0]);

    const interval = setInterval(() => {
      setCurrentStepIndex((prevIndex) => {
        const nextIndex = prevIndex + 1;
        
        if (nextIndex >= selectedScenario.steps.length) {
          // Playback complete
          setIsPlaying(false);
          clearInterval(interval);
          setPlaybackInterval(null);
          return prevIndex;
        }

        setCurrentStep(selectedScenario.steps[nextIndex]);
        return nextIndex;
      });
    }, 2000); // 2 seconds per step

    setPlaybackInterval(interval);
  }, [selectedScenario]);

  // Pause playback
  const pausePlayback = useCallback(() => {
    setIsPlaying(false);
    if (playbackInterval) {
      clearInterval(playbackInterval);
      setPlaybackInterval(null);
    }
  }, [playbackInterval]);

  // Handle play/pause toggle
  const handlePlayPause = useCallback(() => {
    if (isPlaying) {
      pausePlayback();
    } else {
      startPlayback();
    }
  }, [isPlaying, startPlayback, pausePlayback]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (playbackInterval) {
        clearInterval(playbackInterval);
      }
    };
  }, [playbackInterval]);

  // Update current step when index changes
  useEffect(() => {
    if (selectedScenario && currentStepIndex < selectedScenario.steps.length) {
      setCurrentStep(selectedScenario.steps[currentStepIndex]);
    }
  }, [currentStepIndex, selectedScenario]);

  return (
    <div className="App">
      <motion.div 
        className="app-container"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <header className="app-header">
          <motion.h1 
            className="app-title"
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            🤖 LangGraph Workflow Demo
          </motion.h1>
          <motion.p 
            className="app-subtitle"
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            Interactive demonstration of the Fitness Reporting Workflow with animated flow progression
          </motion.p>
        </header>

        <main className="app-main">
          <motion.div
            className="scenarios-sidebar"
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <ScenarioControls
              selectedScenario={selectedScenario}
              onScenarioSelect={handleScenarioSelect}
              isPlaying={isPlaying}
              onPlay={handlePlayPause}
              onPause={handlePlayPause}
              onReset={resetDemo}
              currentStepIndex={currentStepIndex}
              totalSteps={totalSteps}
            />
          </motion.div>

          <motion.div
            className="diagram-main"
            initial={{ x: 20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.8 }}
          >
            <WorkflowDiagram
              currentStep={currentStep}
              scenario={selectedScenario}
              isPlaying={isPlaying}
              onStepComplete={() => {}}
            />
          </motion.div>
        </main>

        <footer className="app-footer">
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 1.0 }}
          >
            <p>
              🚀 Built with React, Mermaid.js, and Framer Motion | 
              📊 Real-time workflow visualization | 
              🎯 Interactive scenario testing
            </p>
          </motion.div>
        </footer>
      </motion.div>
    </div>
  );
}

export default App;
