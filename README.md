# Performance Copilot (PCP) Plugin

This plugin runs PCP pmlogger, collects data until cancelled,
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

***Note:** This plugin is designed to be used as a container image built with
the provided Dockerfile. Using the python directly on a target system will
likely prove problematic*

## Container Privileged Mode

Note that some metrics collected by PCP are in fact at the host system level
even when running in a non-privileged container, but many metrics are
namespace-scoped. In order to collect all metrics at the host level, you will
need to run the containerized plugin in privileged mode with host networking.

## Power User Configurations

***Please exercise caution in using the configuration options noted here.
There is no input validation for the custom configurations, and malformed
entries will lead to a plugin failure, possibly late in the run.***

### pmlogger config files
Under normal operation, the plugin generates for itself a default configuration
file for pmlogger using the `pmlogconf` command. In most circumstances, this
is likely adequate, and no special actions or input are needed from the user for
the configuration.

For experienced users of pmlogger who would like to specify a custom configuration,
the input schema for the plugin does allow a **complete** pmlogger config file to
be included in the input as a multi-line string to the `pmlogger_conf` key.

### pcp2json/pmrep config files
The container will deploy with a standard set of `pmrep` configuration files 
internally under `/etc/pcp/pmrep/`. An experienced user may also pass a **complete**
pmrep config file as a multi-line string to the `pmrep_conf` key.

### pcp2json/pmrep metrics
Any metrics or metricsets defined in the pmrep config file(s) can be referenced
in the standard `pmrep` format, with which the `pcp2json` command is compatible.
The desired metrics/sets are optionally passed as a string to the `pmlogger_metrics`
key in the input. If nothing is provided to this key in the input, the default value
documented below will be used.

# Autogenerated Input/Output Documentation by Arcaflow-Docsgen Below

<!-- Autogenerated documentation by arcaflow-docsgen -->
## Start PCP (`start-pcp`)

Start the PCP data logging tools

### Input

<table><tbody>
<tr><th>Type:</th><td><code>scope</code></td><tr><th>Root object:</th><td>PcpInputParams</td></tr>
<tr><th>Properties</th><td><details><summary>flatten (<code>bool</code>)</summary>
                <table><tbody><tr><th>Name:</th><td>flatten JSON structure</td></tr><tr><th>Description:</th><td>Processes the metrics first into a two-dimensional format via the pcp2csv converter, and then converts the CSV to JSON, effectively flattening the data structure. This is useful when indexing metrics to a service like Elasticsearch.</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Default (JSON encoded):</th><td><pre><code>false</code></pre></td></tr><tr><th>Type:</th><td><code>bool</code></td></tbody></table>
            </details><details><summary>generate_csv (<code>bool</code>)</summary>
                <table><tbody><tr><th>Name:</th><td>generate CSV output</td></tr><tr><th>Description:</th><td>Generates the data payload also in CSV format. This output goes to the debug_logs, or to stderr if the --debug flag is used.</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Default (JSON encoded):</th><td><pre><code>false</code></pre></td></tr><tr><th>Type:</th><td><code>bool</code></td></tbody></table>
            </details><details><summary>pmlogger_conf (<code>string</code>)</summary>
                <table><tbody><tr><th>Name:</th><td>pmlogger configuration file</td></tr><tr><th>Description:</th><td>Complete configuration file content for pmlogger as a multi-line string. If no config file is provided, a default one will be generated. NOTE: Input not validated by the plugin -- Any errors are likely to be produced at the end of the plugin run and may result in workflow failures.</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>string</code></td></tbody></table>
            </details><details><summary>pmlogger_interval (<code>float</code>)</summary>
                <table><tbody><tr><th>Name:</th><td>pmlogger logging interval</td></tr><tr><th>Description:</th><td>The logging interval in seconds (float) used by pmlogger for data collection</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Default (JSON encoded):</th><td><pre><code>1.0</code></pre></td></tr><tr><th>Type:</th><td><code>float</code></td><tr><th>Units:</th><td>nanoseconds</td></tr>
</tbody></table>
            </details><details><summary>pmlogger_metrics (<code>string</code>)</summary>
                <table><tbody><tr><th>Name:</th><td>pmlogger metrics to report</td></tr><tr><th>Description:</th><td>The pmrep-compatible metrics values to report as a space-separated string. NOTE: Input not validated by the plugin -- Any errors are likely to be produced at the end of the plugin run and may result in workflow failures.</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Default (JSON encoded):</th><td><pre><code>&#34;:vmstat :sar :sar-B :sar-w :sar-b :sar-H :sar-r&#34;</code></pre></td></tr><tr><th>Type:</th><td><code>string</code></td></tbody></table>
            </details><details><summary>pmrep_conf (<code>string</code>)</summary>
                <table><tbody><tr><th>Name:</th><td>pmrep configuration file</td></tr><tr><th>Description:</th><td>Complete configuration file content for pmrep as a multi-line string. If no config file is provided, a default one will be used. This configuration is used internally for `pcp2json` and `pcp2csv`. NOTE: Input not validated by the plugin -- Any errors are likely to be produced at the end of the plugin run and may result in workflow failures.</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>string</code></td></tbody></table>
            </details><details><summary>timeout (<code>int</code>)</summary>
                <table><tbody><tr><th>Name:</th><td>pmlogger timeout seconds</td></tr><tr><th>Description:</th><td>Timeout in seconds after which to cancel the pmlogger collection</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>int</code></td>
