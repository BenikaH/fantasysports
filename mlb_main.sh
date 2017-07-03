#!/bin/bash
# example use: sh mlb_main.sh 5000 '2016_07_09' 'main' 500 
# load variables
NUM_SIMS=$1
PROJ_DATE=$2
PROJ_NICKNAME=$3
NUM_LINEAR_LINEUPS=$4

# generate a formatted date for file naming and loading
# FMT_DT=`python -c 'from dateutil.parser import parse; print parse("'$PROJ_DATE'").strftime("%Y_%m_%d");'`

# run simulated games to generate projections
python -m projection_generator $NUM_SIMS $PROJ_DATE $PROJ_NICKNAME

# generate lineups using linear method
Rscript generate_lineups.R $PROJ_DATE $PROJ_NICKNAME $NUM_LINEAR_LINEUPS 'fanduel'
Rscript generate_lineups.R $PROJ_DATE $PROJ_NICKNAME $NUM_LINEAR_LINEUPS 'draftkings'

# build variance additions for our lineups
python -m covariance_calculator $PROJ_DATE 'fanduel' $PROJ_NICKNAME
python -m covariance_calculator $PROJ_DATE 'draftkings' $PROJ_NICKNAME

# append genetic algorithm lineups
python -m mlb_lineup_generator $PROJ_DATE 'fanduel' $PROJ_NICKNAME
python -m mlb_lineup_generator $PROJ_DATE 'draftkings' $PROJ_NICKNAME

