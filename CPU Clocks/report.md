## Clock Domains, Timing, and Scaling in gem5 Benchmarks

## Executive Summary

This report answers critical questions about how `system.clk_domain.clock` and `cpu_clk_domain.clock` affect execution timing, scaling efficiency, and performance bottlenecks in gem5 CPU simulations running the specbzip benchmark.

---

## 1. Clock Domain Evidence from stats.txt Files

From the three benchmark runs (specbzip), we extract the actual clock values from the simulation statistics:

| Run | system.clk_domain.clock | cpu_clk_domain.clock | sim_seconds |
|-----|------------------------:|---------------------:|------------:|
| 1 GHz | 1000 ticks | 1000 ticks | 0.161025 s |
| Default (2 GHz) | 1000 ticks | 500 ticks | 0.083982 s |
| 4 GHz | 1000 ticks | 250 ticks | 0.045678 s |

**Conversion from ticks to Hz:**

In gem5, the simulation frequency is fixed at 1 THz (1×10¹² ticks/second). Clock values represent the **period** in ticks, not frequency:

- **Actual frequency = 1e12 Hz / clock_period_in_ticks**
  - system.clk_domain: 1e12 / 1000 = **1 GHz** (constant in all runs)
  - cpu_clk_domain: 
    - 1e12 / 1000 = **1 GHz** (1GHz run)
    - 1e12 / 500 = **2 GHz** (Default run)
    - 1e12 / 250 = **4 GHz** (4GHz run)

---

## 2. What Is Being Timed at Different Frequencies?

### System Clock Domain (`system.clk_domain.clock`)
- **Controls**: DRAM controller, system interconnect (membus), cache coherency operations, cross-domain synchronization
- **Frequency**: Remains at **1 GHz** in all three runs (clock period = 1000 ticks)
- **Role**: Times all memory accesses, bus transactions, and system-level events

### CPU Cluster Clock Domain (`cpu_clk_domain.clock`)
- **Controls**: CPU cores, L1/L2 caches, pipeline stages, ALUs, register file, branch predictor, per-core logic
- **Frequency**: Changes per run (1 GHz, 2 GHz, 4 GHz)
- **Role**: Times all CPU-centric execution events

### The Critical Insight: Clock Domain Separation

When `cpu_clk_domain` runs faster than `system_clk_domain` (e.g., 4 GHz CPU vs 1 GHz system clock):
- The CPU requests data much faster than the memory system can deliver
- Fixed physical latencies (e.g., ~50 ns DRAM access) translate to **more CPU cycles**
- Clock-domain crossings (CPU ↔ system) introduce synchronization overhead


---

## 3. Why This Separation Exists

gem5 models **independent clock domains** to reflect realistic hardware:

- Separate clock generators for CPU vs. memory subsystems
- Different voltage/frequency scaling (DVFS) policies per domain
- Synchronization logic to bridge clock domains safely


---

## 4. Evidence from config.json (1 GHz Run)

The configuration file confirms the clock domain setup:

```json
"clk_domain": {
    "clock": [1000],                    // system.clk_domain = 1000 ticks = 1 GHz
    "type": "SrcClockDomain"
},
"cpu_clk_domain": {
    "clock": [1000],                    // cpu_clk_domain = 1000 ticks = 1 GHz (for 1GHz run)
    "type": "SrcClockDomain"
}
```

For comparison, the Default (2 GHz) run has: `cpu_clk_domain.clock` = 500 ticks → 2 GHz

---

## 5. Dual-Core Frequency Prediction

**Question**: If we add another processor, what frequency will it have?

**Answer**: The new core will run at the **same `cpu_clk_domain` frequency** unless explicitly reconfigured. 

- Both cores share the same clock domain (`cpu_clk_domain`)
- Both cores see the same CPU frequency (1 GHz, 2 GHz, or 4 GHz per run)

**Realistic Multi-Core Speedup:**

```
Single Core (2 GHz):
  Execution time: 0.083982 seconds

Dual Core (2 GHz) - Theoretical (perfect parallelization):
  Execution time: 0.083982 / 2 ≈ 0.042 seconds
  Expected speedup: 2.0x

Dual Core (2 GHz) - Realistic:
  Execution time: ~0.055-0.065 seconds (estimate)
  Actual speedup: ~1.3-1.5x
  Limitation factors: L2 cache contention, memory bandwidth, coherency overhead
```

---

