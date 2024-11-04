#!/bin/bash

# 200,000件ごとに分割し、6つのスレッドで実行する
BATCH_SIZE=200000

# venv環境のパスを指定
VENV_DIR="venv"  # 仮想環境のディレクトリ名が「venv」の場合

for i in {0..5}
do
  START=$((i * BATCH_SIZE))
  END=$(((i + 1) * BATCH_SIZE))
  THREAD_NUM=$((i + 1))
  
  # screenセッションを作成し、仮想環境をアクティブにしてPythonスクリプトを実行
  screen -dmS "thread_$THREAD_NUM" bash -c "
    source $VENV_DIR/bin/activate;
    python3 main.py $START $END $THREAD_NUM;
    deactivate;
    exec bash"
done

echo "すべてのスレッドが仮想環境内でscreenセッションにより開始されました。"
