#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")/../plugins" ; pwd -P )

docker run \
    --rm \
    --name testneo4j \
    -p7474:7474 -p7687:7687 \
    --volume=$parent_path':/plugins' \
    --env NEO4J_AUTH=neo4j/test \
    --env NEO4J_dbms_security_procedures_unrestricted=algo.* \
    neo4j:3.5.12 &
