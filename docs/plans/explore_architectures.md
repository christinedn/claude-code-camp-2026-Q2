# Explore Agent Architectures

The largest confusion tech professionals have is applying the correct agent solution because
many solutions appears to overlap responsibilities.

We wille xplore multiple agent architecture to determine fit for our agent workload.

## 1. An agent file with referenced files eg. AGENT.md, @~/docs/\*.md

The simplest agent is creating an "agent file" and possibly importing other files that are read conditioanlly when needed.

We should attempt to create an agent file and see if it can connect to the MUD and complete a simple goal: eg. "Find the bakery and list the menu."

We want to use the smallest and least intelligent model and scale up.

## Technical Observations

Using Haiku 4.5, we created a CLAUDE.md with a simple prompt, and told it will need to mange its own local memory via simple markdown files. We provided it with the location of the MUD and the players credentials.

The agent struggled to connect to the MUD.
The agentw ould attempt to create temporary code files to manage a nc connection and execute commands.
The agent did not have enough information about Text User Interface of the MUD to login and see its mistakes.
The agentw ould try and read files not relating to the task.
Increasing the model intelligence to Sonnet 4.6 did not help.

### Technical Conclusions

We could probably write a better prompt or create an artifact that would give the agent full knowledge of the MUD's Text User Interface to successfully login, but since this experience is so fixed, it would be better to have a script that exactly knows how to login so we are not wasting token/usage and deterministic user flows.

Coding harnesses tend to go task and try to write code which we do not need our agent to do. Coding harnesses at least at this specific architecture stage does not appear to be a good fit.

We are justified to build our own Mud SDK to connect to the MUD since clearly the agent wants to manage the connection via script and execute comon commands over the port.

If had an MCP server to our MUD SDK then mabe we could drive the agent ebtter at this architectural level.

I think due to the complexity of the world and player state data I simply do not think updating markdown files will be sufficient but we never concluded whether the curernt agentic loop for the coding harness could handle said task.

Use coding harneses for coding, and for specialized agents make your own loop.
