# Chimerax-InspectET

Visualize CryoET Alignments in 3D.

Currently supports these formats:
- IMOD (only global alignments, not XTILT yet)
- AreTomo3
- cryoET data portal

## Install

Download the wheel file from the most recent release and run this command in the ChimeraX command line:

```
toolshed install /PATH/TO/WHEEL/.whl
```

## Usage

**Using IMOD basename and real data:**

https://github.com/user-attachments/assets/400a8b10-9e6f-44e7-a5a1-019ace61217f

**Using simulated boxes:**

https://github.com/user-attachments/assets/6c87c46b-2f33-4021-b9b2-af050643aea2

**Making an animation:**

Create animations of the alignment using the `inspectet play` command:

```
inspectet play
inspectet play framesPerView 10 loopNumber 4
```

  




