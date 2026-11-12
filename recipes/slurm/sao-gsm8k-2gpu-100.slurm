#!/bin/bash
#SBATCH --gpus=2
#SBATCH --cpus-per-task=16
#SBATCH --mem=120G
#SBATCH --time=12:00:00
#SBATCH --account=vusr117232
#SBATCH --partition=gpu_a100
#SBATCH -J rwkv-sao-gsm8k
#SBATCH -o ${SCRATCH:-/path/to/your/scratch}/rwkv-agentic/logs/sao2g100-%j.out
set -uo pipefail
SCRATCH=${SCRATCH:-/path/to/your/scratch}/rwkv-agentic
V=$SCRATCH/env/skyrl-rwkv
SRC=$SCRATCH/src/skyrl-rwkv
export PATH=$SCRATCH/bin:$PATH
export CUDA_HOME=$V/lib/python3.12/site-packages/nvidia/cu13
export PATH=$CUDA_HOME/bin:$PATH CUDACXX=$CUDA_HOME/bin/nvcc
export LD_LIBRARY_PATH=/sw/arch/RHEL9/EB_production/2024/software/GCCcore/13.3.0/lib64:${LD_LIBRARY_PATH:-}
export PYTHON=$V/bin/python3 UV_PROJECT_ENVIRONMENT=$V UV_CACHE_DIR=/tmp/uv-cache
export FLASHRWKV2_CACHE_DIR=$SCRATCH/cache/flashrwkv2
export TILELANG_CACHE_DIR=$SCRATCH/cache/tilelang
export HF_HOME=$SCRATCH/hf TMPDIR=/tmp
export CUDA_VISIBLE_DEVICES=0,1
cd $SRC || exit 1
LOG=$SCRATCH/logs/sao2g100-train-${SLURM_JOB_ID}.log
nvidia-smi -L >/dev/null 2>&1 || { echo "[sao] NO GPU"; exit 1; }
echo "[sao] preflight $(date -u +%FT%TZ)" >> $LOG
bash examples/train/rwkv/train/sao-gsm8k/run.sh --prepare-flashrwkv2 >> $SCRATCH/logs/sao2g100-preflight-${SLURM_JOB_ID}.log 2>&1
echo "[sao] preflight rc=$?" >> $LOG
export ASYNC_MODE=disabled POLICY_GPUS=2 CRITIC_GPUS=2 INFERENCE_GPUS=2
export MODEL_DIR=$SCRATCH/runs/p15-sft-29014001/hf_exports/global_step_234/policy
export CRITIC_MODEL_DIR=$MODEL_DIR
export DATA_DIR=$SCRATCH/data/gsm8k
export OUTPUT_ROOT=$SCRATCH/runs/sao-gsm8k-${SLURM_JOB_ID}
export RUN_NAME=sao2g100-${SLURM_JOB_ID}
export VLLM_RWKV_TUNING_MODE=tune
for attempt in 1 2; do
  export RAY_TMPDIR=/tmp/ray-${SLURM_JOB_ID}
  rm -rf $RAY_TMPDIR 2>/dev/null; mkdir -p $RAY_TMPDIR
  echo "[sao] attempt=$attempt start=$(date -u +%FT%TZ)" >> $LOG
  MAX_STEPS=100 CKPT_INTERVAL=25 bash examples/train/rwkv/train/sao-gsm8k/run.sh >> $LOG 2>&1
  rc=$?
  echo "[sao] attempt=$attempt rc=$rc end=$(date -u +%FT%TZ)" >> $LOG
  [ $rc -eq 0 ] && break
  sleep 20
done
echo "[sao] done $(date -u +%FT%TZ)" >> $LOG
tail -40 $LOG
