#!/usr/bin/env bash

trains_file="$1"  # A headerless CSV file containing tagbiljett arguments
prices_file="$2"  # A file to store the prices in (generated automatically)

old_prices=$(cat "${prices_file}" 2>/dev/null)

> "${prices_file}"
while IFS=',' read -ra args; do
    prefix="${args[@]}"
    python -m tagbiljett "${args[@]}" | sed -e "s/^/$prefix\t/" >> "${prices_file}"
done < "${trains_file}"

diff <(echo "${old_prices}") <(cat "${prices_file}")
