import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from scipy import stats
from dataclasses import dataclass

@dataclass
class TimeSeriesPoint:
    timestamp: datetime
    value: float
    metadata: Optional[Dict] = None

class TimeSeriesAnalyzer:
    def __init__(self, window_size: int = 7):
        self.window_size = window_size
        self.data_points: List[TimeSeriesPoint] = []

    def add_data_point(self, value: float, timestamp: Optional[datetime] = None, metadata: Optional[Dict] = None):
        if timestamp is None:
            timestamp = datetime.now()
        self.data_points.append(TimeSeriesPoint(timestamp, value, metadata))
        self.data_points.sort(key=lambda x: x.timestamp)

    def get_trend(self, days: int = 30) -> Dict:
        if len(self.data_points) < 2:
            return {"trend": "insufficient_data", "slope": 0.0, "confidence": 0.0}

        cutoff_date = datetime.now() - timedelta(days=days)
        recent_points = [(p.timestamp.timestamp(), p.value) for p in self.data_points 
                        if p.timestamp > cutoff_date]

        if not recent_points:
            return {"trend": "no_recent_data", "slope": 0.0, "confidence": 0.0}

        x, y = zip(*recent_points)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        trend_direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        confidence = abs(r_value)

        return {
            "trend": trend_direction,
            "slope": slope,
            "confidence": confidence,
            "p_value": p_value
        }

    def detect_anomalies(self, z_threshold: float = 2.0) -> List[TimeSeriesPoint]:
        if len(self.data_points) < self.window_size:
            return []

        values = [p.value for p in self.data_points]
        z_scores = stats.zscore(values)
        anomalies = []

        for i, (point, z_score) in enumerate(zip(self.data_points, z_scores)):
            if abs(z_score) > z_threshold:
                anomalies.append(point)

        return anomalies

    def forecast_next_value(self, horizon_days: int = 7) -> Dict:
        if len(self.data_points) < self.window_size:
            return {"forecast": None, "confidence_interval": None}

        recent_values = [p.value for p in self.data_points[-self.window_size:]]
        trend = np.polyfit(range(len(recent_values)), recent_values, 1)
        forecast = np.poly1d(trend)(len(recent_values) + horizon_days)

        # Calculate confidence interval
        std_dev = np.std(recent_values)
        confidence_interval = (forecast - 1.96 * std_dev, forecast + 1.96 * std_dev)

        return {
            "forecast": float(forecast),
            "confidence_interval": {
                "lower": float(confidence_interval[0]),
                "upper": float(confidence_interval[1])
            }
        }

    def get_summary_statistics(self) -> Dict:
        if not self.data_points:
            return {}

        values = [p.value for p in self.data_points]
        return {
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "std_dev": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "total_points": len(values)
        }

    def get_seasonal_patterns(self, period: int = 7) -> Dict:
        if len(self.data_points) < period * 2:
            return {"patterns": "insufficient_data"}

        values = np.array([p.value for p in self.data_points])
        seasonal_means = []
        seasonal_stds = []

        for i in range(period):
            seasonal_data = values[i::period]
            if len(seasonal_data) > 0:
                seasonal_means.append(float(np.mean(seasonal_data)))
                seasonal_stds.append(float(np.std(seasonal_data)))

        return {
            "seasonal_means": seasonal_means,
            "seasonal_stds": seasonal_stds,
            "period": period
        }