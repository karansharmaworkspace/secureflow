package com.logiclegion.zombie;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class FeatureAggregatorTest {

    @Test
    void testCreateAccumulator() {
        FeatureComputationJob.FeatureAggregator aggregator = 
            new FeatureComputationJob.FeatureAggregator();
        
        EndpointFeatures result = aggregator.createAccumulator();
        
        assertNotNull(result);
        assertEquals(0, result.totalCalls);
        assertEquals(0, result.syntheticCalls);
        assertEquals(0, result.realCalls);
        assertEquals(0, result.uniqueUserAgents); // Defaults to 0 (Java int default)
        assertEquals(0, result.uniqueSourceIps);  // Defaults to 0 (Java int default)
        assertEquals(0, result.authTokenCount);
        assertEquals(0, result.noAuthCount);
        assertEquals(0, result.count2xx);
        assertEquals(0, result.count4xx);
        assertEquals(0, result.count5xx);
        assertFalse(result.isOneHundredPercentSynthetic);
    }

    @Test
    void testAddRealCall() {
        FeatureComputationJob.FeatureAggregator aggregator = 
            new FeatureComputationJob.FeatureAggregator();
        EndpointFeatures acc = aggregator.createAccumulator();
        
        ApiCallRecord record = new ApiCallRecord();
        record.ts = 1234567890.0;
        record.method = "GET";
        record.path = "/api/test";
        record.host = "test-host";
        record.status = 200;
        record.responseSize = 1024;
        record.userAgent = "Mozilla/5.0";
        record.sourceIp = "192.168.1.1";
        record.authHeader = "Bearer token123";
        
        EndpointFeatures result = aggregator.add(record, acc);
        
        assertEquals(1, result.totalCalls);
        assertEquals(0, result.syntheticCalls);
        assertEquals(1, result.realCalls);
        assertEquals(1, result.authTokenCount);
        assertEquals(0, result.noAuthCount);
        assertEquals(1, result.count2xx);
        assertEquals(0, result.count4xx);
        assertEquals(0, result.count5xx);
    }

    @Test
    void testAddSyntheticCall() {
        FeatureComputationJob.FeatureAggregator aggregator = 
            new FeatureComputationJob.FeatureAggregator();
        EndpointFeatures acc = aggregator.createAccumulator();
        
        ApiCallRecord record = new ApiCallRecord();
        record.ts = 1234567890.0;
        record.method = "GET";
        record.path = "/api/test";
        record.host = "test-host";
        record.status = 200;
        record.responseSize = 1024;
        record.userAgent = "Prometheus/2.0";
        record.sourceIp = "192.168.1.1";
        record.authHeader = "Bearer token123";
        
        EndpointFeatures result = aggregator.add(record, acc);
        
        assertEquals(1, result.totalCalls);
        assertEquals(1, result.syntheticCalls);
        assertEquals(0, result.realCalls);
        assertEquals(1, result.authTokenCount);
        assertEquals(0, result.noAuthCount);
        assertEquals(1, result.count2xx);
        assertEquals(0, result.count4xx);
        assertEquals(0, result.count5xx);
    }

    @Test
    void testAddCallWithoutAuth() {
        FeatureComputationJob.FeatureAggregator aggregator = 
            new FeatureComputationJob.FeatureAggregator();
        EndpointFeatures acc = aggregator.createAccumulator();
        
        ApiCallRecord record = new ApiCallRecord();
        record.ts = 1234567890.0;
        record.method = "GET";
        record.path = "/api/test";
        record.host = "test-host";
        record.status = 404;
        record.responseSize = 512;
        record.userAgent = "curl/7.68.0";
        record.sourceIp = "10.0.0.1";
        record.authHeader = null;
        
        EndpointFeatures result = aggregator.add(record, acc);
        
        assertEquals(1, result.totalCalls);
        assertEquals(0, result.syntheticCalls);
        assertEquals(1, result.realCalls);
        assertEquals(0, result.authTokenCount);
        assertEquals(1, result.noAuthCount);
        assertEquals(0, result.count2xx);
        assertEquals(1, result.count4xx);
        assertEquals(0, result.count5xx);
    }

    @Test
    void testGetResultAllSynthetic() {
        FeatureComputationJob.FeatureAggregator aggregator = 
            new FeatureComputationJob.FeatureAggregator();
        EndpointFeatures acc = aggregator.createAccumulator();
        
        acc.totalCalls = 100;
        acc.syntheticCalls = 100;
        acc.realCalls = 0;
        
        EndpointFeatures result = aggregator.getResult(acc);
        
        assertTrue(result.isOneHundredPercentSynthetic);
    }

    @Test
    void testGetResultNotSynthetic() {
        FeatureComputationJob.FeatureAggregator aggregator = 
            new FeatureComputationJob.FeatureAggregator();
        EndpointFeatures acc = aggregator.createAccumulator();
        
        acc.totalCalls = 100;
        acc.syntheticCalls = 50;
        acc.realCalls = 50;
        
        EndpointFeatures result = aggregator.getResult(acc);
        
        assertFalse(result.isOneHundredPercentSynthetic);
    }

    @Test
    void testMerge() {
        FeatureComputationJob.FeatureAggregator aggregator = 
            new FeatureComputationJob.FeatureAggregator();
        
        EndpointFeatures a = new EndpointFeatures();
        a.endpointKey = "endpoint1";
        a.totalCalls = 50;
        a.syntheticCalls = 30;
        a.realCalls = 20;
        a.authTokenCount = 15;
        a.noAuthCount = 5;
        a.count2xx = 40;
        a.count4xx = 8;
        a.count5xx = 2;
        
        EndpointFeatures b = new EndpointFeatures();
        b.endpointKey = "endpoint1";
        b.totalCalls = 30;
        b.syntheticCalls = 20;
        b.realCalls = 10;
        b.authTokenCount = 10;
        b.noAuthCount = 0;
        b.count2xx = 25;
        b.count4xx = 4;
        b.count5xx = 1;
        
        EndpointFeatures merged = aggregator.merge(a, b);
        
        assertNull(merged.endpointKey);
        assertEquals(80, merged.totalCalls);
        assertEquals(50, merged.syntheticCalls);
        assertEquals(30, merged.realCalls);
        assertEquals(25, merged.authTokenCount);
        assertEquals(5, merged.noAuthCount);
        assertEquals(65, merged.count2xx);
        assertEquals(12, merged.count4xx);
        assertEquals(3, merged.count5xx);
        assertFalse(merged.isOneHundredPercentSynthetic);
    }
}