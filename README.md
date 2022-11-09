# promtail (subordinate charm)

Charmhub package name: promtail
More information: https://charmhub.io/promtail

Read more for haproxy setup: 

https://devpress.csdn.net/bigdata/62f6169d7e6682346618a814.html

## Deploying
Get the latest release from github and pass it as a resource to juju deployment.

    PROMTAIL_VERSION=$(curl -s "https://api.github.com/repos/grafana/loki/releases/latest" | grep -Po '"tag_name": "v\K[0-9.]+')
    
    wget -qO promtail.zip "https://github.com/grafana/loki/releases/download/v${PROMTAIL_VERSION}/promtail-linux-amd64.zip"
    
    juju deploy loki --resource promtail-zipfile=./promtail.zip --series jammy

## Test Loki listens and registers logs:

Once the status is ready, you can test that loki gets logs first, before testing promtail itself. Send a test log to loki as:


    curl -H "Content-Type: application/json" -XPOST -s "http://localhost:3100/loki/api/v1/push" --data-raw "{\"streams\": [{\"stream\": {\"job\": \"test\"}, \"values\": [[\"$(date +%s)000000000\", \"fizzbuzz\"]]}]}"

Then query loki for those records.

    curl -G -s "http://localhost:3100/loki/api/v1/query_range" --data-urlencode 'query={job="test"}' --data-urlencode 'step=300' | jq .data.result

Should output something like this:
```
[
  {
    "stream": {
      "job": "test"
    },
    "values": [
      [
        "1667977182000000000",
        "fizzbuzz"
      ]
    ]
  }
]
```

## Test promtail.

Once the promtail service is active, it will start monitoring /var/log/*.log and ship it to configured loki host. (TODO: relation)

See: https://grafana.com/docs/grafana-cloud/data-configuration/logs/collect-logs-with-promtail/

## Setting a custom config with an action

    juju run-action promtail/0 set-config config="$(base64 /tmp/promtail.yaml)" --wait


## More configuration examples

More configuration examples can be found here:

https://github.com/grafana/loki/tree/main/clients/cmd/promtail

## Trouble shooting promtail

See: https://grafana.com/docs/loki/latest/clients/promtail/troubleshooting/
