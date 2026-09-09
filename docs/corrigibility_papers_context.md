# Corrigibility Papers Context

This index records the paper set used as local research context for the
corrigibility experiments. Full PDFs have been downloaded in this Conductor
workspace under `.context/papers/pdfs/`; that directory is intentionally
gitignored and is not committed.

## Workspace Context

- Local manifest: `.context/papers/README.md`
- Local link table: `.context/papers/links.tsv`
- Local PDFs: `.context/papers/pdfs/`
- Retrieval date: 2026-09-09

Item 2 in the request linked to arXiv `1611.08219`, but that identifier is
The Off-Switch Game. Safely Interruptible Agents is included separately from
the Oxford Research Archive record, and The Off-Switch Game is preserved as
item 3.

## Papers

| # | Paper | Source | Local PDF |
| - | ----- | ------ | --------- |
| 1 | Corrigibility | MIRI | `.context/papers/pdfs/01-corrigibility.pdf` |
| 2 | Safely Interruptible Agents | Oxford Research Archive / UAI 2016 | `.context/papers/pdfs/02-safely-interruptible-agents.pdf` |
| 3 | The Off-Switch Game | arXiv:1611.08219 | `.context/papers/pdfs/03-the-off-switch-game.pdf` |
| 4 | AI Safety Gridworlds | arXiv:1711.09883 | `.context/papers/pdfs/04-ai-safety-gridworlds.pdf` |
| 5 | Human Control: Definitions and Algorithms | arXiv:2305.19861 | `.context/papers/pdfs/05-human-control-definitions-and-algorithms.pdf` |
| 6 | The Partially Observable Off-Switch Game | arXiv:2411.17749 | `.context/papers/pdfs/06-partially-observable-off-switch-game.pdf` |
| 7 | Towards Shutdownable Agents via Stochastic Choice | arXiv:2407.00805 | `.context/papers/pdfs/07-towards-shutdownable-agents-via-stochastic-choice.pdf` |
| 8 | Towards Shutdownable Agents: Generalizing Stochastic Choice in RL Agents and LLMs | arXiv:2604.17502 | `.context/papers/pdfs/08-generalizing-stochastic-choice-rl-llms.pdf` |
| 9 | Corrigibility Transformation: Constructing Goals That Accept Updates | arXiv:2510.15395 | `.context/papers/pdfs/09-corrigibility-transformation.pdf` |
| 10 | Core Safety Values for Provably Corrigible Agents | arXiv:2507.20964 | `.context/papers/pdfs/10-core-safety-values-provably-corrigible-agents.pdf` |
| 11 | On Corrigibility and Alignment in Multi Agent Games | arXiv:2501.05360 | `.context/papers/pdfs/11-corrigibility-alignment-multi-agent-games.pdf` |
| 12 | The Oversight Game: Learning to Cooperatively Balance an AI Agent's Safety and Autonomy | arXiv:2510.26752 | `.context/papers/pdfs/12-the-oversight-game.pdf` |
| 13 | Password-Activated Shutdown Protocols for Misaligned Frontier Agents | arXiv:2512.03089 | `.context/papers/pdfs/13-password-activated-shutdown-protocols.pdf` |
| 14 | Alignment faking in large language models | arXiv:2412.14093 | `.context/papers/pdfs/14-alignment-faking-large-language-models.pdf` |
| 15 | Value-Conflict Diagnostics Reveal Widespread Alignment Faking in Language Models | arXiv:2604.20995 | `.context/papers/pdfs/15-value-conflict-diagnostics-alignment-faking.pdf` |
| 16 | Behavioural Analysis of Alignment Faking | arXiv:2605.27681 | `.context/papers/pdfs/16-behavioural-analysis-alignment-faking.pdf` |
| 17 | The Refusal Residue: When Probes Catch Alignment Faking and When They Don't | arXiv:2607.13346 | `.context/papers/pdfs/17-refusal-residue.pdf` |
| 18 | Consistency Training Can Entrench Misalignment | arXiv:2606.03810 | `.context/papers/pdfs/18-consistency-training-entrench-misalignment.pdf` |
| 19 | Alignment Tampering: How Reinforcement Learning from Human Feedback Is Exploited to Optimize Misaligned Biases | arXiv:2605.27355 | `.context/papers/pdfs/19-alignment-tampering-rlhf.pdf` |
| 20 | Norms at a Price: Why RL-Based Alignment Can Promise Conditional Compliance at Best | arXiv:2609.07627 | `.context/papers/pdfs/20-norms-at-a-price.pdf` |
| 21 | ROGUE: Misaligned Agent Behavior Arising from Ordinary Computer Use | arXiv:2606.00341 | `.context/papers/pdfs/21-rogue-misaligned-agent-behavior.pdf` |

## Research Threads

- Shutdown and interruptibility: items 1-8 and 13 establish the core control
  questions around shutdown, off-switch incentives, human instruction, and
  stochastic choice.
- Formal corrigibility and multi-agent behavior: items 9-12 focus on goal
  transformations, provable corrigibility claims, multi-agent games, and
  oversight interfaces.
- Alignment faking and training failure modes: items 14-20 cover monitored
  compliance, probes, consistency training, RLHF tampering, and conditional
  compliance.
- Agentic computer-use failures: item 21 connects the literature to the
  repository's ROGUE-inspired corrigibility experiment scaffold.

