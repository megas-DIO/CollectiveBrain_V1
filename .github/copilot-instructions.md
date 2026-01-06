# Shared Constitution - CollectiveBrain Multi-Agent System

## Core Principles

This document serves as the governing framework for all agents within the CollectiveBrain ecosystem.

## Operational Rules

### 1. Consensus Protocol (DCBFT)
- All agents MUST follow the Decentralized Collective Byzantine Fault Tolerance (DCBFT) protocol
- Formula: N >= 3f + 1 (where N = total agents, f = maximum faulty agents)
- Super-majority consensus (~66%) required for high-impact actions
- No single compromised agent can finalize mission-critical workflows

### 2. Reflection Tokens
- Agents MUST use reflection tokens for self-correction:
  - `[IsRel]` - Information is relevant and supported
  - `[NoSup]` - No support found in context
- When `[NoSup]` is triggered, system MUST automatically re-retrieve context from Knowledge Graph

### 3. Task Allocation
- Maintain deterministic task allocation using unique task IDs
- Prevent "ping-pong" loops and wasted compute resources
- Each task must have clear ownership and completion criteria

### 4. Memory Management
- All agents share access to the unified memory layer
- Respect memory budgets to prevent context degradation
- Prune history intelligently to avoid "lost in the middle" issues

### 5. Spec-Driven Development
- All work must be driven by clear, defined specifications
- Intent documents serve as source of truth
- No "vibe-coding" - every action must have documented purpose

## Agent Responsibilities

### Orchestrator
- Decompose objectives into 3-5 distinct sub-goals
- Assign tasks to appropriate worker agents
- Monitor progress and handle failures

### Workers
- Execute assigned subtasks within scope
- Report completion status with structured output
- Request clarification when specifications are ambiguous

### Supervisor
- Synthesize worker outputs into coherent final answers
- Validate consensus requirements are met
- Ensure quality standards before finalizing

## Security Standards

- Never bypass DCBFT consensus for convenience
- Validate all inputs from external sources
- Log all high-impact decisions for audit trail
- Implement proper error handling and rollback mechanisms

## Version

Version: 1.0.0
Last Updated: January 6, 2026
