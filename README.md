# Chimerax-InspectET

Visualize CryoET Alignments in 3D.

Currently supports these formats:
- IMOD (only global alignments, not XTILT yet)
- AreTomo3
- cryoET data portal

## Install

Download the wheel file from the [most recent release](https://github.com/uermel/chimerax-InspectET/releases/) and run this command in the ChimeraX command line:

```
toolshed install /PATH/TO/WHEEL/ChimeraX_InspectET-0.0.5-py3-none-any.whl
```

## Usage

**Using IMOD basename and real data:**

https://github.com/user-attachments/assets/155f1418-d0d2-45b2-a1db-ee0aa5bec8f0

**Using simulated boxes:**

https://github.com/user-attachments/assets/6c87c46b-2f33-4021-b9b2-af050643aea2

**Making an animation:**

Create animations of the alignment using the `inspectet play` command:

```
inspectet play framesPerView 10 loopNumber 4
```

  