## 6. Scaling Efficiency Analysis

### Observed Execution Times

| CPU Frequency | sim_seconds (specbzip) |
|---------------:|----------------------:|
| 1 GHz | 0.161025 s |
| 2 GHz (Default) | 0.083982 s |
| 4 GHz | 0.045678 s |

### Speedup Calculations

```
1 GHz → 2 GHz:
  Speedup = 0.161025 / 0.083982 = 1.915x
  Ideal speedup = 2.0x
  Efficiency = 1.915 / 2.0 = 95.75%

1 GHz → 4 GHz:
  Speedup = 0.161025 / 0.045678 = 3.523x
  Ideal speedup = 4.0x
  Efficiency = 3.523 / 4.0 = 88.08%
```

### Conclusion: NO Perfect Scaling

Scaling efficiency **degrades** as CPU frequency increases:
- 1→2 GHz: 95.75% efficiency (nearly ideal)
- 1→4 GHz: 88.08% efficiency (11.9% performance loss)

The loss becomes progressively worse at higher frequencies, indicating a fundamental bottleneck.

---

## 7. Why Scaling Is Imperfect

### Primary Cause: Memory Latency in Clock Cycles

Physical memory latencies are fixed in nanoseconds but scale with CPU frequency **in cycles**:

DRAM access latency: ~50 ns (constant, independent of CPU frequency)

At 1 GHz:
  50 ns ÷ (1 ns per cycle) = 50 CPU cycles

At 2 GHz:
  50 ns ÷ (0.5 ns per cycle) = 100 CPU cycles

At 4 GHz:
  50 ns ÷ (0.25 ns per cycle) = 200 CPU cycles

The cost of each cache miss increases 4x from 1 GHz to 4 GHz.



### Secondary Cause: Limited Memory Bandwidth


The memory bandwidth remains the same whatever the cpu clock is. As a result the memory can't keep up with the requests from the CPU

### Secondary Cause: Shared L2/L3 Cache Contention

- Cache miss rate is proportional to memory access patterns
- At higher frequencies, more instructions contend for the same cache
- Each miss becomes more expensive (in cycles)
- Combined effect: Memory subsystem becomes the critical bottleneck

---

## 8. Complete Metrics Comparison

| Metric | 1 GHz | 2 GHz | 4 GHz |
|--------|------:|------:|------:|
| **sim_seconds** | 0.161025 | 0.083982 | 0.045678 |
| **Speedup vs 1 GHz** | 1.0x | 1.915x | 3.523x |
| **Scaling Efficiency** | 100% | 95.75% | 88.08% |
| **CPI** | 1.6102 | 1.6797 | 1.8271 |
| **L2 Miss Rate** | 28.22% | 28.22% | 28.22% |
| **system.clk_domain** | 1 GHz | 1 GHz | 1 GHz |
| **cpu_clk_domain** | 1 GHz | 2 GHz | 4 GHz |
| **Memory Latency (cycles)** | 50 | 100 | 200 |

---

## 9. Final Conclusions

### Answers to Core Questions

1. **What is being timed at different frequencies?**
   - CPU execution: Times all CPU-centric events using `cpu_clk_domain`
   - Memory: Times all memory operations using `system_clk_domain` (1 GHz fixed)

2. **Why do two clock domains exist?**
   - Real hardware has independent clock generators for CPU and memory
   - Allows modeling of heterogeneous clock scenarios

3. **What frequency would a second processor have?**
   - Same as the first: whatever `cpu_clk_domain` is set to
   - Without separate clock domains per core, both run synchronously

4. **Is scaling perfect across frequencies?**
   - **NO.** Efficiency drops from 95.75% (1→2 GHz) to 88.08% (1→4 GHz)
   - 11.9% performance loss at 4 GHz indicates significant bottlenecks

5. **Why isn't scaling perfect?**
   - **Primary**: Fixed memory latency becomes exponentially worse in cycles
   - **Secondary**: Limited bandwidth

### Practical Implications

**For CPU Design:**
- Don't increase frequency without improving memory bandwidth
- Cache sizes should scale with frequency (larger L2/L3 at higher clocks)
- Solution: wider memory buses, prefetching, better branch prediction

**For Software Optimization:**
- Higher CPU frequency ≠ always faster (memory-bound workloads plateau)
- Data locality and cache efficiency matter more at high frequencies
- Profile before optimizing; memory bottleneck might be dominant

---
