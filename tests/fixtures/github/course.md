# System Design Course

Intro text before the first chapter.

# Load Balancing

A load balancer spreads requests across servers so that no single server is overloaded. See [caching](#caching) and the [CDN chapter](#content-delivery-network-cdn).

## Types

Layer 4 balancers route by IP and port while layer 7 balancers read the request.

```sh
# not a heading
echo "# also not a heading"
```

# Caching

A cache stores copies of data so that later requests are served faster. Compare with [load balancing](#load-balancing).

## Eviction policies

Least recently used evicts the entry that was read longest ago.

# Caching

A second chapter with the same title gets a numbered anchor, just as GitHub numbers it.

# Content Delivery Network (CDN)

A CDN serves content from servers close to the reader.
