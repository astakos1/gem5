# optimization 
In this exercise it is requested to optimize a cpu by changing the cache size and assocciativity.
By running the optimization1.sh file in the gem5 folder we get the results of the simulations. Then we use the read_results.sh script with the conf_script.ini to extract the CPI data. The baseline is 
- L1D 32kB
- L1I 64kB
- L1 assoc 1
- L2 512kB
- L2 assoc 2
- cacheline size 64
- cpu clock 1GHz

In the following tests we keep the baseline parameters and change 1 parameter at a time.
 
|change| CPI | comment| 
|:---:|:---:|:---:|
|baseline |	2.650259  | baseline
L1 associativity 2		|2.631263| better
L1 associativity 4		|2.631263| same as 2
L1I size 128kB	|	2.650305| higher
L1D size 64kB	|   2.640463| better
L1D size 128kB	|	2.636110| better than 64kB
L2 associativity 4	|	2.640405| better
L2 associativity 8	|	2.639899| better than assoc 4
L2 associativity 16| 	2.639899| same as 8
L2 associativity 32|	2.639908| same as 8
L2 size 1024KB|	2.640031| better
L2 size 2048KB|	2.638463| better than 1MB
L2 size 4096KB|	2.636092| better than 2MB
cacheline 512|	1.574962| much better
cacheline 256|	1.691744| much better
cacheline 128|	2.008416| much better
cacheline 32|	3.925389| worse
cacheline 16|	6.614754| worse
clk_2|	3.513414 | higher CPI but faster overall
clk_4|	5.320101 | higher CPI but faster overall

We conclude that the L1 associativity doesn't change the CPI much, while the cacheline size changes it drastically. Improving the L2 and L1 size also increases the CPI. The best parameters are the following.

- L1 associativity 2
- L1I size 128KB
- L1D size 128KB
- L2 associativity 8 (since higher will increase hardware complexity)
- L2 size 4096KB (max allowed by the exercise)
- cacheline size 512 
- A faster cpu clock would reduce the time for the completion of the program. For example the 4GHz clock increases the cpi by 32% but the speed is almost 3.5 times better, but this exersise requests lower CPI, not time. For this reason we will keep the clock at 1GHz.

By applying these parameters a CPI of 1.491601 is achieved

Some considerations: Although higher cache size is improving the CPI, the available area on the silicone chip is limited. Additioinally, higher associativity increases hardware complexity and access time

# Cost Function for Cache Memory Architecture


##  Area Cost Model

### 1. Theoretical Background

SRAM used in caches requires **6 transistors per bit** (6T SRAM cell). In comparison, DRAM needs only 1 transistor + 1 capacitor per bit, which is why cache memory is significantly more expensive.

According to the CACTI model (Cache Access and Cycle Time Information) widely used in computer architecture:

### 2. Area Cost Function

$$C_{area} = \alpha_{L1} \cdot C_{L1} + \alpha_{L2} \cdot C_{L2}$$

Where:

**L1 Cache Cost:**
$$C_{L1} = S_{L1} \cdot (k_{data} + k_{tag} \cdot A_{L1}) \cdot \beta_{L1}$$

**L2 Cache Cost:**
$$C_{L2} = S_{L2} \cdot (k_{data} + k_{tag} \cdot A_{L2}) \cdot \beta_{L2}$$

### 3. Weight Coefficients

| Coefficient | Value | Justification |
|-------------|-------|---------------|
| $\alpha_{L1}$ | **3.0 - 5.0** | L1 uses faster (more expensive) transistors, located near core, requires stricter timing margins |
| $\alpha_{L2}$ | **1.0** | Baseline reference |
| $\beta_{L1}$ | **1.0** | Baseline size coefficient |
| $\beta_{L2}$ | **0.7 - 0.8** | L2 can use denser cells (density-optimized) |
| $k_{data}$ | **1.0** | Cost for data arrays |
| $k_{tag}$ | **0.15 - 0.25** | Cost for tag arrays (proportionally smaller) |

### 4. Associativity Cost

Increasing associativity adds:

1. **Comparators**: $A$ comparators for tag matching
2. **Multiplexers**: $A$-to-1 mux for way selection
3. **Replacement Logic**: LRU/PLRU hardware complexity ~$O(\log_2 A)$ for PLRU
4. **CAM Overhead**: Content-Addressable Memory overhead

$$C_{assoc}(A) = A \cdot k_{comp} + \log_2(A) \cdot k_{mux} + LRU_{cost}(A)$$

LRU Cost Estimation:
- A ≤ 2: $LRU_{cost} = 1$ (1 bit per set)
- A = 4: $LRU_{cost} = 3$ (pseudo-LRU with 3 bits)
- A = 8: $LRU_{cost} = 7$ (pseudo-LRU with 7 bits)
- A > 8: True LRU becomes prohibitive, approximations used

## Latency Cost Model

### 1. Access Latency Model

Based on research and the CACTI model:

$$T_{access}(S, A) = T_{base} \cdot (1 + k_s \cdot \log_2(S)) \cdot (1 + k_a \cdot \log_2(A))$$

Where:
- $T_{base}$: Base access time (1 cycle for minimal cache)
- $k_s \approx 0.1 - 0.2$: Size impact coefficient
- $k_a \approx 0.05 - 0.15$: Associativity impact coefficient

### 2. Typical Latency Values

| Level | Latency (cycles) | Size | Associativity |
|-------|------------------|------|---------------|
| L1 Data | **3-4** | 32-64 KB | 4-8 way |
| L1 Instruction | **3-4** | 32-64 KB | 4-8 way |
| L2 | **10-14** | 256KB-1MB | 8-16 way |
| L3 | **30-50** | 8-32 MB | 12-16 way |
| Main Memory | **100-300** | GBs | N/A |

