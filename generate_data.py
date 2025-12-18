import pandas as pd
import numpy as np

# Configuration constants for dataset generation
RANDOM_SEED = 42  # For reproducibility

# Sample counts
NORMAL_SAMPLES = 10000
ATTACK_SAMPLES = 3000

# Normal traffic characteristics
NORMAL_PACKET_SIZE_MIN = 480
NORMAL_PACKET_SIZE_MAX = 550
NORMAL_INTER_ARRIVAL_MIN = 0.01
NORMAL_INTER_ARRIVAL_MAX = 0.05
NORMAL_PACKET_RATE_MIN = 100
NORMAL_PACKET_RATE_MAX = 150
NORMAL_DURATION_MIN = 15
NORMAL_DURATION_MAX = 25

# Attack traffic characteristics
ATTACK_PACKET_SIZE_MIN = 1400
ATTACK_PACKET_SIZE_MAX = 1800
ATTACK_INTER_ARRIVAL_MIN = 0.40
ATTACK_INTER_ARRIVAL_MAX = 0.70
ATTACK_PACKET_RATE_MIN = 800
ATTACK_PACKET_RATE_MAX = 1000
ATTACK_DURATION_MIN = 1
ATTACK_DURATION_MAX = 5
ATTACK_FAILED_LOGINS_MIN = 5
ATTACK_FAILED_LOGINS_MAX = 15

# Set seed for reproducibility (using 42 for consistent results across runs)
np.random.seed(RANDOM_SEED)

print("🚀 Generating UAV Security Dataset...")

# Generate NORMAL traffic
print(f"\n📊 Creating {NORMAL_SAMPLES} NORMAL traffic samples...")

normal_data = {
    'packet_size': np.random.randint(NORMAL_PACKET_SIZE_MIN, NORMAL_PACKET_SIZE_MAX, NORMAL_SAMPLES),
    'inter_arrival_time': np.round(np.random.uniform(NORMAL_INTER_ARRIVAL_MIN, NORMAL_INTER_ARRIVAL_MAX, NORMAL_SAMPLES), 3),
    'packet_rate': np.random.randint(NORMAL_PACKET_RATE_MIN, NORMAL_PACKET_RATE_MAX, NORMAL_SAMPLES),
    'connection_duration': np.random.randint(NORMAL_DURATION_MIN, NORMAL_DURATION_MAX, NORMAL_SAMPLES),
    'failed_logins': np.random.choice([0, 1], NORMAL_SAMPLES, p=[0.95, 0.05]),
    'label': ['normal'] * NORMAL_SAMPLES
}

# Generate ATTACK traffic
print(f"🚨 Creating {ATTACK_SAMPLES} ATTACK traffic samples...")

attack_data = {
    'packet_size': np.random.randint(ATTACK_PACKET_SIZE_MIN, ATTACK_PACKET_SIZE_MAX, ATTACK_SAMPLES),
    'inter_arrival_time': np.round(np.random.uniform(ATTACK_INTER_ARRIVAL_MIN, ATTACK_INTER_ARRIVAL_MAX, ATTACK_SAMPLES), 3),
    'packet_rate': np.random.randint(ATTACK_PACKET_RATE_MIN, ATTACK_PACKET_RATE_MAX, ATTACK_SAMPLES),
    'connection_duration': np.random.randint(ATTACK_DURATION_MIN, ATTACK_DURATION_MAX, ATTACK_SAMPLES),
    'failed_logins': np.random.randint(ATTACK_FAILED_LOGINS_MIN, ATTACK_FAILED_LOGINS_MAX, ATTACK_SAMPLES),
    'label': ['attack'] * ATTACK_SAMPLES
}

# Combine into DataFrame
df_normal = pd.DataFrame(normal_data)
df_attack = pd.DataFrame(attack_data)
df = pd.concat([df_normal, df_attack], ignore_index=True)

# Shuffle the data
print("\n🔀 Shuffling data...")
df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

# Save to CSV
print("💾 Saving to uav_data.csv...")
df.to_csv('uav_data.csv', index=False)

print(f"\n✅ SUCCESS! Generated {len(df)} samples!")
print(f"   - Normal: {len(df_normal)} ({len(df_normal)/len(df)*100:.1f}%)")
print(f"   - Attack: {len(df_attack)} ({len(df_attack)/len(df)*100:.1f}%)")
print(f"\n📁 File saved: uav_data.csv")
print(f"📊 File size: {len(df)} rows x {len(df.columns)} columns")
print("\n🎉 Ready for model training!")
