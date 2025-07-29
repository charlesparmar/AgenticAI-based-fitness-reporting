# LangGraph Workflow Flow Diagram

## Overview
This document provides a detailed flow diagram of the AgenticAI-based Fitness Reporting System using LangGraph for orchestration.

## Workflow Architecture

```mermaid
graph TD
    A[START: fetch_email] --> B[fetch_database]
    B --> C[reconcile_data]
    C --> D{Data Exists?}
    
    D -->|No| E[validate_data]
    D -->|Yes| Z[END: Data Already Exists]
    
    E --> F{Validation Success?}
    F -->|Yes| G[supabase_entry]
    F -->|No| Z
    
    G --> H{Supabase Success?}
    H -->|Yes| I[report_drafter]
    H -->|No| Z
    
    I --> J[email_evaluation]
    J --> K[feedback_decision]
    
    K --> L{Email Approved?}
    L -->|Yes| M[send_final_email]
    L -->|No| N{Max Iterations?}
    
    N -->|No| O[feedback_loop]
    N -->|Yes| M
    
    O --> I
    
    M --> P[cleanup]
    P --> Q[END: Workflow Complete]
    
    style A fill:#e1f5fe
    style Q fill:#c8e6c9
    style Z fill:#ffcdd2
    style M fill:#fff3e0
    style P fill:#f3e5f5
```

## Detailed Node Flow

### 1. **fetch_email** 📧
- **Purpose**: Fetch latest fitness email from Gmail
- **Input**: Gmail credentials from environment
- **Output**: Email data in JSON format
- **Next**: fetch_database

### 2. **fetch_database** 🗄️
- **Purpose**: Fetch latest database entry from SQLite Cloud
- **Input**: None (uses stored credentials)
- **Output**: Database data in JSON format
- **Next**: reconcile_data

