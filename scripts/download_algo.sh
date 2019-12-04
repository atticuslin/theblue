#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")/.." ; pwd -P )

cd "$parent_path"

mkdir plugins
cd plugins
curl -OL http://s3-eu-west-1.amazonaws.com/com.neo4j.graphalgorithms.dist/neo4j-graph-algorithms-3.5.12.1-standalone.jar