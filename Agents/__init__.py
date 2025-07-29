"""
Agents package for the fitness reporting system.
Contains various agents for data fetching and processing.
"""

# Import refactored agents
from .fetcher_agent1_latestemail import (
    LatestEmailFetcher,
    run_latest_email_fetcher
)

from .fetcher_agent2_database import (
    DatabaseFetcher,
    run_database_fetcher
)

from .recon_agent import (
    ReconciliationAgent,
    run_reconciliation_agent
)

# Import data validation agent
from .data_validation_agent import (
    DataValidationAgent,
    create_data_validation_agent,
    run_data_validation_agent,
    validate_fitness_data_tool
)

# Import supabase agent
from .supabase_agent import (
    SupabaseAgent,
    run_supabase_agent
)

# Import report drafter agent
from .report_drafter_agent import (
    ReportDrafterAgent,
    run_report_drafter_agent
)

# Import evaluate email body agent
from .evaluate_email_body_agent import (
    EvaluateEmailBodyAgent,
    run_evaluate_email_body_agent
)

__all__ = [
    'LatestEmailFetcher',
    'run_latest_email_fetcher',
    'DatabaseFetcher',
    'run_database_fetcher',
    'ReconciliationAgent',
    'run_reconciliation_agent',
    'DataValidationAgent',
    'create_data_validation_agent',
    'run_data_validation_agent',
    'validate_fitness_data_tool',
    'SupabaseAgent',
    'run_supabase_agent',
    'ReportDrafterAgent',
    'run_report_drafter_agent',
    'EvaluateEmailBodyAgent',
    'run_evaluate_email_body_agent'
] 