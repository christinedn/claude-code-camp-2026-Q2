---
name: mud-player
description: >
  Connect to and play a tbaMUD/CircleMUD text game running over telnet (default
  localhost:4000) using the bundled mudctl.py daemon, with persistent memory in
  data/player.md and data/world.md so play can be driven toward longer-term goals
  across many turns - e.g. "reach level 7", "defeat the orc warlord", "save up
  200 gold". Use this whenever the user wants to log into, explore, or play the
  MUD, including single commands like "move north in the mud", "attack the
  monster", "check my inventory in the game", "play tbamud", or any request to
  issue MUD commands or read game state. The MUD is one long stateful session, so
  ALWAYS drive it through mudctl.py rather than raw `nc` (a fresh nc per command
  loses login/room state and garbles the telnet handshake).
---

# Playing the MUD (tbaMUD on localhost:4000)

A MUD is a single persistent TCP session. Login, current room, inventory, and
combat all live on that one connection. `scripts/mudctl.py` runs a background
daemon that holds the socket open, answers the telnet client-detection
handshake, and logs every byte the server sends. You send commands and read
output through it.

`SCRIPT=scripts/mudctl.py` (relative to this skill dir). Run with `python3`.

## Default credentials

Character `dummy`, password `helloworld`. Ask the user before using different
credentials or a different host/port.

## Core commands

- `python3 $SCRIPT start [--host H] [--port P]` - connect + daemonize, prints the banner
- `python3 $SCRIPT send "<line>" [--pause SECS]` - send one line, wait, print new output
- `python3 $SCRIPT wait --for "REGEX" -t SECS` - block until text appears, then print new output
- `python3 $SCRIPT recent` - print output since the last read
- `python3 $SCRIPT tail -n N` - last N lines of the whole session log
- `python3 $SCRIPT status` - connected or not
- `python3 $SCRIPT stop` - disconnect

`send`/`recent`/`wait` share a read cursor, so each call shows only what's new -
you won't re-read the whole log every time.

## Memory: data/player.md and data/world.md

The MUD itself only shows you what's in the current room - it has no memory of
where the orc warlord's lair was three rooms back, or that you're 1,646 exp
short of level 7. That's what these two files are for. They live at
`data/player.md` and `data/world.md` relative to this skill dir. Read them at
the start of a session to pick up where you left off, and update them whenever
something changes - don't wait until the end, since a crash or a long combat
death mid-session would otherwise lose the write.

If the files don't exist yet, create them from these templates:

**`data/player.md`** - who you are and what you're working toward:
```markdown
# Player: dummy

## Current goal
<what the user asked for, e.g. "reach level 7" or "defeat the orc warlord in the necropolis">

## Status (last updated: <timestamp>)
- Level: 1  Exp: 177 / 2000 (to next level)
- HP: 21/21  Mana: 100/100  Move: 85/85
- Gold: 10
- Location: The Great Field Of Midgaard

## Inventory
- (nothing yet)

## Equipment
- (nothing worn)

## Known skills/spells
- kick (poor)

## Progress log
- <date>: created character, starting goal set to reach level 7
```

**`data/world.md`** - what you've learned about the world that isn't in any
single room description:
```markdown
# World notes: tbaMUD (localhost:4000)

## Map
- Midgaard start field -> south -> Behind The Temple Altar -> south -> Temple
  of Midgaard -> south -> Temple Square -> south -> Market Square
- Bakery: from Market Square go west (Main Street), then north
- Guild of Swordsmen: Market Square -> east -> east -> east -> south (entrance
  hall) -> east (bar) -> south (practice yard, guildmaster here)

## Monsters
- <mob name>: <location>, <notable drops/danger/level>

## Shops
- Bakery: danish 7g, bread 14g, waybread 71g

## Open questions / TODO
- <anything you haven't figured out yet, e.g. "where do practice sessions come from?">
```

