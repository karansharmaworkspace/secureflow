# Zombie Detection Flink Job

Main Apache Flink job implementation for real-time feature computation. Processes streaming API traffic data from Kafka and computes endpoint features used by the XGBoost classifier for zombie detection.

## Purpose

This Flink job consumes network traffic events from Kafka topics, computes rolling feature windows per endpoint (call volume, user agent diversity, response patterns, timing characteristics), and outputs feature vectors for ML classification.
