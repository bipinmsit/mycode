#!/bin/sh

collect () {
  report "$( nvidia-smi --query-gpu=utilization.gpu --format=csv -i $GPU_ID | sed "1 d" | sed "s/\ %//g" )"
}

