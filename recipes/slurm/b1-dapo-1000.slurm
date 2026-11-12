#!/bin/bash
#SBATCH --gpus=2
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --account=vusr117232
#SBATCH --partition=gpu_a100
#SBATCH -J rwkv-b1-dapo1000  # 用户自行改名
#SBATCH -o ${SCRATCH:-/path/to/your/scratch}/rwkv-agentic/logs/p2b-smoke-%j.out
set -uo pipefail
SCRATCH=${SCRATCH:-/path/to/your/scratch}/rwkv-agentic; V=$SCRATCH/env/skyrl-rwkv; SRC=$SCRATCH/src/skyrl-rwkv
export PATH=$SCRATCH/bin:$PATH
export CUDA_HOME=$V/lib/python3.12/site-packages/nvidia/cu13
export PATH=$CUDA_HOME/bin:$PATH CUDACXX=$CUDA_HOME/bin/nvcc
export LD_LIBRARY_PATH=/sw/arch/RHEL9/EB_production/2024/software/GCCcore/13.3.0/lib64:${LD_LIBRARY_PATH:-}
export PYTHON=$V/bin/python3 UV_PROJECT_ENVIRONMENT=$V UV_CACHE_DIR=/tmp/uv-cache
export FLASHRWKV2_CACHE_DIR=$SCRATCH/cache/flashrwkv2 TILELANG_CACHE_DIR=$SCRATCH/cache/tilelang
export HF_HOME=$SCRATCH/hf TMPDIR=/tmp RAY_TMPDIR=/tmp/ray-${SLURM_JOB_ID}
mkdir -p $RAY_TMPDIR $SCRATCH/runs
LOG=$SCRATCH/logs/p2b-train-${SLURM_JOB_ID}.log
cd $SRC || exit 1
nvidia-smi -L >/dev/null 2>&1 || { echo "[p2b] NO GPU"; exit 1; }
bash examples/train/rwkv/train/p2b_dapo/run.sh --prepare-flashrwkv2 > $SCRATCH/logs/p2b-preflight-${SLURM_JOB_ID}.log 2>&1
echo "[p2b] preflight exit=$?"
export ASYNC_MODE=disabled POLICY_GPUS=2 INFERENCE_GPUS=2
export MODEL_DIR=$SCRATCH/runs/p15-sft-29014001/hf_exports/global_step_234/policy
export DATA_DIR=/scratch-shared/szhang4/rwkv-agentic/data/gsm8k
export OUTPUT_ROOT=$SCRATCH/runs/p2b-dapo-${SLURM_JOB_ID}
export RUN_NAME=p2b-smoke-${SLURM_JOB_ID}
export VLLM_RWKV_TUNING_MODE=tune
export BATCH_SIZE=4 MICRO_BATCH_SIZE=1 GROUP_SIZE=4 POLICY_MINI_BATCH_SIZE=4 MAX_GENERATE_LENGTH=1280 MAX_TOKENS_PER_MICROBATCH=49152
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export MAX_STEPS=1000 CKPT_INTERVAL=100 EVAL_INTERVAL=1000 SAMPLING_TEMP=1.0 STRICT_REWARD=false DYN_SAMPLING=null
for attempt in 1 2; do
  rm -rf /tmp/ray-${SLURM_JOB_ID} 2>/dev/null; mkdir -p /tmp/ray-${SLURM_JOB_ID}
  echo "[p2b] attempt=$attempt start=$(date -u +%FT%TZ)" >> $LOG
  bash examples/train/rwkv/train/p2b_dapo/run.sh \
    generator.inference_engine.enforce_eager=true \
    generator.inference_engine.gpu_memory_utilization=0.4 \
    generator.inference_engine.max_num_seqs=32 >> $LOG 2>&1
  rc=$?
  echo "[p2b] attempt=$attempt rc=$rc end=$(date -u +%FT%TZ)" >> $LOG
  [ $rc -eq 0 ] && break
  sleep 30
done
echo "[p2b] done $(date -u +%FT%TZ)"; tail -30 $LOG
