#!/bin/bash

cat << EOF > ${PIPELINES_DIR}/pipelines.yaml
cross_lsdb_dev:
    display_name: 'LSDB Crossmatch (dev)'
    path: '${PIPELINES_DIR}/cross_lsdb_dev'
    executor: 'local' # only to orchestration
    runner: 'bash'
    executable: 'run.sh'
    schema_config: '${PIPELINES_DIR}/cross_lsdb_dev/config.py'
    version: '0.0.1'
EOF