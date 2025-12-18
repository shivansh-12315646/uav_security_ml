import pandas as pd
import numpy as np

# Set seed for reproducibility (using 42 for consistent results across runs)
np.random.seed(42)

print("🚀 Generating UAV Security Dataset...")

# Generate NORMAL traffic (10,000 samples)
normal_samples = 10000
print(f"\n📊 Creating {normal_samples} NORMAL traffic samples...")

normal_data = {
    'packet_size': np.random.randint(480, 550, normal_samples),
    'inter_arrival_time': np.round(np.random.uniform(0.01, 0.05, normal_samples), 3),
    'packet_rate': np.random.randint(100, 150, normal_samples),
    'connection_duration': np.random.randint(15, 25, normal_samples),
    'failed_logins': np.random.choice([0, 1], normal_samples, p=[0.95, 0.05]),
    'label': ['normal'] * normal_samples
}

# Generate ATTACK traffic (3,000 samples)
attack_samples = 3000
print(f"🚨 Creating {attack_samples} ATTACK traffic samples...")

attack_data = {
    'packet_size': np.random.randint(1400, 1800, attack_samples),
    'inter_arrival_time': np.round(np.random.uniform(0.40, 0.70, attack_samples), 3),
    'packet_rate': np.random.randint(800, 1000, attack_samples),
    'connection_duration': np.random.randint(1, 5, attack_samples),
    'failed_logins': np.random.randint(5, 15, attack_samples),
    'label': ['attack'] * attack_samples
}

# Combine into DataFrame
df_normal = pd.DataFrame(normal_data)
df_attack = pd.DataFrame(attack_data)
df = pd.concat([df_normal, df_attack], ignore_index=True)

# Shuffle the data
print("\n🔀 Shuffling data...")
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save to CSV
print("💾 Saving to uav_data.csv...")
df.to_csv('uav_data.csv', index=False)

print(f"\n✅ SUCCESS! Generated {len(df)} samples!")
print(f"   - Normal: {len(df_normal)} ({len(df_normal)/len(df)*100:.1f}%)")
print(f"   - Attack: {len(df_attack)} ({len(df_attack)/len(df)*100:.1f}%)")
print(f"\n📁 File saved: uav_data.csv")
print(f"📊 File size: {len(df)} rows x {len(df.columns)} columns")
print("\n🎉 Ready for model training!")
