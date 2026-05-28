#!/bin/bash
module load intel
module load impi

# cpus="$SLURM_CPUS_ON_NODE"
# cpus="$SLURM_NTASKS"
cpus="N_CPUS_FOR_SIM"
nodelistcompact="$SLURM_JOB_NODELIST"
nodelistfull=`scontrol show hostnames $nodelistcompact`
n_prcs=`echo $nodelistfull | sed 's/$/ /g' | sed 's/ /:'"$cpus,"'/g'`

echo $n_prcs

sim_file="SIM_FILE_NAME"
java_name="JOB_NAME"
rm -f "JOB_NAME".log

version="STAR_VERSION"

rm -f DONE
rm -f ABORT

${version}/star/bin/starccm+ -printpids -batch -rsh ssh $java_name.java $sim_file -on $n_prcs | tee -a "JOB_NAME".log
touch DONE
