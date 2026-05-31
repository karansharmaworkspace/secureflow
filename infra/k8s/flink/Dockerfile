FROM flink:1.19.0-scala_2.12-java11

COPY target/zombie-feature-job-1.0.0.jar /opt/flink/usrlib/zombie-feature-job.jar

RUN mkdir -p /opt/flink/checkpoints /opt/flink/savepoints

ENTRYPOINT ["/docker-entrypoint.sh"]
