#!/bin/bash

TABLE="traffic_stats"
CHAIN="count_chain"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <install|uninstall|check>"
    exit 1
fi

ACTION=$1

if [ "$ACTION" == "install" ]; then
    # Check if table exists
    exists=$(sudo nft -j list ruleset | jq 'any(.nftables[]; .table?.name=="'"$TABLE"'")')
    if [ "$exists" == "true" ]; then
        echo "Table $TABLE exists, deleting it first..."
        sudo nft delete table inet "$TABLE"
    fi

    # Create table and chain
    echo "Creating table $TABLE and chain $CHAIN..."
    sudo nft add table inet "$TABLE"
    sudo nft add chain inet "$TABLE" "$CHAIN" '{ type filter hook prerouting priority 0; policy accept; }'

elif [ "$ACTION" == "uninstall" ]; then
    # Delete chain and table
    echo "Deleting chain $CHAIN and table $TABLE..."
    sudo nft delete chain inet "$TABLE" "$CHAIN" 2>/dev/null
    sudo nft delete table inet "$TABLE" 2>/dev/null

elif [ "$ACTION" == "check" ]; then
    # Check if table exists and return status
    exists=$(sudo nft -j list ruleset | jq 'any(.nftables[]; .table?.name=="'"$TABLE"'")')
    if [ "$exists" == "true" ]; then
        echo "true"
        exit 0
    else
        echo "false"
        exit 1
    fi

else
    echo "Unknown action: $ACTION"
    exit 1
fi

echo "Done."
