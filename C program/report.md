## Results from executing main_ARM on MinorCPU and TimingSimpleCPU
| Stats   |   Minor CPU   | TimingSimple CPU | Notes|
|:----------:|:-------------:|:------:|:------:|
| sim_insts | 11,257 | 11,202 | Nearly the same |
| sim_ops | 12,772 | 12,663 | Minor has more due to micro-op decomposition |
| numCycles | 72,232 | 87,476 | Minor needed less cycles |
| idleCycles | 51,776 | 0 | Timing Simple was always busy |
| host_inst_rate | 268,224 | 622,472 | TimingSimple calculates faster |
| sim_seconds (us) | 36 | 44 | TimingSimple needed more time |
| CPI | 6.416630 | 7.8 | For TimingSimple calculated as 87,476 Cycles / 11,202 Instructions | 

### Explanation
#### Similarities
* sim_insts (instructions simulated): Nearly identical (11,257 vs. 11,202).
Reason: Both run the same executable (e.g., a "hello" or similar program), so the total dynamic instruction count is workload-dependent and not affected by CPU model internals. The slight difference (~0.5%) could be due to Minor's micro-op decomposition or minor execution variations, but it's negligible.

* sim_ops (ops including micro-ops): Close (12,772 vs. 12,663).
Reason: Ops represent the total operations (instructions + micro-ops). Minor decomposes instructions into micro-ops for pipeline accuracy, leading to ~1% more ops. TimingSimple treats instructions more functionally, with fewer breakdowns. Both reflect the same workload, so similarity holds.

#### Differences
* sim_ticks/sim_seconds (total ticks/simulated time): TimingSimple longer (43.7M ticks / 0.000044s vs. 36.1M / 0.000036s).
Reason: TimingSimple stalls on every memory access (timing mode), waiting for cache/memory responses, inflating simulated time. Minor models pipeline stages more efficiently, with less waiting, leading to faster simulated execution despite idling.

* CPI (cycles per instruction): Minor better (6.42 CPI vs. 7.80).
Reason: Minor's detailed pipeline (fixed stages, configurable structures) accurately simulates in-order flow, reducing wasted cycles. TimingSimple's functional approach overestimates latencies (e.g., atomic accesses assume worst-case times), increasing CPI. 

* host_inst_rate (simulator efficiency, inst/s): TimingSimple faster (622,472 vs. 268,224).
Reason: TimingSimple is simpler (no detailed pipeline stages, fewer internal structures), so the host simulates it quicker. Minor's complexity (e.g., pipeline evaluation, activity recording) adds overhead, slowing host-side processing despite better simulated performance.

* numCycles (CPU cycles): TimingSimple more (87,476 vs. 72,232).
Reason: Aligns with higher CPI—TimingSimple's stalls and simpler execution require more cycles. Minor's accurate modeling minimizes cycles by optimizing in-order flow.

* idleCycles/idle_fraction: Minor has significant idling (51,776 cycles / ~72% idle vs. almost 0).
Reason: Minor includes pipeline idling (e.g., for synchronization, event handling) to mimic real hardware accurately. TimingSimple doesn't model idling, as it's purely functional and busy-focused, assuming continuous execution.

* Instruction Breakdowns (e.g., loads, stores, branches): TimingSimple has detailed counts (e.g., 2,063 loads, 1,926 stores, 2,143 branches); Minor lacks or has pipeline-focused stats.
Reason: TimingSimple tracks functional execution details for simplicity. Minor prioritizes pipeline internals (e.g., fetch2 instruction types, branch prediction) over per-instruction counts, as it's designed for micro-architectural analysis.

## Modifying the parameters
We modify the available L1 Instruction and Data cache with the _"--l1d_size = 512B --l1i_size = 512B"_ flag. We reduce it because the program is very simple and in order to see more differentiated statistics.

 Stats   |   Minor CPU   | TimingSimple CPU | Notes|
|:----------:|:-------------:|:------:|:------:|
| sim_insts | 11,202 | 11,257 | same as before modification |
| sim_ops | 12,772 | 12,663 | same as before modification |
| numCycles | 147,314 | 151,618 | Higher | 
| idleCycles | 122,772 | 0.002 | Higher | 
| host_inst_rate | 329,767 | 1,119,807 |  | 
| sim_seconds (us) | 74 | 76 | Significant more time | 
| CPI | 13.086 | 7.80 | Minor CPI higher | 

### Explanation for 512B Cache Results

#### Similarities
* sim_insts and sim_ops: Identical to the original configuration (11,202 / 11,257 insts, 12,663 / 12,772 ops).
  Reason: These metrics are primarily determined by the workload (the ARM executable), not the cache size. The instruction count remains consistent across runs for the same program, as cache size affects timing but not the total dynamic instructions executed.

#### Differences
* numCycles: Both CPUs require significantly more cycles (147,314 for Minor, 151,618 for TimingSimple) compared to the original (~72k-87k).
  Reason: With a tiny 512B cache, cache misses are frequent, causing the CPU to stall waiting for memory accesses. This inflates the cycle count as the pipeline can't proceed efficiently.

* idleCycles: Minor has extremely high idling (122,772 cycles, ~83% idle), while TimingSimple has negligible idling (0.002 cycles).
  Reason: Minor models detailed pipeline behavior, including idling during stalls for cache misses or synchronization. TimingSimple, being functional, doesn't simulate idling and assumes continuous execution, though it still experiences stalls internally.

* host_inst_rate: TimingSimple remains faster to simulate (1,119,807 inst/s vs. Minor's 329,767).
  Reason: TimingSimple's simpler model (no complex pipeline stages) allows quicker host-side computation, even with increased simulated cycles due to misses.

* sim_seconds: Both take longer (74-76 μs vs. ~36-44 μs originally).
  Reason: More cycles and stalls translate to longer simulated time. The small cache amplifies memory latency effects, slowing down the simulation proportionally.

* CPI: Minor's CPI worsens significantly (13.086 vs. original 6.42), while TimingSimple's stays the same (7.80).
  Reason: Small caches lead to higher miss rates, increasing stalls and thus CPI. Minor's detailed modeling captures this more accurately, showing a bigger jump. TimingSimple's functional approach may underestimate some latencies, keeping CPI stable.

Overall, the 512B cache highlights the critical role of cache size in performance: small caches cause frequent misses, degrading CPI and efficiency, especially in detailed models like Minor. TimingSimple trades accuracy for speed, showing less variation but still impacted.

