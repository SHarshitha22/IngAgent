# tests/test_agents.py

from agents.ingestion_agent import IngestionAgent
from db import Database
import os

def test_ingestion_agent():
    """Test that ingestion agent runs and saves data to DB."""

    pr_number = int(os.getenv("PR_NUMBER", "1"))

    agent = IngestionAgent()
    db = Database()

    # Run ingestion
    output = agent.run(pr_number)

    # Basic checks on returned dict
    assert "title" in output
    assert "author" in output
    assert "changed_files" in output

    # Check DB stored the output
    saved = db.get_agent_output(pr_number, "ingestion_agent")
    assert saved is not None
    assert "changed_files" in saved
