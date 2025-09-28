#!/bin/sh

TABLE="traffic_stats"
CHAIN="count_chain"

# Check if table exists
require_table() {
    if ! sudo nft -j list ruleset | jq 'any(.nftables[]; .table?.name=="'"$TABLE"'")' | grep -q true; then
        echo "Error: Table $TABLE does not exist."
        exit 1
    fi
}

# Check if port is valid
check_port() {
    port=$1
    if ! echo "$port" | grep -Eq '^[0-9]+$'; then
        echo "Error: Port must be a number."
        exit 1
    fi
    if [ "$port" -lt 0 ] || [ "$port" -gt 65535 ]; then
        echo "Error: Port out of valid range (0-65535)."
        exit 1
    fi
}

# Check if counter exists
counter_exists() {
    port=$1
    s_counter="s_$port"
    d_counter="d_$port"
    sudo nft -j list ruleset \
        | jq -r '.nftables[] | select(.counter != null) | .counter.name' \
        | grep -E "^($s_counter|$d_counter)$" >/dev/null 2>&1
}

# Add port counters and rules
add_port() {
    port=$1
    require_table
    check_port "$port"

    if counter_exists "$port"; then
        echo "Warning: Counters for port $port already exist. Skipping addition."
        return
    fi

    echo "Adding counters and rules for port $port..."
    sudo nft add counter inet $TABLE d_$port '{ packets 0 bytes 0; }' 2>/dev/null
    sudo nft add counter inet $TABLE s_$port '{ packets 0 bytes 0; }' 2>/dev/null
    sudo nft add rule inet $TABLE $CHAIN tcp sport $port counter name s_$port 2>/dev/null
    sudo nft add rule inet $TABLE $CHAIN tcp dport $port counter name d_$port 2>/dev/null
}

# Delete port counters and rules
del_port() {
    port=$1
    require_table
    check_port "$port"

    s_counter="s_$port"
    d_counter="d_$port"

    if ! counter_exists "$port"; then
        echo "Warning: Counters for port $port do not exist. Skipping deletion."
        return
    fi

    echo "Deleting counters and rules for port $port..."

    # Delete rules that reference the counters
    sudo nft -j list ruleset \
      | jq -r '
          .nftables[]
          | select(.rule?)
          | select(.rule.expr[]? | .counter? == "'"$s_counter"'" or .counter? == "'"$d_counter"'")
          | .rule.handle
        ' \
      | xargs -r -I{} sudo nft delete rule inet $TABLE $CHAIN handle {}

    # Delete counters
    sudo nft delete counter inet $TABLE $s_counter 2>/dev/null
    sudo nft delete counter inet $TABLE $d_counter 2>/dev/null
}

# Print all counters in traffic_stats table
print_counters() {
    require_table
    sudo nft -j list ruleset | jq \
        '.nftables[]
         | select(.counter != null)
         | select(.counter.table=="'"$TABLE"'")'
}

# Script entry point
case "$1" in
    add)
        [ -z "$2" ] && echo "Usage: $0 add <port>" && exit 1
        add_port "$2"
        ;;
    del)
        [ -z "$2" ] && echo "Usage: $0 del <port>" && exit 1
        del_port "$2"
        ;;
    print)
        print_counters
        ;;
    *)
        echo "Usage: $0 {add <port>|del <port>|print}"
        exit 1
        ;;
esac
