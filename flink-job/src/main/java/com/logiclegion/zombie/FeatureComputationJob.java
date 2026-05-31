package com.logiclegion.zombie;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;

import java.time.Duration;
import java.util.*;

public class FeatureComputationJob {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    public static void main(String[] args) throws Exception {
        String bootstrapServers = System.getenv().getOrDefault("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092");
        String rawTopic = System.getenv().getOrDefault("KAFKA_RAW_TOPIC", "raw-api-calls");
        String outputTopic = System.getenv().getOrDefault("KAFKA_OUTPUT_TOPIC", "enriched-features");

        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.enableCheckpointing(60000);
        env.getCheckpointConfig().setCheckpointTimeout(120000);

        KafkaSource<String> source = KafkaSource.<String>builder()
            .setBootstrapServers(bootstrapServers)
            .setTopics(rawTopic)
            .setGroupId("flink-feature-job")
            .setValueOnlyDeserializer(new SimpleStringSchema())
            .build();

        DataStream<ApiCallRecord> calls = env
            .fromSource(source, WatermarkStrategy.noWatermarks(), "kafka-source")
            .map(json -> ApiCallRecord.fromJson(json))
            .filter(record -> record != null)
            .assignTimestampsAndWatermarks(
                WatermarkStrategy.<ApiCallRecord>forBoundedOutOfOrderness(Duration.ofSeconds(10))
                    .withTimestampAssigner((record, ts) -> (long) (record.ts * 1000))
            );

        DataStream<String> features7d = calls
            .keyBy(ApiCallRecord::endpointKey)
            .window(SlidingEventTimeWindows.of(Time.days(7), Time.hours(1)))
            .aggregate(new FeatureAggregator())
            .map(features -> MAPPER.writeValueAsString(features.toMap()));

        DataStream<String> features30d = calls
            .keyBy(ApiCallRecord::endpointKey)
            .window(SlidingEventTimeWindows.of(Time.days(30), Time.hours(6)))
            .aggregate(new FeatureAggregator())
            .map(features -> MAPPER.writeValueAsString(features.toMap()));

        DataStream<String> features90d = calls
            .keyBy(ApiCallRecord::endpointKey)
            .window(SlidingEventTimeWindows.of(Time.days(90), Time.days(1)))
            .aggregate(new FeatureAggregator())
            .map(features -> MAPPER.writeValueAsString(features.toMap()));

        DataStream<String> allFeatures = features7d.union(features30d, features90d);

        KafkaSink<String> sink = KafkaSink.<String>builder()
            .setBootstrapServers(bootstrapServers)
            .setRecordSerializer(KafkaRecordSerializationSchema.builder()
                .setTopic(outputTopic)
                .setValueSerializationSchema(new SimpleStringSchema())
                .build())
            .build();

        allFeatures.sinkTo(sink);

        env.execute("zombie-feature-computation");
    }

    public static class FeatureAggregator implements AggregateFunction<ApiCallRecord, EndpointFeatures, EndpointFeatures> {

        @Override
        public EndpointFeatures createAccumulator() {
            return new EndpointFeatures();
        }

        @Override
        public EndpointFeatures add(ApiCallRecord record, EndpointFeatures acc) {
            acc.endpointKey = record.endpointKey();
            acc.totalCalls++;

            if (record.isKnownMonitor()) {
                acc.syntheticCalls++;
            } else {
                acc.realCalls++;
            }

            acc.uniqueUserAgents = -1;
            acc.uniqueSourceIps = -1;

            if (record.hasAuth()) acc.authTokenCount++;
            else acc.noAuthCount++;

            if (record.status >= 200 && record.status < 300) acc.count2xx++;
            else if (record.status >= 400 && record.status < 500) acc.count4xx++;
            else if (record.status >= 500) acc.count5xx++;

            return acc;
        }

        @Override
        public EndpointFeatures getResult(EndpointFeatures acc) {
            acc.isOneHundredPercentSynthetic = acc.syntheticCalls > 0 && acc.realCalls == 0;
            return acc;
        }

        @Override
        public EndpointFeatures merge(EndpointFeatures a, EndpointFeatures b) {
            EndpointFeatures merged = new EndpointFeatures();
            merged.totalCalls = a.totalCalls + b.totalCalls;
            merged.syntheticCalls = a.syntheticCalls + b.syntheticCalls;
            merged.realCalls = a.realCalls + b.realCalls;
            merged.authTokenCount = a.authTokenCount + b.authTokenCount;
            merged.noAuthCount = a.noAuthCount + b.noAuthCount;
            merged.count2xx = a.count2xx + b.count2xx;
            merged.count4xx = a.count4xx + b.count4xx;
            merged.count5xx = a.count5xx + b.count5xx;
            merged.isOneHundredPercentSynthetic = merged.syntheticCalls > 0 && merged.realCalls == 0;
            return merged;
        }
    }
}
