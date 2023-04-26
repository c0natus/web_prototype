#!/bin/bash

base_dir=${PWD}

nohup streamlit run ./Front/home.py --server.port=2941 > ${base_dir}/Front/log.out &
nohup uvicorn Back.main:app --reload --host=0.0.0.0 > ${base_dir}/Back/log.out &