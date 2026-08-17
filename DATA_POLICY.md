# EchoCare Data Handling Policy (Prototype)

**What is stored:** daily check-in transcripts, sentiment/linguistic trend scores,
prescription data (name, dosage, timing — synthetic only in this prototype).

**What is NOT stored:** raw audio beyond transcription (transcribe, discard audio),
any data not needed for trend analysis.

**Retention:** transcripts retained 90 days for trend comparison, then auto-deleted
(to be implemented in Phase 2 as a scheduled cleanup job).

**Access:** only the check-in agent and pattern-analysis agent read transcripts;
only the escalation agent and an authenticated caregiver view alert summaries —
never raw transcripts, only the cited evidence excerpt.

**Deletion:** a user or their designated caregiver can request full deletion at any time.

**Disclaimer:** EchoCare is a research/portfolio prototype, not a validated medical
device, and does not diagnose any condition.
