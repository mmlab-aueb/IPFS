# Visualization of IPFS DHT queries
These scripts enable the visualization of the connections timeline during an IPFS DHT query.

## Use instructions

### Step 1. Start the IPFS daemon on your machine

Assuming you have already installed IPFS, you start the IPFS daemon by executing:

```bash
ipfs daemon
```

### Step 2. Run an IPFS DHT query

To run an IPFS DHT query, you normally execute:

```bash
ipfs dht query <CID>
```

In order to visualize the connections opened and used during a query, you should also provide the verbose flag (-v) and redirect the standard output into a file, say query.log. Here's an example, including a sample CID:

```bash
ipfs dht query -v QmefYbmED9E1cw3NEqtxKDmVrzk3Z351ZDgwzwKdQ4Ajbj > query.log
```



### Step 3. Parse the query log

To parse the log produced in the previous step, you should execute:

```bash
cat query.log | ./log2plot.py > DATA
```

This will parse the query log, and will output visualization data to be consumed by gnuplot. We redirect that output into a file called DATA, which the gnuplot script expects to find.

### Step 4. Visualize the data

At this final step, you execute [gnuplot](http://www.gnuplot.info/) to produce the visualization. You execute:

```bash
gnuplot graph.gpi
```

This will pop up a window with the timeline of connections that took place during the query.

You may optionally click on the top left button in the visualization window to export the plot as a PDF or image.


