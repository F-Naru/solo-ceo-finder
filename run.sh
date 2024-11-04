#!/bin/bash

# 200,000件ごとに分割し、6つのスレッドで実行する
BATCH_SIZE=200000

for i in {0..5}
do
  START=$((i * BATCH_SIZE))
  END=$(((i + 1) * BATCH_SIZE))
  THREAD_NUM=$((i + 1))
  
  # Pythonスクリプトをバックグラウンドで実行し、START, END, THREAD_NUMを渡す
  python my_script.py $START $END $THREAD_NUM &
done

# すべてのバックグラウンドジョブが終了するのを待機
wait
