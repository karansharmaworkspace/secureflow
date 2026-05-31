FEATURE_COLUMNS = [
    "total_calls",
    "synthetic_calls",
    "real_calls",
    "days_since_last_real_call",
    "unique_user_agents",
    "unique_source_ips",
    "auth_ratio",
    "ratio_2xx",
    "ratio_4xx",
    "ratio_5xx",
    "response_size_mean",
    "response_size_stddev",
    "interarrival_mean_ms",
    "interarrival_stddev_ms",
    "unique_hours_of_day",
    "is_100pct_synthetic",
]

TARGET_COLUMN = "is_zombie"
