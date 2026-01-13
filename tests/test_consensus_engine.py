"""Tests for Consensus Engine module."""

import pytest
from consensus_engine import DCBFTEngine, VoteType, ConsensusDecision


class TestDCBFTEngine:
    """Test suite for DCBFT consensus engine."""

    def test_calculate_min_agents(self):
        """Test minimum agents calculation (N >= 3f + 1)."""
        engine = DCBFTEngine(max_faulty_agents=1)
        assert engine.min_required_agents == 4  # 3*1 + 1

        engine2 = DCBFTEngine(max_faulty_agents=2)
        assert engine2.min_required_agents == 7  # 3*2 + 1

    def test_calculate_quorum(self):
        """Test quorum calculation (~66%)."""
        engine = DCBFTEngine(max_faulty_agents=1)

        assert engine._calculate_quorum(3) == 2  # ceil(3 * 2/3)
        assert engine._calculate_quorum(4) == 3  # ceil(4 * 2/3)
        assert engine._calculate_quorum(5) == 4  # ceil(5 * 2/3)

    def test_initiate_vote_success(self):
        """Test successful vote initiation."""
        engine = DCBFTEngine(max_faulty_agents=1)
        agents = ["agent_1", "agent_2", "agent_3", "agent_4"]

        vote_session = engine.initiate_vote(
            "test_decision",
            "Test decision description",
            agents
        )

        assert vote_session["decision_id"] == "test_decision"
        assert vote_session["status"] == "pending"
        assert len(vote_session["required_agents"]) == 4
        assert vote_session["quorum_required"] == 3

    def test_initiate_vote_insufficient_agents(self):
        """Test vote initiation with insufficient agents."""
        engine = DCBFTEngine(max_faulty_agents=1)
        agents = ["agent_1", "agent_2"]  # Need 4, only have 2

        result = engine.initiate_vote(
            "test_decision",
            "Test decision",
            agents
        )

        assert result["status"] == "failed"
        assert "error" in result

    def test_cast_vote_success(self):
        """Test successful vote casting."""
        engine = DCBFTEngine(max_faulty_agents=1)
        agents = ["agent_1", "agent_2", "agent_3", "agent_4"]

        engine.initiate_vote("test_decision", "Test", agents)

        result = engine.cast_vote(
            "test_decision",
            "agent_1",
            VoteType.APPROVE,
            "Test justification"
        )

        assert result["status"] == "recorded"
        assert result["vote_recorded"] == "approve"
        assert result["total_votes"] == 1

    def test_cast_vote_duplicate(self):
        """Test duplicate vote prevention."""
        engine = DCBFTEngine(max_faulty_agents=1)
        agents = ["agent_1", "agent_2", "agent_3", "agent_4"]

        engine.initiate_vote("test_decision", "Test", agents)
        engine.cast_vote("test_decision", "agent_1", VoteType.APPROVE)

        # Try to vote again
        result = engine.cast_vote("test_decision", "agent_1", VoteType.REJECT)

        assert result["status"] == "failed"
        assert "already voted" in result["error"]

    def test_cast_vote_unauthorized(self):
        """Test unauthorized vote prevention."""
        engine = DCBFTEngine(max_faulty_agents=1)
        agents = ["agent_1", "agent_2", "agent_3", "agent_4"]

        engine.initiate_vote("test_decision", "Test", agents)

        result = engine.cast_vote(
            "test_decision",
            "unauthorized_agent",
            VoteType.APPROVE
        )

        assert result["status"] == "failed"
        assert "not authorized" in result["error"]

    def test_tally_votes_consensus_reached(self):
        """Test consensus reached scenario."""
        engine = DCBFTEngine(max_faulty_agents=1)
        agents = ["agent_1", "agent_2", "agent_3", "agent_4"]

        engine.initiate_vote("test_decision", "Test", agents)

        # Cast votes (3 approve = quorum)
        engine.cast_vote("test_decision", "agent_1", VoteType.APPROVE)
        engine.cast_vote("test_decision", "agent_2", VoteType.APPROVE)
        engine.cast_vote("test_decision", "agent_3", VoteType.APPROVE)

        result = engine.tally_votes("test_decision")

        assert result["decision"] == ConsensusDecision.REACHED.value
        assert result["vote_breakdown"]["approve"] == 3
        assert result["quorum_met"] is True

    def test_tally_votes_consensus_failed(self):
        """Test consensus failed scenario."""
        engine = DCBFTEngine(max_faulty_agents=1)
        agents = ["agent_1", "agent_2", "agent_3", "agent_4"]

        engine.initiate_vote("test_decision", "Test", agents)

        # Cast mixed votes (no quorum for either)
        engine.cast_vote("test_decision", "agent_1", VoteType.APPROVE)
        engine.cast_vote("test_decision", "agent_2", VoteType.REJECT)
        engine.cast_vote("test_decision", "agent_3", VoteType.REJECT)

        result = engine.tally_votes("test_decision")

        assert result["decision"] == ConsensusDecision.FAILED.value
        assert result["quorum_met"] is True

    def test_tally_votes_insufficient(self):
        """Test insufficient votes scenario."""
        engine = DCBFTEngine(max_faulty_agents=1)
        agents = ["agent_1", "agent_2", "agent_3", "agent_4"]

        engine.initiate_vote("test_decision", "Test", agents)

        # Only 2 votes, need 3 for quorum
        engine.cast_vote("test_decision", "agent_1", VoteType.APPROVE)
        engine.cast_vote("test_decision", "agent_2", VoteType.APPROVE)

        result = engine.tally_votes("test_decision")

        assert result["decision"] == ConsensusDecision.INSUFFICIENT_VOTES.value
        assert result["votes_cast"] == 2
        assert result["quorum_required"] == 3

    def test_get_decision_status(self):
        """Test getting decision status."""
        engine = DCBFTEngine(max_faulty_agents=1)
        agents = ["agent_1", "agent_2", "agent_3", "agent_4"]

        engine.initiate_vote("test_decision", "Test", agents)

        status = engine.get_decision_status("test_decision")

        assert status is not None
        assert status["is_finalized"] is False
        assert status["status"] == "pending"

    def test_verify_consensus_legacy(self):
        """Test legacy verify_consensus method."""
        engine = DCBFTEngine()

        # Test with sufficient nodes and votes
        votes = [True, True, True, True]  # 4 approvals
        result = engine.verify_consensus(votes, f_faulty_nodes=1)
        assert result == "Consensus Reached"

        # Test with insufficient approvals
        votes = [True, False, False, False]  # Only 1 approval
        result = engine.verify_consensus(votes, f_faulty_nodes=1)
        assert result == "Consensus Failed"

        # Test with insufficient nodes
        votes = [True, True]  # Only 2 nodes, need 4
        result = engine.verify_consensus(votes, f_faulty_nodes=1)
        assert "Insufficient nodes" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