Use `score` and `inventory`/`equipment` in-game to refresh the numbers in
player.md - don't guess at HP or gold, always read them off the actual game
output. world.md is more free-form: add a line whenever you learn a room
connection, a mob's location, or a shop's stock that would otherwise mean
re-discovering it next time.

## Working toward a goal (multi-turn play)

When the user gives you a standing goal ("reach level 7", "kill the orc
warlord"), the loop each turn is:

1. Read `data/player.md` and `data/world.md` first, so you know current level/
   HP/location and whatever the world notes say about relevant mobs or routes.
2. Decide the next concrete action given the goal and current status - e.g. if
   HP is low, don't seek out a fight, `rest` or return to a safe room; if the
   goal is exp and you're at full health, find and fight something appropriate
   for your level.
3. Act (send commands via mudctl.py), reading the results carefully.
4. Update `data/player.md` with anything that changed (HP, exp, level, gold,
   inventory, location) and append a short line to the progress log. If you
   learned something new about the world (a mob's location, a shop's prices,
   a room connection), add it to `data/world.md`.

Judgment matters more than rigid steps here: a MUD session might span dozens
of turns, mobs can be tougher than expected, and the right move depends on
what actually happens on screen, not a fixed script. If HP drops dangerously
low mid-fight, `flee` rather than dying - death usually costs exp. Treat the
memory files as a durable record you're building up, not a one-time checklist.

## Login sequence (do this exactly, in order)

The prompts arrive with delays, so pause between steps and confirm each prompt
before sending the next. If `status` already says connected and you see a game
prompt like `21H 100M 85V >`, skip login.

1. `python3 $SCRIPT start` - wait for `By what name do you wish to be known?`
   (use `wait --for "name do you wish" -t 8` if the banner is slow)
2. `send "dummy" --pause 1.5` - expect `Password:`
3. `send "helloworld" --pause 2.5` - expect `*** PRESS RETURN:`
4. `send "" --pause 2` - expect the account menu (`1) Enter the game.`)
5. `send "1" --pause 2` - you're in the world; you'll see a room description
   ending in a status prompt like `21H 100M 85V (news) (motd) >`

## Playing

Once in-game, send normal MUD verbs and read the result:

```
python3 $SCRIPT send "look"
python3 $SCRIPT send "north"
python3 $SCRIPT send "inventory"
python3 $SCRIPT send "score"
```

Common verbs: `look` / `l`, movement `n e s w u d`, `look <target>`, `get <item>`,
`inventory` / `i`, `equipment` / `eq`, `wear <item>`, `wield <weapon>`,
`kill <mob>` / `flee`, `cast '<spell>' <target>`, `say <text>`, `who`, `score`.

Reading output well:
- The `HH MM V >` line is the status prompt (hit/mana/move) - it marks the end
  of a response and shows current health.
- After combat or a command that takes a beat, use
  `wait --for "prompt or keyword" -t 6` instead of a fixed pause so you capture
  the full result.
- Movement into a new room prints that room's description and exits
  (`[ Exits: n e s w ]`).

## Leaving cleanly

Before disconnecting, do a final `score` and `inventory`/`equipment` and write
the results into `data/player.md` so the next session starts from accurate
numbers instead of stale ones.

Inside the game, `send "quit"` returns to the menu; `send "0"` exits tbaMUD.
Then `python3 $SCRIPT stop` to tear down the daemon. `stop` alone (without
quitting in-game) also works - it just drops the connection.

## Troubleshooting

- `not connected` on send: run `start` first.
- Stuck at "Attempting to Detect Client": the handshake needs a moment; the
  daemon auto-refuses telnet options so it settles to an `Unknown` client -
  `wait --for "name do you wish" -t 8`.
- Garbled input / wrong prompt: you likely sent a line during the detection
  phase. `stop`, then `start` and follow the login sequence with pauses.
- Full transcript lives at `$TMPDIR/mudctl/mud.log` (or `/tmp/mudctl/mud.log`).
