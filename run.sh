#!/bin/bash

# 200,000件ごとに分割し、6つのスレッドで実行する
BATCH_SIZE=200000

for i in {0..5}
do
  START=$((i * BATCH_SIZE))
  END=$(((i + 1) * BATCH_SIZE))
  THREAD_NUM=$((i + 1))
  
  # screenセッションを作成し、Pythonスクリプトを実行
  screen -dmS "thread_$THREAD_NUM" bash -c "python3 main.py $START $END $THREAD_NUM; exec bash"
done

echo "すべてのスレッドがscreenセッションで開始されました。"
