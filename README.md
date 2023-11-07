# Performance Copilot (PCP) Plugin

This plugin runs sar and pmlogger, collects data until cancelled,
and then generates a structured output of the results.

***Note:** This plugin runs indefinitely until explicitly cancelled.
When used as a stand-alone plugin, the data collection can be stopped
with `Ctrl-c`. When used in an Arcaflow workflow, the `stop_if`
option should be used to send the `cancel` signal to the plugin based
on the status of another plugin.*

Workflow example snippet with `stop_if`:
```yaml
steps:
  pcp:
    plugin: quay.io/arcalot/arcaflow-plugin-pcp:latest
    step: start-pcp
    input: !expr $.input.pcp_params
    stop_if: !expr $.steps.sysbench.outputs
  sysbench:
    plugin: quay.io/arcalot/arcaflow-plugin-sysbench:latest
    step: sysbenchcpu
    input: !expr $.input.sysbench_params
```

## Using the plugin
Build the container:
```
docker build . -t arcaflow-plugin-pcp
```

Run with the provided example input:
```
cat configs/pcp_example.yaml | docker run -i --rm arcaflow-plugin-pcp -f -
```
# Autogenerated Input/Output Documentation by Arcaflow-Docsgen Below

<!-- Autogenerated documentation by arcaflow-docsgen -->
## Start PCP (`start-pcp`)

Start the PCP data logging tools

### Input

<table><tbody>
<tr><th>Type:</th><td><code>scope</code></td><tr><th>Root object:</th><td>PcpInputParams</td></tr>
<tr><th>Properties</th><td><details><summary>pmlogger_interval (<code>float</code>)</summary>
                <table><tbody><tr><th>Name:</th><td>pmlogger logging interval</td></tr><tr><th>Description:</th><td>The logging interval in seconds (float) used by pmlogger for data collection</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>float</code></td><tr><th>Units:</th><td>nanoseconds</td></tr>
</tbody></table>
            </details><details><summary>timeout (<code>int</code>)</summary>
                <table><tbody><tr><th>Name:</th><td>pmlogger timeout seconds</td></tr><tr><th>Description:</th><td>Timeout in seconds after which to cancel the pmlogger collection</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>int</code></td>
</tbody></table>
            </details></td></tr>
