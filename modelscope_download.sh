#!/bin/bash

# 检查是否提供了两个参数
#if [ "$#" -ne 2 ]; then
#    echo "Usage: $0 MODEL LOCAL_DIR"
#    exit 1
#fi

MODEL="pengzhendong/faster-whisper-tiny"
LOCAL_DIR="/Users/4paradigm//data/modelscope_hub/pengzhendong/faster-whisper-tiny"


# 规范化路径，这里使用了～来代表用户的主目录
#LOCAL_DIR=$(echo "$LOCAL_DIR" | sed 's/^~\(\/\?\)/${HOME}\1/')

# 获取 LOCAL_DIR 的绝对路径
#LOCAL_DIR=$(cd "$(dirname "$LOCAL_DIR")"; pwd -P)/$(basename "$LOCAL_DIR")


# 检查 LOCAL_DIR 是否存在
if [ ! -d "$LOCAL_DIR" ]; then
    # 如果 LOCAL_DIR 不存在，则创建它
    mkdir -p "$LOCAL_DIR"
    if [ $? -ne 0 ]; then
        echo "Failed to create directory: $LOCAL_DIR"
        exit 1
    else
        echo "Directory created: $LOCAL_DIR"
    fi
else
    echo "Directory exists: $LOCAL_DIR"
fi

# 执行下载命令
modelscope download --model "$MODEL" --local_dir "$LOCAL_DIR"

# 如果你需要添加错误处理或者更多的逻辑，可以在这里进行扩展