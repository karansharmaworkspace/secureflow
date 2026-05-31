package com.logiclegion.zombie;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

public class ApiCallRecord {
    private static final ObjectMapper MAPPER = new ObjectMapper();

    public double ts;
    public String method;
    public String path;
    public int status;
    public String userAgent;
    public String host;
    public String referrer;
    public long responseSize;
    public String sourceIp;
    public String authHeader;

    public static ApiCallRecord fromJson(String json) {
        try {
            return MAPPER.readValue(json, ApiCallRecord.class);
        } catch (JsonProcessingException e) {
            return null;
        }
    }

    public String endpointKey() {
        return host + "|" + method + "|" + path;
    }

    public boolean hasAuth() {
        return authHeader != null && !authHeader.isEmpty();
    }

    public boolean isKnownMonitor() {
        if (userAgent == null) return false;
        String ua = userAgent.toLowerCase();
        return ua.contains("prometheus") ||
               ua.contains("kube-probe") ||
               ua.contains("datadog agent") ||
               ua.contains("healthcheck") ||
               ua.contains("uptimerobot");
    }
}
