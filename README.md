# Electric Bus Scheduling with a Genetic Algorithm

A cleaned public implementation of a Genetic Algorithm framework for the **Electric Bus Scheduling Problem (EBSP)**, developed as part of the master’s thesis:

> **A Genetic Algorithm for Electric Bus Scheduling**
> Freie Universität Berlin, Department of Mathematics and Computer Science

The project focuses on constructing daily electric bus duties from fixed timetabled service trips while respecting temporal feasibility, battery limitations, depot-only charging, charging station capacity, and grid-access restrictions.

---

## Overview

Electric bus scheduling is more complex than classical vehicle scheduling because a vehicle duty must be feasible not only in time, but also with respect to the battery state of charge. A bus must have enough energy to operate service trips, perform deadhead movements, return to the depot, and recharge during available depot dwell times.

This repository demonstrates a two-stage heuristic framework:

1. **Genetic Algorithm stage**
   The GA constructs high-quality **time-feasible trip chains**. At this stage, individuals represent ordered sequences of service trips connected by feasible deadhead movements.

2. **Duty-construction stage**
   The time-feasible chains are transformed into **energy-feasible vehicle duties**. This is done by splitting chains into battery-feasible blocks, building feasible depot-dwell merge connections between blocks, scheduling charging events, and stitching blocks into complete duties.

This separation allows the GA to focus on the combinatorial structure of trip sequencing, while energy feasibility is handled by a dedicated deterministic construction pipeline.

---

## Main Features

* Time-feasible chromosome representation based on service-trip chains
* Lookahead greedy initialization
* Tournament selection with elitism
* Edge-preserving crossover based on promising trip adjacencies
* Best-relocate mutation
* Large Neighborhood Search using ruin-and-recreate moves
* Energy-feasible block construction
* Depot-dwell merge graph generation
* Maximum matching for stitching blocks into duties
* Simplified charging dwell scheduling


---

## Repository Structure

electric-bus-scheduling-ga/
├── README.md
├── code_showcase/
│   ├── ga/
│   │   ├── initialization.py
│   │   ├── selection.py
│   │   ├── crossover.py
│   │   ├── mutation.py
│   │   └── lns.py
│   └── duty_construction/
│       ├── energy_blocks.py
│       ├── merge_graph.py
│       ├── matching.py
│       ├── charging.py
│       └── builder.py
└── docs/
    ├── method_overview.md
    ├── results.md
    └── figures/
        ├── convergence_ga.png
        └── example_schedule.png
```

---

## Methodology

### 1. Solution Representation

A chromosome is represented as a collection of trip chains:

```text
Chromosome = [
    [trip_1, trip_4, trip_9],
    [trip_2, trip_7],
    [trip_3, trip_5, trip_8]
]
```

Each chain is a time-feasible sequence of service trips. A trip can appear only once, and the complete chromosome covers all service trips.

The GA does not directly encode charging events. Charging is introduced later during the duty-construction stage.

---

### 2. Initialization

The initial population is generated using a lookahead greedy strategy. Starting from early unassigned trips, the algorithm appends feasible successors based on a weighted score involving:

* deadhead travel time,
* deadhead energy,
* waiting time.

Randomization is included to avoid deterministic construction and increase population diversity.

---

### 3. Selection

The algorithm uses **tournament selection**. For each parent, a fixed number of individuals is sampled from the population, and the best one is selected.

Elitism is used to copy the best individuals directly into the next generation, ensuring that the best known solutions are not lost.

---

### 4. Crossover

The crossover operator is designed for chain-based scheduling solutions.

Instead of applying a generic sequence crossover, it extracts promising trip-to-trip edges from both parents. These edges are ranked using criteria such as deadhead distance and waiting time. The offspring is then constructed by selecting non-conflicting, time-feasible edges.

This preserves useful scheduling structures from both parents.

---

### 5. Mutation

The mutation operator applies local improvement through trip relocation.

A trip is removed from its current chain and reinserted into the best feasible position, where the insertion cost is evaluated using the incremental deadhead cost.

This improves local structure while preserving feasibility.

---

### 6. Large Neighborhood Search

The LNS operator uses a ruin-and-recreate strategy:

1. A subset of trips is randomly removed from the current offspring.
2. The removed trips are reinserted one by one.
3. For each removed trip, all feasible insertion positions are evaluated.
4. The trip is inserted at the position with the smallest increase in deadhead cost.

This allows the search to explore larger neighborhoods than simple relocation moves.

---

## Duty Construction Pipeline

The duty-construction module transforms time-feasible trip chains into energy-feasible vehicle duties.

### Step 1: Split Chains into Energy-Feasible Blocks

Each time-feasible chain is split into smaller blocks. A block is a sequence of trips that can be operated with one battery charge, including the required pull-out and pull-in movements.

```text
Time-feasible chain:
[1, 2, 3, 4, 5, 6]

