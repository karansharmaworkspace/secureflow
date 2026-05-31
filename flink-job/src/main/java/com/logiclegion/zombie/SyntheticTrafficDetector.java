package com.logiclegion.zombie;

import java.util.*;

public class SyntheticTrafficDetector {

    private static final Set<String> MONITOR_USER_AGENTS = Set.of(
        "prometheus", "kube-probe", "datadog agent",
        "healthcheck", "uptimerobot", "pingdom",
        "grafana", "newrelic", "appdynamics"
    );

    public static DetectionResult detect(List<ApiCallRecord> calls) {
        if (calls.isEmpty()) return new DetectionResult(false, 0, "no data");

        int signalsTriggered = 0;
        int totalSignals = 7;

        if (isRegularInterval(calls)) signalsTriggered++;
        if (isMonitorUserAgent(calls)) signalsTriggered++;
        if (isLowEntropyPayload(calls)) signalsTriggered++;
        if (isSingleSourceIp(calls)) signalsTriggered++;
        if (isAlways200(calls)) signalsTriggered++;
        if (isTimeClustered(calls)) signalsTriggered++;
        if (isExactlyPeriodic(calls)) signalsTriggered++;

        double confidence = (double) signalsTriggered / totalSignals;
        boolean isSynthetic = confidence >= 0.6;
        String reason = String.format("%d/%d synthetic signals (%.0f%%)", signalsTriggered, totalSignals, confidence * 100);

        return new DetectionResult(isSynthetic, confidence, reason);
    }

    private static boolean isRegularInterval(List<ApiCallRecord> calls) {
        if (calls.size() < 3) return false;
        List<Long> intervals = new ArrayList<>();
        for (int i = 1; i < calls.size(); i++) {
            intervals.add((long) (calls.get(i).ts - calls.get(i-1).ts));
        }
        double mean = intervals.stream().mapToLong(Long::longValue).average().orElse(0);
        double variance = intervals.stream().mapToDouble(i -> Math.pow(i - mean, 2)).average().orElse(0);
        double stddev = Math.sqrt(variance);
        return stddev < 1.0;
    }

    private static boolean isMonitorUserAgent(List<ApiCallRecord> calls) {
        return calls.stream().allMatch(c -> {
            if (c.userAgent == null) return false;
            String ua = c.userAgent.toLowerCase();
            return MONITOR_USER_AGENTS.stream().anyMatch(ua::contains);
        });
    }

    private static boolean isLowEntropyPayload(List<ApiCallRecord> calls) {
        if (calls.size() < 2) return false;
        Set<Long> sizes = new HashSet<>();
        for (ApiCallRecord c : calls) sizes.add(c.responseSize);
        return sizes.size() == 1;
    }

    private static boolean isSingleSourceIp(List<ApiCallRecord> calls) {
        Set<String> ips = new HashSet<>();
        for (ApiCallRecord c : calls) ips.add(c.sourceIp);
        return ips.size() == 1;
    }

    private static boolean isAlways200(List<ApiCallRecord> calls) {
        return calls.stream().allMatch(c -> c.status == 200);
    }

    private static boolean isTimeClustered(List<ApiCallRecord> calls) {
        Set<Integer> hours = new HashSet<>();
        for (ApiCallRecord c : calls) {
            Date d = new Date((long) c.ts * 1000);
            hours.add(d.getHours());
        }
        return hours.size() <= 2;
    }

    private static boolean isExactlyPeriodic(List<ApiCallRecord> calls) {
        if (calls.size() < 4) return false;
        List<Long> intervals = new ArrayList<>();
        for (int i = 1; i < calls.size(); i++) {
            intervals.add((long) (calls.get(i).ts - calls.get(i-1).ts));
        }
        long first = intervals.get(0);
        return intervals.stream().allMatch(i -> Math.abs(i - first) <= 1);
    }

    public static class DetectionResult {
        public final boolean isSynthetic;
        public final double confidence;
        public final String reason;

        public DetectionResult(boolean isSynthetic, double confidence, String reason) {
            this.isSynthetic = isSynthetic;
            this.confidence = confidence;
            this.reason = reason;
        }
    }
}
