sudo tc qdisc add dev lo root handle 1:0 netem delay "$@"