### 3. **reconcile_data** 🔄
- **Purpose**: Compare email data with database using LLM
- **Input**: Email JSON + Database JSON
- **Output**: Reconciliation result with data_exists flag
- **Next**: validate_data (if data doesn't exist)

### 4. **validate_data** 🔍
- **Purpose**: Validate fitness data against historical trends
- **Input**: Email data (temporary file)
- **Output**: Validation result with status and confidence
- **Condition**: Only runs if reconciliation shows new data
- **Next**: supabase_entry (if validation successful)

### 5. **supabase_entry** 📱
- **Purpose**: Enter validated data into Supabase application
- **Input**: Email data
- **Output**: Supabase entry result
- **Condition**: Only runs if validation was successful
- **Next**: report_drafter (if entry successful)

### 6. **report_drafter** 📝
- **Purpose**: Draft fitness report email using LLM
- **Input**: Supabase data + feedback (if iteration > 1)
- **Output**: Email body data
- **Condition**: Only runs if Supabase entry was successful
- **Next**: email_evaluation

### 7. **email_evaluation** 🔍
- **Purpose**: Evaluate email body quality and provide feedback
- **Input**: Email body data from report_drafter
- **Output**: Evaluation result with approval status and feedback
- **Condition**: Only runs if report_drafter was successful
- **Next**: feedback_decision

### 8. **feedback_decision** 🤔
- **Purpose**: Decide whether to continue feedback loop or send email
- **Input**: Email evaluation result + iteration count
- **Logic**:
  - If email approved → send_final_email
  - If max iterations (3) reached → send_final_email
  - Otherwise → feedback_loop
- **Next**: Conditional based on decision

### 9. **feedback_loop** 🔄
- **Purpose**: Update feedback and iteration count for next iteration
- **Input**: Email evaluation result
- **Output**: Updated state with feedback and incremented iteration
- **Next**: report_drafter (restart drafting with feedback)

### 10. **send_final_email** 📤
- **Purpose**: Send the approved email using Final Email Agent
- **Input**: Email body data from report_drafter
- **Output**: Email sending result
- **Features**: 
  - Excel attachment with all historical data
  - Push notification after successful send
- **Next**: cleanup

### 11. **cleanup** 🧹
- **Purpose**: Clean up browser sessions and system resources
- **Input**: None
- **Output**: Cleanup result
- **Next**: end_workflow

### 12. **end_workflow** 🏁
- **Purpose**: Workflow termination
- **Input**: Final state
- **Output**: Complete workflow result

## State Management

### WorkflowState Structure
```python
class WorkflowState(TypedDict):
    email_data: Dict[str, Any]              # Email fetching result
    database_data: Dict[str, Any]           # Database fetching result
    reconciliation_result: Dict[str, Any]   # Data reconciliation result
    validation_result: Dict[str, Any]       # Data validation result
    supabase_result: Dict[str, Any]         # Supabase entry result
    report_drafter_result: Dict[str, Any]   # Report drafting result
    email_evaluation_result: Dict[str, Any] # Email evaluation result
    feedback: str                           # Feedback for iterations
    iteration_count: int                    # Current iteration (1-3)
    max_iterations: int                     # Maximum iterations (3)
    final_email_sent: bool                  # Email sending status
    cleanup_result: Dict[str, Any]          # Cleanup result
    error: str                              # Error messages
    timestamp: str                          # Workflow timestamp
```

## Conditional Logic

### Data Existence Check
```python
if reconciliation_result.get('data_exists'):
    # Skip to end - data already exists
    return "end_workflow"
else:
    # Continue with validation
    return "validate_data"
```

### Validation Success Check
```python
if validation_result.get('validation_result', {}).get('validation_status') == 'Validation Success':
    # Continue with Supabase entry
    return "supabase_entry"
else:
    # Skip to end - validation failed
    return "end_workflow"
```

### Email Approval Logic
```python
if email_evaluation_result.get('approved', False):
    # Email approved - send it
    return "send_final_email"
elif iteration_count >= max_iterations:
    # Max iterations reached - force send
    return "send_final_email"
else:
    # Continue feedback loop
    return "feedback_loop"
```

## Error Handling

### Graceful Degradation
- **Missing data**: Workflow continues with available data
- **API failures**: Error messages captured in state
- **Validation failures**: Workflow ends gracefully
- **Email failures**: Error logged, cleanup still runs

### State Persistence
- **Partial results**: Stored in state for debugging
- **Error messages**: Captured in state.error field
- **Timestamps**: Tracked for monitoring

## Performance Characteristics

### Execution Flow
1. **Sequential execution** for data fetching and validation
2. **Conditional branching** based on data existence and validation
3. **Iterative feedback loop** for email quality improvement
4. **Parallel processing** within individual agents

### Time Estimates
- **Email fetching**: ~5-10 seconds
- **Database fetching**: ~2-5 seconds
- **Data reconciliation**: ~10-15 seconds
- **Validation**: ~5-10 seconds
- **Supabase entry**: ~10-20 seconds
- **Report drafting**: ~15-30 seconds
- **Email evaluation**: ~5-10 seconds
- **Feedback loop**: Variable (1-3 iterations)
- **Email sending**: ~5-10 seconds
- **Cleanup**: ~2-5 seconds

**Total estimated time**: 2-5 minutes (depending on iterations)

## Monitoring and Observability

### LangSmith Integration
- **Project**: Charles-Fitness-report
- **Tracing**: V2 enabled for all operations
- **Endpoint**: https://api.smith.langchain.com
- **Dashboard**: https://smith.langchain.com/

### Logging Points
- **Node entry/exit**: Each node logs start/completion
- **Conditional decisions**: Decision points logged
- **Error conditions**: All errors captured and logged
- **Performance metrics**: Execution times tracked

### State Inspection
- **Intermediate results**: Available at each step
- **Error propagation**: Errors bubble up through state
- **Iteration tracking**: Feedback loop progress monitored

## Key Features

### 🔄 **Feedback Loop System**
- **Maximum 3 iterations** for email quality improvement
- **LLM-based evaluation** of email content
- **Structured feedback** for iterative improvement
- **Automatic approval** after max iterations

### 📊 **Data Validation**
- **Historical trend analysis** using LLM
- **Confidence scoring** for validation decisions
- **Pushover notifications** for validation results
- **Temporary file management** for data processing

### 📤 **Email System**
- **Excel attachment** with complete historical data
- **Push notifications** after successful sending
- **Gmail OAuth2.0** integration
- **Professional formatting** with LLM assistance

### 🧹 **Resource Management**
- **Automatic cleanup** of browser sessions
- **Temporary file removal** after processing
- **Memory management** for long-running workflows
- **Error recovery** and graceful degradation

## Workflow Variants

### Early Termination Paths
1. **Data already exists** → End immediately
2. **Validation fails** → End with error
3. **Supabase entry fails** → End with error
4. **Report drafting fails** → End with error

### Success Paths
1. **Email approved on first try** → Send immediately
2. **Email approved after feedback** → Send after iterations
3. **Email forced after max iterations** → Send with current version

### Error Recovery
- **Network issues**: Retry logic in individual agents
- **API failures**: Graceful degradation with error messages
- **Resource issues**: Cleanup ensures system stability 