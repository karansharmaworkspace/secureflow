package com.logiclegion.zombie;

import java.util.HashMap;
import java.util.Map;

public class EndpointFeatures {
    public String endpointKey;
    public long windowStart;
    public long windowEnd;

    public long totalCalls;
    public long syntheticCalls;
    public long realCalls;
    public long daysSinceLastRealCall;

    public int uniqueUserAgents;
    public int uniqueSourceIps;
    public int authTokenCount;
    public int noAuthCount;

    public int count2xx;
    public int count4xx;
    public int count5xx;

    public double responseSizeMean;
    public double responseSizeStddev;

    public double interarrivalMeanMs;
    public double interarrivalStddevMs;

    public int uniqueHoursOfDay;

    public boolean isOneHundredPercentSynthetic;

    public Map<String, Object> toMap() {
        Map<String, Object> m = new HashMap<>();
        m.put("endpoint_key", endpointKey);
        m.put("window_start", windowStart);
        m.put("window_end", windowEnd);
        m.put("total_calls", totalCalls);
        m.put("synthetic_calls", syntheticCalls);
        m.put("real_calls", realCalls);
        m.put("days_since_last_real_call", daysSinceLastRealCall);
        m.put("unique_user_agents", uniqueUserAgents);
        m.put("unique_source_ips", uniqueSourceIps);
        m.put("auth_ratio", totalCalls > 0 ? (double) authTokenCount / totalCalls : 0);
        m.put("ratio_2xx", totalCalls > 0 ? (double) count2xx / totalCalls : 0);
        m.put("ratio_4xx", totalCalls > 0 ? (double) count4xx / totalCalls : 0);
        m.put("ratio_5xx", totalCalls > 0 ? (double) count5xx / totalCalls : 0);
        m.put("response_size_mean", responseSizeMean);
        m.put("response_size_stddev", responseSizeStddev);
        m.put("interarrival_mean_ms", interarrivalMeanMs);
        m.put("interarrival_stddev_ms", interarrivalStddevMs);
        m.put("unique_hours_of_day", uniqueHoursOfDay);
        m.put("is_100pct_synthetic", isOneHundredPercentSynthetic);
        return m;
    }
}