<tr><td colspan="2"><details><summary><strong>Objects</strong></summary><details><summary>PcpInputParams (<code>object</code>)</summary>
            <table><tbody><tr><th>Type:</th><td><code>object</code></td><tr><th>Properties</th><td><details><summary>pmlogger_interval (<code>float</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>pmlogger logging interval</td></tr><tr><th>Description:</th><td>The logging interval in seconds (float) used by pmlogger for data collection</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>float</code></td><tr><th>Units:</th><td>nanoseconds</td></tr>
</tbody></table>
        </details><details><summary>timeout (<code>int</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>pmlogger timeout seconds</td></tr><tr><th>Description:</th><td>Timeout in seconds after which to cancel the pmlogger collection</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>int</code></td>
</tbody></table>
        </details></td></tr>
</tbody></table>
        </details></details></td></tr>
</tbody></table>

### Outputs


#### error

<table><tbody>
<tr><th>Type:</th><td><code>scope</code></td><tr><th>Root object:</th><td>Error</td></tr>
<tr><th>Properties</th><td><details><summary>error (<code>string</code>)</summary>
                <table><tbody><tr><th>Required:</th><td>Yes</td></tr><tr><th>Type:</th><td><code>string</code></td></tbody></table>
            </details></td></tr>
<tr><td colspan="2"><details><summary><strong>Objects</strong></summary><details><summary>Error (<code>object</code>)</summary>
            <table><tbody><tr><th>Type:</th><td><code>object</code></td><tr><th>Properties</th><td><details><summary>error (<code>string</code>)</summary>
        <table><tbody><tr><th>Required:</th><td>Yes</td></tr><tr><th>Type:</th><td><code>string</code></td></tbody></table>
        </details></td></tr>
</tbody></table>
        </details></details></td></tr>
</tbody></table>

#### success

<table><tbody>
<tr><th>Type:</th><td><code>scope</code></td><tr><th>Root object:</th><td>PerfOutput</td></tr>
<tr><th>Properties</th><td><details><summary>pcp_output (<code>list[<code>reference[IntervalOutput]</code>]</code>)</summary>
                <table><tbody><tr><th>Name:</th><td>PCP output list</td></tr><tr><th>Description:</th><td>Performance data from PCP provided in a list format</td></tr><tr><th>Required:</th><td>Yes</td></tr><tr><th>Type:</th><td><code>list[<code>reference[IntervalOutput]</code>]</code></td><tr><td colspan="2">
    <details>
        <summary>List items</summary>
        <table><tbody><tr><th>Type:</th><td><code>reference[IntervalOutput]</code></td><tr><th>Referenced object:</th><td>IntervalOutput</td></tr></tbody></table>
    </details>
</td></tr></tbody></table>
            </details></td></tr>
<tr><td colspan="2"><details><summary><strong>Objects</strong></summary><details><summary>IntervalOutput (<code>object</code>)</summary>
            <table><tbody><tr><th>Type:</th><td><code>object</code></td><tr><th>Properties</th><td><details><summary>@interval (<code>int</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>Interval ID</td></tr><tr><th>Description:</th><td>The interval ID as reported by PCP</td></tr><tr><th>Required:</th><td>Yes</td></tr><tr><th>Type:</th><td><code>int</code></td>
</tbody></table>
        </details><details><summary>@timestamp (<code>string</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>Interval timestamp</td></tr><tr><th>Description:</th><td>The timestamp of the reported interval</td></tr><tr><th>Required:</th><td>Yes</td></tr><tr><th>Type:</th><td><code>string</code></td></tbody></table>
        </details><details><summary>commit (<code>map[<code>string</code>, <code>
    any</code>]</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>commit</td></tr><tr><th>Description:</th><td>The commit for the interval</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>map[<code>string</code>, <code>
    any</code>]</code></td><tr><td colspan="2">
    <details>
        <summary>Key type</summary>
        <table><tbody><tr><th>Type:</th><td><code>string</code></td></tbody></table>
    </details>
</td></tr>
<tr><td colspan="2">
    <details>
        <summary>Value type</summary>
        <table><tbody><tr><th>Type:</th><td><code>
    any</code></td></tbody></table>
    </details>
</td></tr>
</tbody></table>
        </details><details><summary>disk (<code>map[<code>string</code>, <code>
    any</code>]</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>disk</td></tr><tr><th>Description:</th><td>The disk structure for the interval</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>map[<code>string</code>, <code>
    any</code>]</code></td><tr><td colspan="2">
    <details>
        <summary>Key type</summary>
        <table><tbody><tr><th>Type:</th><td><code>string</code></td></tbody></table>
    </details>
</td></tr>
<tr><td colspan="2">
    <details>
        <summary>Value type</summary>
        <table><tbody><tr><th>Type:</th><td><code>
    any</code></td></tbody></table>
    </details>
</td></tr>
</tbody></table>
        </details><details><summary>kbin (<code>map[<code>string</code>, <code>
    any</code>]</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>kbin</td></tr><tr><th>Description:</th><td>The KB in value for the interval</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>map[<code>string</code>, <code>
    any</code>]</code></td><tr><td colspan="2">
    <details>
        <summary>Key type</summary>
        <table><tbody><tr><th>Type:</th><td><code>string</code></td></tbody></table>
    </details>
</td></tr>
<tr><td colspan="2">
    <details>
        <summary>Value type</summary>
        <table><tbody><tr><th>Type:</th><td><code>
    any</code></td></tbody></table>
    </details>
</td></tr>
</tbody></table>
        </details><details><summary>kbout (<code>map[<code>string</code>, <code>
    any</code>]</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>kbout</td></tr><tr><th>Description:</th><td>The KB out value for the interval</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>map[<code>string</code>, <code>
    any</code>]</code></td><tr><td colspan="2">
    <details>
        <summary>Key type</summary>
        <table><tbody><tr><th>Type:</th><td><code>string</code></td></tbody></table>
    </details>
</td></tr>
<tr><td colspan="2">
    <details>
        <summary>Value type</summary>
        <table><tbody><tr><th>Type:</th><td><code>
    any</code></td></tbody></table>
    </details>
</td></tr>
</tbody></table>
        </details><details><summary>kernel (<code>map[<code>string</code>, <code>
    any</code>]</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>kernel</td></tr><tr><th>Description:</th><td>The kernel CPU structure for the interval</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>map[<code>string</code>, <code>
    any</code>]</code></td><tr><td colspan="2">
    <details>
        <summary>Key type</summary>
        <table><tbody><tr><th>Type:</th><td><code>string</code></td></tbody></table>
    </details>
</td></tr>
<tr><td colspan="2">
    <details>
        <summary>Value type</summary>
        <table><tbody><tr><th>Type:</th><td><code>
    any</code></td></tbody></table>
    </details>
</td></tr>
</tbody></table>
        </details><details><summary>mem (<code>map[<code>string</code>, <code>
    any</code>]</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>mem</td></tr><tr><th>Description:</th><td>The memory structure for the interval</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>map[<code>string</code>, <code>
    any</code>]</code></td><tr><td colspan="2">
    <details>
        <summary>Key type</summary>
        <table><tbody><tr><th>Type:</th><td><code>string</code></td></tbody></table>
    </details>
</td></tr>
<tr><td colspan="2">
    <details>
        <summary>Value type</summary>
        <table><tbody><tr><th>Type:</th><td><code>
    any</code></td></tbody></table>
    </details>
</td></tr>
</tbody></table>
        </details><details><summary>memused (<code>map[<code>string</code>, <code>
    any</code>]</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>memused</td></tr><tr><th>Description:</th><td>The memory used value for the interval</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>map[<code>string</code>, <code>
    any</code>]</code></td><tr><td colspan="2">
    <details>
        <summary>Key type</summary>
        <table><tbody><tr><th>Type:</th><td><code>string</code></td></tbody></table>
    </details>
</td></tr>
<tr><td colspan="2">
    <details>
        <summary>Value type</summary>
        <table><tbody><tr><th>Type:</th><td><code>
    any</code></td></tbody></table>
    </details>
</td></tr>
</tbody></table>
        </details><details><summary>pktin (<code>map[<code>string</code>, <code>
    any</code>]</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>pktin</td></tr><tr><th>Description:</th><td>The packets in for the interval</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>map[<code>string</code>, <code>
    any</code>]</code></td><tr><td colspan="2">
    <details>
        <summary>Key type</summary>
        <table><tbody><tr><th>Type:</th><td><code>string</code></td></tbody></table>
    </details>
</td></tr>
<tr><td colspan="2">
    <details>
        <summary>Value type</summary>
        <table><tbody><tr><th>Type:</th><td><code>
    any</code></td></tbody></table>
    </details>
</td></tr>
</tbody></table>
        </details><details><summary>pktout (<code>map[<code>string</code>, <code>
    any</code>]</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>pktout</td></tr><tr><th>Description:</th><td>The packets out for the interval</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>map[<code>string</code>, <code>
    any</code>]</code></td><tr><td colspan="2">
    <details>
        <summary>Key type</summary>
        <table><tbody><tr><th>Type:</th><td><code>string</code></td></tbody></table>
    </details>
</td></tr>
<tr><td colspan="2">
    <details>
        <summary>Value type</summary>
        <table><tbody><tr><th>Type:</th><td><code>
    any</code></td></tbody></table>
    </details>
</td></tr>
</tbody></table>
        </details></td></tr>
</tbody></table>
        </details><details><summary>PerfOutput (<code>object</code>)</summary>
            <table><tbody><tr><th>Type:</th><td><code>object</code></td><tr><th>Properties</th><td><details><summary>pcp_output (<code>list[<code>reference[IntervalOutput]</code>]</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>PCP output list</td></tr><tr><th>Description:</th><td>Performance data from PCP provided in a list format</td></tr><tr><th>Required:</th><td>Yes</td></tr><tr><th>Type:</th><td><code>list[<code>reference[IntervalOutput]</code>]</code></td><tr><td colspan="2">
    <details>
        <summary>List items</summary>
        <table><tbody><tr><th>Type:</th><td><code>reference[IntervalOutput]</code></td><tr><th>Referenced object:</th><td>IntervalOutput</td></tr></tbody></table>
    </details>
</td></tr></tbody></table>
        </details></td></tr>
</tbody></table>
        </details></details></td></tr>
</tbody></table>
<!-- End of autogenerated documentation -->
