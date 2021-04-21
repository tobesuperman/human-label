#!/bin/bash
source activate lbj
export PYTHONPATH=/home/human_label:$PYTHONPATH
pid_number=`ps -ef|grep scut_human_label|grep -v grep|wc -l`
if [ $pid_number -eq 0 ]
then
    cd /home/human_label
    python scut_human_label.py >/dev/null 2>&1 &
    echo `date +%Y-%m-%d` `date +%H:%M:%S`  '重启标签人工修改' >>/home/human_label/restart.log
fi
