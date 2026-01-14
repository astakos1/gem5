# First part   
In the first part it is asked to run the _"./build/ARM/gem5.opt -d hello_result configs/example/arm/starter_se.py --cpu="minor" "tests/test-progs/hello/bin/arm/linux/hello"_ command that simulates the _"starter_se.py"_ file with the _"minorCPU"_. According to the stats.txt we conclude that 
* the Simulator instruction rate is 299655 inst/s
* The frequency was 1GHz
* Number of instructions simulated 5027
* Number of ops (including micro ops) simulated 5831
* CPI: 6.991048 = 7
* IPC (Instructions Per Cycle) 0.143
* Total number of cycles that the object has spent stopped 24816
* number of cpu cycles simulated 35144
* Number of conditional branches predicted 1359
* Number of miss predicted indirect branches 63
* Number of BTB hits 395
* BTB Hit Percentage 20.5%
* Number of bytes read from this memory (total) 10688
* Total number of bytes read from DRAM 15040
* L1 Instruction Cache number of demand (read+write) accesses 2793
* L1 Instruction Cache number of demand (read+write) hits 2466
* L1 Instruction Cache hit percentage 88.3%
* L1 Data Cache number of demand (read+write) accesses 2160
* L1 Data Cache number of demand (read+write) hits 1983
* L1 Data Cache hit percentage 91.8%
* L2 total number of demand (read+write) accesses 474
* L2 number of overall misses 474
  

from the config.ini we confirm that
* it is a single core cpu (cpu_id=0)
* memory is 2Gb (mem_ranges=0:2147483647)
* L1 Instruction Cache is 48Kb 3 way set associative (addr_ranges=0:18446744073709551615
assoc=3)
* L1 Data Cache is 32Kb 2 way set associative (addr_ranges=0:18446744073709551615
assoc=2)
* L2 Cache is 1Mb 16 way set associative (addr_ranges=0:18446744073709551615
assoc=16)
* L2 hit access time is 12 cycles (data_latency=12)

The sim_ticks is the total amount of the simulation tun time in ticks, hereby 35144000. Each tick is 1 ps, specified by the clock period.

sim_seconds is the total simulated time in seconds, hereby 0.000035 = 35 ms. This is derived bt dividing sim_ticks / sim_freq.

sim_insts is the number of committed instructions finished by the simulated cpu, hereby 5027.

host_insts_rate is the simulator's efficiency and is calculated by the number of instructions processed per second. hereby 299655 inst/s

**L1 and L2 accesses:**
* The L1 Instruction Cache accesses were 2793 (icache.demand_accesses::total)  
* The L1 Data Cache accesses were 2160 (dcache.demand_accesses::total)  
* Total L1 Cache accesses were 4953 (icache.demand_accesses::total + dcache.demand_accesses::total)  
* The L2 Cache accesses were 474 (system.cpu_cluster.l2.demand_accesses::total)


We could also calculate the Cache accesses by the following methodes:   
**L1 D-Cache Accesses**: Sum all the individual request types sent from the CPU to the data cache:  
Accesses = ReadReq Hits + ReadReq Misses + WriteReq Hits + WriteReq Misses  
**L2 Cache Accesses**: The L2 cache is only accessed when there is a miss in the L1 caches. Therefore:  
L2 Accesses = L1 Instruction Cache Misses + L1 Data Cache Misses

---
