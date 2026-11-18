# message-queues-and-brokers gaps (pass b16)

- Dead letter queue (only two Singh sentences; folded into "Message queue features")
- Message ordering guarantees (FIFO vs unordered queues, per-partition ordering)
- Idempotent consumer / deduplication (Singh idempotency chapter exists)
- Amazon Simple Queue Service
- Advanced Message Queuing Protocol (own article)
- MQTT (own article)
- Message-oriented middleware
- Point-to-point messaging
- RabbitMQ exchanges and routing (direct, fanout, topic)
- Apache ActiveMQ, NATS
- Observer pattern
- Task queue
- types-of-message-queue.md: besides the selection criteria it is learning advice (no entry)
- Wikipedia Message broker "Real-time semantics" (CORBA) not drafted: niche

# gaps (message-queues-and-brokers, gap-fill chunks 03-04)
- Job queue: a batch-scheduler concept (priority, execution time, resources); folded into the Batch processing entry in event-streaming-and-kafka, no entry of its own
- AMQP and MQTT history (JPMorgan, iMatix, ZeroMQ split, IBM/OASIS) and ActiveMQ/Flink-style release and benchmark trivia: skipped as business history
- MQTT-SN and MQTT 5.0 details beyond a mention (reason codes, shared subscriptions, topic alias): only in mention_sent_ids
- RabbitMQ exchanges and routing (direct, fanout, topic): still no sentences; suggest the RabbitMQ docs or Wikipedia "Message broker" routing pages
- Choosing a message queue: assembled from per-product facts; no source gives an explicit decision guide (queue versus stream versus pub/sub by workload); suggest official docs for SQS, RabbitMQ, Kafka comparisons
- Amazon SQS standard versus FIFO queue types, visibility timeout and retention: not in the Wikipedia page; suggest AWS SQS developer guide if the licence allows
- Point-to-point messaging and Fan-out (software): only a sentence each; suggest "Fan-out (software)"
