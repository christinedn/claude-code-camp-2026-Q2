# Preweek Technical Documentation

## Technical Goal

The technical goal of Preweek (Explore) is to determine how well do Agent Architetures fit our business use-case. For example, an agent file with referenced AGENT.md, or agent skills driven by main agent eg. ~/.skills.

## Technical Uncertainty

- Uncertain if an coding harness agentic loop is capable enough to drive a non-coding workload
- Uncertain if the LLM thinking mode is able to hold memory and drive decisions
- Uncertain that a coding harness can interact with a MUD without a interface or SDK/manage the nc session

## Technical Hypotheses

- Based on the example agent architectures, we will probably have issues with the coding harness driving the MUD without an interface. This is because agents usually have a hard time driving APIs since the API is not defined.
- We will need an interface because managing a long-living telnet session can be difficult.
- We will likely need to implement a specialized agentic loop for our use-case, as typical models memory will not be capable enough to remember and navigate the MUD world.
- We may need to roll-our-own agent without an SDK because generic primitives for observability/memory . Our use-case will require specialized implementation and we also want to connect with all frontier models and SDKs will lack one of them.

## Technical Observations

- An Agent.md could not connect to the MUD. It could create scripts but was not really able to connect to the MUD and needed knowledge of of the deterministic TUI of the MUD.
- Skills and Subsgents performed when given a script to manage the telnet session. Thye were able to play the MUD (although maybe not in the most efficient way).
- Using Markdown files where the coding harness updates simple memory files to produce brittle navigation instructions. Example below:

```sh
Starting field to Market Square (all single exits unless noted):
The Great Field Of Midgaard (start, N blocked by "plot device")
  -> S -> The Great Field Of Midgaard (path continues N/S)
  -> S -> Behind The Temple Altar (N to countryside/Dragonhelm Mountains)
  -> S -> By The Temple Altar (statue of Odin)
  -> S -> The Temple Of Midgaard (Reading Room W, donation room E, ATM here) [exits n e s w d]
  -> S -> The Temple Square (Clerics' Guild W, Grunting Boar Inn E, fountain)
  -> S -> Market Square (statue; roads in all 4 directions)
```

## Technical Conclusions

- Skills and subagents are capable of playing the MUD.
- We need memory for map navigation/world data.
- New technical use-case of wehther or not we should have our agent handle multiple sessions of multiple players. Co-op is a common factor in MUD so this is something to consider.
- We could not n8n completely due to technical restraints executing external scripts.
- We are still uncertain of implementing our own specialzied loops, and will need to explored more in week 2.
- Without a customized agentic loop, the agent could not perform exploration goals efficiently and did not have any key meta/journey player strategies.

## Key Takeway

- When we have a specialized use-case like playing MUD, we likely cannot leverage generic SDKs for agents because we need speciailized tools/agentic loops.