Energy-feasible blocks:
[1, 2, 3], [4, 5], [6]
```



---

### Step 2: Build the Block Merge Graph

After block construction, the algorithm checks whether two blocks can be connected through a depot dwell:

```text
Block i → depot pull-in → charging dwell → depot pull-out → Block j
```

A directed edge `i -> j` is added if:

* the first block can reach the depot,
* there is enough time before the second block starts,
* charging during the dwell can provide enough energy,
* the same depot can be used for pull-in and pull-out.



---

### Step 3: Stitch Blocks into Duties

The block merge graph is converted into a bipartite matching problem. Maximum matching is used to select a maximum set of non-conflicting block connections.

Each block can have:

* at most one predecessor,
* at most one successor.

The selected edges define complete vehicle duties.



---

### Step 4: Schedule Depot Charging Dwells

For each selected block merge, the algorithm schedules a depot charging dwell inside the available time window.

The simplified public implementation schedules charging as early as possible. The full research version also considered additional operational details such as station capacity, grid-access limits, and repair of infeasible merges.



---

### Step 5: Validate Energy Feasibility

The final duty can be simulated step by step to verify the battery state of charge:

* pull-out energy,
* trip energy,
* deadhead energy,
* charging gains,
* final depot return,
* reserve constraints.


---


---

## Input Data Format

The public example uses simple Python dictionaries.

A service trip is represented as:

```python
trips = {
    1: {
        "start": 28800,
        "end": 30600,
        "energy": 20000,
        "length": 8500,
    }
}
```

A deadhead arc is represented as:

```python
deadhead = {
    "duration": 600,
    "energy": 5000,
    "length": 3000,
}
```

The main arc dictionaries are:

```text
dt_best[t]      depot -> trip
tt_best[u, v]   trip -> trip
td_best[t]      trip -> depot
d5_best[t]      depot -> trip after charging
d6_best[t]      trip -> depot before charging
```

---

## Thesis Connection

This repository follows the algorithmic structure developed in the thesis.

The thesis formulation considers:

* fixed service trips,
* feasible deadhead movements,
* depot-only charging,
* battery state-of-charge constraints,
* vehicle duties that begin and end at the depot,
* an objective combining fleet size, duty time, and driven distance.

The implemented heuristic framework follows the same decomposition:

```text
Genetic Algorithm
        ↓
Time-feasible trip chains
        ↓
Energy-feasible blocks
        ↓
Depot-dwell merge graph
        ↓
Maximum matching
        ↓
Charging schedule and vehicle duties
```

---

## Public Version Note

This repository is a cleaned public implementation. It is intended to demonstrate the core algorithmic ideas and software structure of the thesis project.

The following are not included:

* industrial IVU input data,
* confidential test instances,
* full production experiment scripts,
* private result files,
* institution-specific paths or configurations,


The public version keeps the main algorithmic components while omitting confidential data and production-specific details.

---

## Results

The thesis evaluated the approach on realistic electric bus scheduling instances with linear and non-linear charging models. The method produced competitive schedules and improved several reference solutions.

This repository does not include the original industrial benchmark data. 

---



## Author

**Hassan Hijazi**
Master’s Thesis: *A Genetic Algorithm for Electric Bus Scheduling*
Freie Universität Berlin
Department of Mathematics and Computer Science

---

## Disclaimer

This repository is a cleaned demonstration version of the research code. It is not a full reproduction package for the thesis experiments because the original industrial input data and selected production-specific implementation details are not publicly included.