### 3. Average Memory Access Time (AMAT)

$$AMAT = T_{L1} + MR_{L1} \cdot (T_{L2} + MR_{L2} \cdot T_{mem})$$

Where $MR$ = Miss Rate for each level.

## Cache Line Size Impact

### 1. Trade-offs

| Larger Cache Line | Advantages | Disadvantages |
|-------------------|------------|---------------|
| B ↑ | Better spatial locality | Larger miss penalty |
| B ↑ | Fewer tags (smaller overhead) | Cache pollution |
| B ↑ | More efficient DRAM burst | False sharing (multicore) |

### 2. Optimal Size

Literature shows:
- **32 bytes**: Legacy systems
- **64 bytes**: Typical for modern x86/ARM processors
- **128 bytes**: Some high-bandwidth systems

$$C_{line}(B) = k_{transfer} \cdot B + k_{pollution} \cdot B^{0.5}$$

## Complete Cost Function

### 1. Total Cost Function

$$C_{total} = w_a \cdot C_{area} + w_l \cdot C_{latency} + w_p \cdot C_{power}$$

Where $w_a$, $w_l$, $w_p$ are weights depending on designer priorities.

### 2. Practical Form (Arbitrary Cost Units)

```
Cost_Total = 
    # L1 Area Cost (more expensive per KB)
    3.5 × S_L1 × (1 + 0.15 × A_L1)
    
    # L2 Area Cost
    + 1.0 × S_L2 × (1 + 0.10 × A_L2)
    
    # Associativity Complexity
    + 2.0 × A_L1 × log2(A_L1)
    + 0.8 × A_L2 × log2(A_L2)
    
    # Cache Line Overhead
    + 0.5 × (64/B) × (S_L1 + S_L2)  # Tag overhead inversely proportional to B
    
    # High-Frequency Penalty (stricter timing requirements)
    + 1.5 × (f_CPU / 2.0) × S_L1  # Normalized to 2 GHz baseline
```

### 3. Calculations

**default Configuration:**
- L1: 96 KB, 1-way
- L2: 512 KB, 2-way  
- B: 64 bytes
- f: 1.0 GHz

```
Cost = 3.5×96×(1+0.15×1) + 1.0×512×(1+0.10×2) 
       + 2.0×1×1×log2(1) + 0.8×2×log2(2)
       + 0.5×1×(96+512)
       + 1.5×0.5×96
       
       = 386.4 + 614.4 + 1.6 + 304 + 272 + 72
       = 1650.4 units
```

**Best CPI Configuration:**
- L1: 256 KB, 2-way
- L2: 4096 KB, 16-way  
- B: 512 bytes
- f: 1.0 GHz

```
Cost = 3.5×256×(1+0.15×2) + 1.0×4096×(1+0.10×16) 
       + 2.0×2×1 + 0.8×16×4
       + 0.5×0.125×(256+4096)
       + 1.5×0.5×256
       
       = 1164.8 + 10649.6 + 4 + 51.2 + 272 + 192
       = 12333.6 units
```

**Low L2 CPI Configuration:**
- L1: 256 KB, 2-way
- L2: 1024 KB, 4-way  
- B: 512 bytes
- f: 1.0 GHz

```
Cost = 3.5×256×(1+0.15×2) + 1.0×1024×(1+0.10×4) 
       + 2.0×2×1 + 0.8×4×4
       + 0.5×0.125×(256+1024)
       + 1.5×0.5×256
       
       = 1164.8 + 1433.6 + 4 + 12.8 + 80 + 192
       = 2887.2 units
```

**Conclusions**  
Even though we heavily optimized our CPI, The complexity and cost increased dramatically. for a 77.68% improvement in CPI, the cost increased 747.3%. The major increase is due to the L2 cache size and associativity. By reducing the L2 size to 1KB and the L2 associativity to 4, the CPI becomes 1.492062, increased by less than 1% while the cost decreased by 76.59%. 

## Design Decision Guidelines

### 1. Rules of Thumb

| Change | Cost Impact | Performance Impact |
|--------|-------------|-------------------|
| 2× L1 Size | +3.5× cost increase | -20-40% miss rate |
| 2× L1 Assoc | +15-25% cost | -10-15% miss rate |
| 2× L2 Size | +1× cost increase | -30-50% miss rate |
| 2× L2 Assoc | +10-15% cost | -5-10% miss rate |
| 2× Cache Line | Complex | Workload dependent |

## Summary

This analysis provides a **qualitative and quantitative framework** for evaluating design choices in memory hierarchy. Key conclusions:

1. **L1 is ~3-5× more expensive per byte** than L2 due to speed-optimized design
2. **Associativity has sub-linear effect** on miss rate but linear/super-linear effect on cost
3. **Cache line size** affects both tag overhead and spatial locality
4. **CPU frequency** imposes stricter timing margins on L1

Additionally, the L2 cache was found to have a major factor in cost, while marginally improving the CPI. As a result, it was desided to be reduced as a more realistic scenario.

## References

1. **CACTI**: Muralimanohar, N., Balasubramonian, R., & Jouppi, N. P. "CACTI 6.0: A Tool to Model Large Caches." HP Laboratories Technical Report.

2. **Memory Hierarchy Design**: Hennessy, J. L., & Patterson, D. A. "Computer Architecture: A Quantitative Approach." Morgan Kaufmann.

3. **SRAM Cell Design**: Rabaey, J. M. "Digital Integrated Circuits: A Design Perspective." Prentice Hall.

4. **Cache Design Trade-offs**: Jouppi, N. P. "Improving Direct-Mapped Cache Performance by the Addition of a Small Fully-Associative Cache and Prefetch Buffers." ISCA 1990.
