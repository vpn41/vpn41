#!/usr/bin/env bash

THISDIR=$(dirname ${0})
docker build "${THISDIR}" -f "${THISDIR}/build-bin.Dockerfile" -t vpn41-build
docker run -v $(pwd)/dist:/dist --rm vpn41-build
