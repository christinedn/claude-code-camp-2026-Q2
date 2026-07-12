# World notes: tbaMUD (localhost:4000)

## Map (confirmed by walking it, 2026-07-11)

Starting field to Market Square (all single exits unless noted):
```
The Great Field Of Midgaard (start, N blocked by "plot device")
  -> S -> The Great Field Of Midgaard (path continues N/S)
  -> S -> Behind The Temple Altar (N to countryside/Dragonhelm Mountains)
  -> S -> By The Temple Altar (statue of Odin)
  -> S -> The Temple Of Midgaard (Reading Room W, donation room E, ATM here) [exits n e s w d]
  -> S -> The Temple Square (Clerics' Guild W, Grunting Boar Inn E, fountain)
  -> S -> Market Square (statue; roads in all 4 directions)
```

From Market Square:
```
Market Square
  -> W -> Main Street (Armory S, Bakery N)
       -> N -> The Bakery (dead end, exit S only)
       -> S -> The Armory (armorer, cityguard, peacekeeper; dead end, exit N only)
  -> E -> Main Street (general store N, Pet Shop S, market place W)
       -> E -> Main Street (weapon shop N, Guild of Swordsmen S)
            -> S -> Entrance Hall To The Guild Of Swordsmen (ATM, knight guard) [exits n e]
                 -> E -> The Bar Of Swordsmen (bulletin board, waiter) [exits s w]
                      -> S -> The Tournament And Practice Yard
                              (guildmaster here; well leads Down into darkness) [exits n d]
```

Unexplored: general store, Pet Shop, weapon shop interiors, Clerics' Guild,
Grunting Boar Inn, Reading Room, donation room, the well leading down from
the practice yard, everywhere east/north beyond the starting field.

## Monsters
- (none fought yet)
- "A beastly fido" - seen mucking through garbage on Main Street near the
  Guild of Swordsmen. Likely a low-level starter mob (fidos are classic
  CircleMUD trash mobs). Untested.

## Shops
- **Bakery** (Main Street, north of the Armory intersection): danish pastry 7g,
  bread 14g, waybread 71g - all unlimited stock. `dummy` has 10g, can afford
  only the danish.
- **Armory**: armor for sale, not itemized yet - `list` there next visit.

## NPCs of note
- Fighters' guildmaster (Tournament And Practice Yard): handles `practice`.
  As of level 1 with 177 exp, 0 practice sessions available - said "you do
  not seem to be able to practice now". Open question below.

## Open questions / TODO
- How are practice sessions earned - leveling up, quests, or something else?
  Check again after gaining a level.
- Where does combat actually happen - do mobs wander into rooms, or do we
  need to seek them out (e.g. the well leading down from the practice yard)?
- No light source yet - night fell once and a field room showed "pitch
  black"; need a torch/lantern from a shop before wandering off lit streets.