</tbody></table>
            </details></td></tr>
<tr><td colspan="2"><details><summary><strong>Objects</strong></summary><details><summary>PcpInputParams (<code>object</code>)</summary>
            <table><tbody><tr><th>Type:</th><td><code>object</code></td><tr><th>Properties</th><td><details><summary>flatten (<code>bool</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>flatten JSON structure</td></tr><tr><th>Description:</th><td>Processes the metrics first into a two-dimensional format via the pcp2csv converter, and then converts the CSV to JSON, effectively flattening the data structure. This is useful when indexing metrics to a service like Elasticsearch.</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Default (JSON encoded):</th><td><pre><code>false</code></pre></td></tr><tr><th>Type:</th><td><code>bool</code></td></tbody></table>
        </details><details><summary>generate_csv (<code>bool</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>generate CSV output</td></tr><tr><th>Description:</th><td>Generates the data payload also in CSV format. This output goes to the debug_logs, or to stderr if the --debug flag is used.</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Default (JSON encoded):</th><td><pre><code>false</code></pre></td></tr><tr><th>Type:</th><td><code>bool</code></td></tbody></table>
        </details><details><summary>pmlogger_conf (<code>string</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>pmlogger configuration file</td></tr><tr><th>Description:</th><td>Complete configuration file content for pmlogger as a multi-line string. If no config file is provided, a default one will be generated. NOTE: Input not validated by the plugin -- Any errors are likely to be produced at the end of the plugin run and may result in workflow failures.</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>string</code></td></tbody></table>
        </details><details><summary>pmlogger_interval (<code>float</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>pmlogger logging interval</td></tr><tr><th>Description:</th><td>The logging interval in seconds (float) used by pmlogger for data collection</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Default (JSON encoded):</th><td><pre><code>1.0</code></pre></td></tr><tr><th>Type:</th><td><code>float</code></td><tr><th>Units:</th><td>nanoseconds</td></tr>
</tbody></table>
        </details><details><summary>pmlogger_metrics (<code>string</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>pmlogger metrics to report</td></tr><tr><th>Description:</th><td>The pmrep-compatible metrics values to report as a space-separated string. NOTE: Input not validated by the plugin -- Any errors are likely to be produced at the end of the plugin run and may result in workflow failures.</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Default (JSON encoded):</th><td><pre><code>&#34;:vmstat :sar :sar-B :sar-w :sar-b :sar-H :sar-r&#34;</code></pre></td></tr><tr><th>Type:</th><td><code>string</code></td></tbody></table>
        </details><details><summary>pmrep_conf (<code>string</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>pmrep configuration file</td></tr><tr><th>Description:</th><td>Complete configuration file content for pmrep as a multi-line string. If no config file is provided, a default one will be used. This configuration is used internally for `pcp2json` and `pcp2csv`. NOTE: Input not validated by the plugin -- Any errors are likely to be produced at the end of the plugin run and may result in workflow failures.</td></tr><tr><th>Required:</th><td>No</td></tr><tr><th>Type:</th><td><code>string</code></td></tbody></table>
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
<tr><th>Properties</th><td><details><summary>pcp_output (<code>list[<code>
    any</code>]</code>)</summary>
                <table><tbody><tr><th>Name:</th><td>PCP output list</td></tr><tr><th>Description:</th><td>List of of performance data in intervals from PCP</td></tr><tr><th>Required:</th><td>Yes</td></tr><tr><th>Type:</th><td><code>list[<code>
    any</code>]</code></td><tr><td colspan="2">
    <details>
        <summary>List items</summary>
        <table><tbody><tr><th>Type:</th><td><code>
    any</code></td></tbody></table>
    </details>
</td></tr></tbody></table>
            </details></td></tr>
<tr><td colspan="2"><details><summary><strong>Objects</strong></summary><details><summary>PerfOutput (<code>object</code>)</summary>
            <table><tbody><tr><th>Type:</th><td><code>object</code></td><tr><th>Properties</th><td><details><summary>pcp_output (<code>list[<code>
    any</code>]</code>)</summary>
        <table><tbody><tr><th>Name:</th><td>PCP output list</td></tr><tr><th>Description:</th><td>List of of performance data in intervals from PCP</td></tr><tr><th>Required:</th><td>Yes</td></tr><tr><th>Type:</th><td><code>list[<code>
    any</code>]</code></td><tr><td colspan="2">
    <details>
        <summary>List items</summary>
        <table><tbody><tr><th>Type:</th><td><code>
    any</code></td></tbody></table>
    </details>
</td></tr></tbody></table>
        </details></td></tr>
</tbody></table>
        </details></details></td></tr>
</tbody></table>
<!-- End of autogenerated documentation -->
