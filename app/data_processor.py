import pandas as pd
import numpy as np
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "sensor_data.csv")

# Expected ranges from data_dictionary.md
RANGES = {
    "lat": (32.65, 32.72),
    "lon": (-117.20, -117.14),
    "depth_m": (0.0, 15.0),
    "water_temp_c": (12.0, 25.0),
    "dissolved_oxygen_mgl": (4.0, 12.0),
    "ph": (7.5, 8.5),
    "turbidity_ntu": (0.0, 50.0),
    "salinity_ppt": (30.0, 36.0),
    "battery_pct": (0.0, 100.0)
}

class Pipeline:
    def __init__(self):
        self.df = None
        self.anomalies = []
    
    def load_data(self):
        self.df = pd.read_csv(DATA_FILE)
        # Handle artificially corrupted timestamp +00:00Z
        self.df['timestamp'] = self.df['timestamp'].str.replace('+00:00Z', 'Z', regex=False)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], format='mixed', utc=True)
        
        # Sort by timestamp
        self.df = self.df.sort_values("timestamp").reset_index(drop=True)
        
        self._detect_anomalies()
        
    def _detect_anomalies(self):
        anomalies_list = []
        
        # Method 1: Range Validation
        for col, (min_val, max_val) in RANGES.items():
            if col in self.df.columns:
                out_of_bounds = self.df[(self.df[col] < min_val) | (self.df[col] > max_val)]
                for idx, row in out_of_bounds.iterrows():
                    # Check if the value is NaN to avoid false positives on missing data
                    if pd.isna(row[col]):
                        continue
                        
                    anomalies_list.append({
                        "timestamp": row["timestamp"].isoformat(),
                        "sensor": col,
                        "value": row[col],
                        "issue": f"Out of valid range ({min_val} to {max_val})",
                        "method": "Range Validation",
                        "row_index": int(idx)
                    })
                    
        # Method 2: Rolling Window Deviation (Z-Score)
        numeric_cols = ["water_temp_c", "dissolved_oxygen_mgl", "ph", "turbidity_ntu", "salinity_ppt", "depth_m"]
        window_size = 6 # 1 hour (6 readings of 10 mins)
        threshold = 3.2 # Z-Score threshold
        
        for col in numeric_cols:
            if col in self.df.columns:
                rolling_mean = self.df[col].rolling(window=window_size, center=True, min_periods=3).mean()
                rolling_std = self.df[col].rolling(window=window_size, center=True, min_periods=3).std()
                
                # Replace zero std with np.nan to avoid division by zero
                rolling_std = rolling_std.replace(0, np.nan)
                
                z_scores = (self.df[col] - rolling_mean) / rolling_std
                
                # Handle potential divide by nan issues
                z_scores = z_scores.fillna(0)
                
                spikes = self.df[z_scores.abs() > threshold]
                
                for idx, row in spikes.iterrows():
                    # Only add if not already flagged by range validation
                    already_flagged = any((a["row_index"] == idx and a["sensor"] == col) for a in anomalies_list)
                    if not already_flagged:
                        anomalies_list.append({
                            "timestamp": row["timestamp"].isoformat(),
                            "sensor": col,
                            "value": row[col],
                            "issue": f"Statistical spike (z-score: {z_scores[idx]:.2f})",
                            "method": "Rolling Z-Score",
                            "row_index": int(idx)
                        })
                        
        self.anomalies = anomalies_list
        
    def get_data(self, start=None, end=None):
        df_subset = self.df
        if start:
            df_subset = df_subset[df_subset['timestamp'] >= pd.to_datetime(start, utc=True)]
        if end:
            df_subset = df_subset[df_subset['timestamp'] <= pd.to_datetime(end, utc=True)]
            
        # Convert timestamp to string before returning
        result = df_subset.copy()
        result['timestamp'] = result['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Replace NaN with None for JSON serialization
        result = result.replace({np.nan: None})
        return result.to_dict(orient="records")
        
    def get_anomalies(self):
        return self.anomalies
        
    def get_summary(self):
        numeric_cols = ["water_temp_c", "dissolved_oxygen_mgl", "ph", "turbidity_ntu", "salinity_ppt", "depth_m", "lat", "lon", "battery_pct"]
        stats = {}
        for col in numeric_cols:
            if col in self.df.columns:
                # dropna for basic stats to avoid issues
                clean_col = self.df[col].dropna()
                stats[col] = {
                    "min": float(clean_col.min()) if len(clean_col) > 0 else None,
                    "max": float(clean_col.max()) if len(clean_col) > 0 else None,
                    "mean": float(clean_col.mean()) if len(clean_col) > 0 else None,
                    "std": float(clean_col.std()) if len(clean_col) > 0 else None
                }
                
        # Count anomalies by method
        by_method = {}
        for a in self.anomalies:
            method = a["method"]
            by_method[method] = by_method.get(method, 0) + 1
            
        # Count anomaly by sensor
        by_sensor = {}
        for a in self.anomalies:
            sensor = a["sensor"]
            by_sensor[sensor] = by_sensor.get(sensor, 0) + 1
            
        return {
            "total_rows": len(self.df),
            "total_anomalies": len(self.anomalies),
            "stats": stats,
            "anomalies_by_method": by_method,
            "anomalies_by_sensor": by_sensor
        }

pipeline = Pipeline()
