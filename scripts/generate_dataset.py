"""
Professional UAV Security Dataset Generator
============================================

Generates realistic UAV security dataset with comprehensive features:
- Flight parameters (altitude, speed, direction)
- Communication metrics (signal strength, GPS accuracy)
- System status (battery, temperature, vibration)
- Attack patterns (jamming, spoofing, unauthorized access)

Features:
- 10 comprehensive UAV metrics
- 6 attack types including normal operation
- Balanced dataset with proper distributions
- Realistic attack signatures
- Export to CSV for training
"""
import pandas as pd
import numpy as np
import os

# Configuration
RANDOM_SEED = 42
DATASET_SIZE = 20000  # Total samples
ATTACK_RATIO = 0.30  # 30% attacks, 70% normal

# Attack types distribution
ATTACK_TYPES = {
    'normal': 0.70,
    'jamming_attack': 0.10,
    'gps_spoofing': 0.08,
    'unauthorized_access': 0.07,
    'signal_interference': 0.03,
    'physical_tampering': 0.02
}

# Feature ranges (min, max) for NORMAL operation
NORMAL_RANGES = {
    'altitude': (50, 400),  # meters - normal flight altitude
    'speed': (10, 80),  # km/h - normal cruise speed
    'direction': (0, 360),  # degrees
    'signal_strength': (70, 100),  # percentage - strong signal
    'distance_from_base': (0, 5000),  # meters
    'flight_time': (60, 3600),  # seconds
    'battery_level': (30, 100),  # percentage - healthy battery
    'temperature': (15, 35),  # celsius - normal operating temp
    'vibration': (0, 3),  # scale - minimal vibration
    'gps_accuracy': (80, 100)  # percentage - accurate GPS
}

# Attack signatures - how attacks affect metrics
ATTACK_SIGNATURES = {
    'jamming_attack': {
        'signal_strength': (0, 30),  # Very weak signal
        'gps_accuracy': (0, 40),  # Poor GPS
        'vibration': (5, 10),  # High vibration from distress
    },
    'gps_spoofing': {
        'gps_accuracy': (10, 50),  # Inconsistent GPS
        'altitude': (0, 600),  # Abnormal altitude readings
        'speed': (0, 150),  # Erratic speed
        'direction': (0, 360),  # Rapid direction changes
    },
    'unauthorized_access': {
        'signal_strength': (40, 70),  # Moderate signal (hijacked)
        'direction': (0, 360),  # Unexpected direction
        'speed': (0, 120),  # Unusual speed patterns
        'flight_time': (0, 600),  # Short, suspicious sessions
    },
    'signal_interference': {
        'signal_strength': (20, 50),  # Weak, fluctuating signal
        'gps_accuracy': (40, 70),  # Degraded GPS
        'vibration': (3, 7),  # Moderate vibration
    },
    'physical_tampering': {
        'vibration': (7, 10),  # Very high vibration
        'temperature': (40, 60),  # Overheating
        'battery_level': (0, 40),  # Rapid battery drain
        'altitude': (0, 100),  # Low altitude (grounded/crashed)
    }
}


def generate_normal_sample():
    """Generate a single normal operation sample."""
    return {
        'altitude': np.random.uniform(*NORMAL_RANGES['altitude']),
        'speed': np.random.uniform(*NORMAL_RANGES['speed']),
        'direction': np.random.uniform(*NORMAL_RANGES['direction']),
        'signal_strength': np.random.uniform(*NORMAL_RANGES['signal_strength']),
        'distance_from_base': np.random.uniform(*NORMAL_RANGES['distance_from_base']),
        'flight_time': np.random.uniform(*NORMAL_RANGES['flight_time']),
        'battery_level': np.random.uniform(*NORMAL_RANGES['battery_level']),
        'temperature': np.random.uniform(*NORMAL_RANGES['temperature']),
        'vibration': np.random.uniform(*NORMAL_RANGES['vibration']),
        'gps_accuracy': np.random.uniform(*NORMAL_RANGES['gps_accuracy']),
        'threat_type': 'normal',
        'is_threat': 0
    }


def generate_attack_sample(attack_type):
    """Generate a single attack sample with specific signatures."""
    # Start with normal baseline
    sample = generate_normal_sample()
    
    # Apply attack signature
    if attack_type in ATTACK_SIGNATURES:
        signature = ATTACK_SIGNATURES[attack_type]
        for feature, (min_val, max_val) in signature.items():
            sample[feature] = np.random.uniform(min_val, max_val)
    
    # Update labels
    sample['threat_type'] = attack_type
    sample['is_threat'] = 1
    
    return sample


def generate_dataset(total_samples=DATASET_SIZE, output_file='data/uav_security_dataset.csv'):
    """
    Generate complete UAV security dataset.
    
    Args:
        total_samples: Total number of samples to generate
        output_file: Output CSV file path
    
    Returns:
        DataFrame with generated dataset
    """
    print("=" * 70)
    print("🚁 UAV SECURITY DATASET GENERATOR")
    print("=" * 70)
    print(f"\n📊 Configuration:")
    print(f"   Total Samples: {total_samples:,}")
    print(f"   Attack Ratio: {ATTACK_RATIO * 100:.1f}%")
    print(f"   Random Seed: {RANDOM_SEED}")
    print(f"\n🎯 Attack Types Distribution:")
    
    np.random.seed(RANDOM_SEED)
    
    # Calculate samples per attack type
    samples_per_type = {}
    for attack_type, ratio in ATTACK_TYPES.items():
        count = int(total_samples * ratio)
        samples_per_type[attack_type] = count
        print(f"   {attack_type:25} {count:6,} ({ratio * 100:5.1f}%)")
    
    print(f"\n⚙️  Generating samples...")
    
    # Generate samples
    dataset = []
    
    for attack_type, count in samples_per_type.items():
        print(f"   Generating {count:,} {attack_type} samples...", end=" ")
        
        for _ in range(count):
            if attack_type == 'normal':
                sample = generate_normal_sample()
            else:
                sample = generate_attack_sample(attack_type)
            dataset.append(sample)
        
        print("✓")
    
    # Create DataFrame
    df = pd.DataFrame(dataset)
    
    # Shuffle dataset
    print(f"\n🔀 Shuffling dataset...")
    df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
    
    # Add timestamp simulation (for realism)
    print(f"📅 Adding timestamps...")
    base_time = pd.Timestamp.now() - pd.Timedelta(days=30)
    df['timestamp'] = [base_time + pd.Timedelta(seconds=i*60) for i in range(len(df))]
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save to CSV
    print(f"\n💾 Saving dataset to {output_file}...")
    df.to_csv(output_file, index=False)
    
    # Display statistics
    print(f"\n" + "=" * 70)
    print("✅ DATASET GENERATION COMPLETE!")
    print("=" * 70)
    print(f"\n📈 Dataset Statistics:")
    print(f"   Total Samples: {len(df):,}")
    print(f"   Features: {len(df.columns) - 3}")  # Exclude threat_type, is_threat, timestamp
    print(f"   File Size: {os.path.getsize(output_file) / 1024:.2f} KB")
    
    print(f"\n🏷️  Label Distribution:")
    print(df['threat_type'].value_counts().to_string())
    
    print(f"\n📊 Feature Summary (first 10 features):")
    print(df.describe().iloc[:, :10].to_string())
    
    print(f"\n🎉 Ready for model training!")
    print(f"   Use: python scripts/train_models.py")
    
    return df


if __name__ == "__main__":
    # Generate dataset
    df = generate_dataset()
    
    # Optional: Display sample rows
    print(f"\n📋 Sample Data (first 5 rows):")
    print(df.head().to_string())
