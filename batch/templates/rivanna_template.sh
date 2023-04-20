#!/bin/bash
#SBATCH -p {QUEUE}
#SBATCH -N {NUM_NODES}
#SBATCH --qos={QOS}
#SBATCH --ntasks-per-node={TASKS_PER_NODE}
#SBATCH --cpus-per-task={CPUS_PER_TASK}
#SBATCH --exclusive
#SBATCH -t {TIME}
#SBATCH --output=experiments/out/{TEST_NAME}/{OUTPUT}.out
#SBATCH --account=nssac_students

# Set flags
ENABLE_SCRATCH={ENABLE_SCRATCH}
ENABLE_DATA_GENERATION={ENABLE_DATA_GENERATION}
ENABLE_CACHE={ENABLE_CACHE}
ENABLE_SMP={ENABLE_SMP}
ENABLE_TRACING={ENABLE_TRACING}
ENABLE_LOAD_BALANCING={ENABLE_LB}

export PROJECT_ROOT=$HOME/biocomplexity/loimos

module load gompi/9.2.0_3.1.6

export PROTOBUF_HOME="$PROJECT_ROOT/protobuf/cmake/install"
export LD_LIBRARY_PATH="$PROTOBUF_HOME/lib/:$CHARM_HOME/lib/:$LD_LIBRARY_PATH"

BIN="$PROJECT_ROOT/loimos/src/loimos"
OUT_DIR=experiments/out/{TEST_NAME}/{OUTPUT}
OUT_FILE=$OUT_DIR-record.csv
DISEASE_MODEL=$PROJECT_ROOT/loimos/data/disease_models/{DISEASE_MODEL}

if $ENABLE_SCRATCH; then
  POPULATION_DIR=/scratch/$USER/loimos/data/populations/{DATASET}/
else
  POPULATION_DIR=$PROJECT_ROOT/loimos/data/populations/{DATASET}/
fi

# Loimos expects different positional arguments based on whether or not the
# network data will be generated at runtime
if $ENABLE_DATA_GENERATION; then
  ARGS="1 {PEOPLE_GRID_WIDTH} {PEOPLE_GRID_HEIGHT} {LOCATION_GRID_WIDTH} {LOCATION_GRID_HEIGHT} {DEGREE} {LOC_PARTITION_WIDTH} {LOC_PARTITION_HEIGHT} {PEOPLE_CHARES} {DAYS} $OUT_FILE $DISEASE_MODEL"
else
 ARGS="0 {NUM_PEOPLE} {NUM_LOCATIONS} {PEOPLE_CHARES} {LOC_CHARES} {DAYS} 7 $OUT_FILE $DISEASE_MODEL $POPULATION_DIR"
fi

if ! $ENABLE_CACHE; then
  rm $POPULATION_DIR/*.cache
fi

export CHARM_HOME="/home/arr2vg/biocomplexity/loimos/charm/mpi-linux-x86_64"
if $ENABLE_SMP; then
  BIN="$BIN-smp"
  ARGS="$ARGS ++ppn {PPN} +pemap {PEMAP} +commap {COMMAP}"
  #ARGS="$ARGS ++auto-provision"
  export CHARM_HOME="$CHARM_HOME-smp"
fi

if $ENABLE_TRACING; then
  BIN="$BIN-prj"
  ARGS="$ARGS +logsize 20000000 +traceoff +gz-trace +traceroot $OUT_DIR"

  if [ -d $OUT_DIR ]; then
    rm $OUT_DIR/{OUTPUT}.*.log.gz
  else
    mkdir $OUT_DIR
  fi
fi

if $ENABLE_LOAD_BALANCING; then
  BIN="$BIN-lb"
  ARGS="$ARGS -balancer RefineLB +LBDebug 0 +LBOff"
fi

CMD="srun -n {NUM_TASKS} $BIN $ARGS"

# Save run command to make settings explicit in output file; can be helpful
# when debugging runs
echo Running Loimos with command:
echo "$CMD"

$CMD
