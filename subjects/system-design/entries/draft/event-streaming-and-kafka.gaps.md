# event-streaming-and-kafka gaps (pass b16)

- Event streaming (platform concept; only Singh's brokers-vs-streaming comparison mentions it)
- Event store
- Kafka Connect (three sentences only; folded into "Apache Kafka")
- Debezium
- Kafka partitions, replication and in-sync replicas (own documentation page)
- Kafka log compaction and retention
- Kafka exactly-once semantics and idempotent producer
- Consumer lag
- Apache Flink, Apache Spark Streaming (own pages; only one-line mentions here)
- Batch processing versus stream processing (4 sentences on a ByteByteGo trade-offs page; folded into "Stream processing")
- Slowly changing dimension
- Stream processing page is mostly GPU and hardware history (Stanford Imagine, Cell, Amiga blitter, CUDA); not drafted

# gaps (event-streaming-and-kafka, gap-fill chunks 03-04)
- Lambda architecture and Kappa architecture: named by Spark and Flink pages, no page crawled; suggest Wikipedia "Lambda architecture"
- Windowing, event time and watermarks in stream processing: Flink says it supports event-time processing but no sentence explains it; suggest a Flink or Beam doc page
- Apache Storm, Apache Samza, Amazon Kinesis as entries: only named in passing
- Spark history, versions, Spark Connect, PySpark, MLlib algorithm lists, GraphX trivia, Flink Forward conference and Stratosphere history: skipped as product trivia
- Batch processing history (mainframes, JCL, z/OS) skipped; Unix cron and at only mentioned; suggest "Cron" if scheduled jobs belong in the course
- Complex event processing: business process management and operational intelligence sections skipped
