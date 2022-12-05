# Python Plugin Performance Copilot

This plugin runs sar and pmlogger, collects data for the given amount of time,
and then generates a JSON output file of the results.

Build the container:
```
docker build . -t arcaflow-metadata-plugin
```

Run with the provided example input:
```
cat pcp_example.py | docker run -i --rm arcaflow-metadata-plugin -f -
```
