import matplotlib.pyplot as plt

# Data points from your results
results = {
    'baseline': 2.650, 'L1a_2': 2.631, 'L1a_4': 2.631,
    'L1is_64': 2.650, 'L1is_128': 2.650, 'L1id_64': 2.640, 'L1id_128': 2.636,
    'L2a_4': 2.640, 'L2a_8': 2.639, 'L2a_16': 2.639, 'L2a_32': 2.639,
    'L2s_1024': 2.640, 'L2s_2048': 2.638, 'L2s_4096': 2.636,
    'cacheline_16': 6.614, 'cacheline_32': 3.925, 'cacheline_128': 2.008, 
    'cacheline_256': 1.691, 'cacheline_512': 1.574,
    'clk_2': 3.513, 'clk_4': 5.320
}

def create_plot(title, labels, values, filename):
    plt.figure(figsize=(8, 5))
    plt.bar(labels, values, color='navy')
    plt.title(title)
    plt.ylabel('CPI')
    plt.xticks(rotation=15)
    plt.grid(True, axis='y', linestyle='--')
    # Add text labels on top of bars
    for i, v in enumerate(values):
        plt.text(i, v + 0.05, str(v), ha='center')
    plt.tight_layout()
    plt.savefig(filename)
    print("Saved: " + filename)
    plt.close()

# 1. L1 Size Impact
create_plot("L1 Total Size vs CPI", 
            ["Base", "I-128", "D-64", "D-128"], 
            [results['baseline'], results['L1is_128'], results['L1id_64'], results['L1id_128']], 
            "l1_size.png")

# 2. L1 Associativity
create_plot("L1 Associativity vs CPI", 
            ["1-way", "2-way", "4-way"], 
            [results['baseline'], results['L1a_2'], results['L1a_4']], 
            "l1_assoc.png")

# 3. L2 Size (The error was here)
create_plot("L2 Size vs CPI", 
            ["512k", "1024k", "2048k", "4096k"], 
            [results['baseline'], results['L2s_1024'], results['L2s_2048'], results['L2s_4096']], 
            "l2_size.png")

# 4. L2 Associativity
create_plot("L2 Associativity vs CPI", 
            ["2-way", "4-way", "8-way", "16-way"], 
            [results['baseline'], results['L2a_4'], results['L2a_8'], results['L2a_16']], 
            "l2_assoc.png")

# 5. Clock Speed
create_plot("Clock Speed vs CPI", 
            ["1GHz", "2GHz", "4GHz"], 
            [results['baseline'], results['clk_2'], results['clk_4']], 
            "clock_speed.png")

# 6. Cacheline Size
create_plot("Cacheline Size vs CPI", 
            ["16", "32", "64", "128", "256", "512"], 
            [results['cacheline_16'], results['cacheline_32'], results['baseline'], results['cacheline_128'], results['cacheline_256'], results['cacheline_512']], 
            "cacheline.png")