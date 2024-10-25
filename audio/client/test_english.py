import json
import os
import ssl
import sys
import threading
import time
import traceback
from loguru import logger

import websocket
from websocket import create_connection


class Client:
    def __init__(self, sut_url: str, data_info: dict) -> None:
        # base_url = "ws://127.0.0.1:5003"
        self.base_url = "ws://localhost:5003/recognition"
        # 和数据集的语音又关系，如果数据集每一条没有配置，则采用榜单默认的配置
        self.chunk_size = os.getenv('chunk_size', 3200)
        self.wait_time = os.getenv('wait_time', 0.1)
        self.data_info = data_info
        self.exception = False
        self.close_time = None
        self.send_time = []
        self.recv_time = []
        self.predict_data = []

    def action(self):
        # 初始化连接
        self._connect_init()
        # 创建接收线程
        self.trecv = threading.Thread(target=self._recv)
        self.trecv.start()
        # 发送数据
        self._send()
        self._close()
        # 生成结果
        return self._gen_result()

    def _connect_init(self):
        # 设置超时时间为 5 秒
        end_time = time.time() + 5
        success = False
        try:
            self.ws = create_connection(self.base_url)
            # 发送初始参数，告知有当前要识别语言。
            self.ws.send(json.dumps({"parameter": {"lang": self.data_info["lang"]}}))
            while time.time() < end_time and not success:
                data = self.ws.recv()
                if len(data) == 0:
                    time.sleep(1)
                    continue
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except Exception:
                        logger.info(data)
                        logger.info("初始化阶段，数据不是 json 字符串格式，终止流程")
                        exit(-1)
                if isinstance(data, dict):
                    success = data.get("success", False)
                    if not success:
                        logger.info(f"初始化失败，返回的结果为 {data}，终止流程")
                    else:
                        break
                logger.info("初始化阶段，数据不是 json 字符串格式，终止流程")
                exit(-1)
        except websocket.WebSocketConnectionClosedException:
            logger.info("初始化阶段连接中断，终止流程")
            exit(-1)
        if not success:
            logger.info("初始化阶段 2s 没有返回数据，时间太长，终止流程")
            exit(-1)

    def _send(self):
        """
        // 平台方发送字节数据 （bytes 数据）
        b'xxxxxxxxxxxx'
        """
        # 读取 WAV 文件
        with open(self.data_info['file'], 'rb') as fp:
            wav_data = fp.read()
            meta_length = wav_data.index(b'data') + 8

        try:
            with open(self.data_info['file'], 'rb') as fp:
                # 去掉 wav 文件的头信息
                fp.read(meta_length)
                # 正文内容
                while True:
                    chunk = fp.read(self.chunk_size)
                    if not chunk:
                        break
                    self.ws.send(chunk, websocket.ABNF.OPCODE_BINARY)
                    self.send_time.append(time.perf_counter())
                    time.sleep(self.wait_time)
            logger.info("当条语音数据发送完成")
            self.ws.send(json.dumps({'end': True}))
            logger.info("2s 后关闭双向连接.")
            self.close_time = time.perf_counter() + 2
        except Exception:
            logger.info("发送数据失败")
            exit(-1)

    def _recv(self):
        """
        测试方自行决定要合适返回
        返回时要返回下面的形式  （ json.dumps 转成 str 发送 ）
        需要多返回3个字段start_time，end_time，words，以下是一个样例
        {
          "recognition_results": {
            "text": "最先启动的还是",
            "final_result": false,
            "sentence_seq": 0, //"para_seq": 0,
            "start_time": 6300,
            "end_time": 6421,
            "words": [
                {
                    "text": "最",
                    "start_time": 6300,
                    "end_time": 6321,
                },
                {
                    "text": "先",
                    "start_time": 6321,
                    "end_time": 6345,
                },
                {
                    "text": "启动",
                    "start_time": 6345,
                    "end_time": 6370,
                },
                 {
                    "text": "的",
                    "start_time": 6370,
                    "end_time": 6386,
                },
                 {
                    "text": "还是",
                    "start_time": 6386,
                    "end_time": 6421,
                }
            ]
          }
        }
        """
        try:
            while self.ws.connected:
                recv_data = self.ws.recv()
                if isinstance(recv_data, str):
                    if recv_data := str(recv_data):
                        recv_data = json.loads(recv_data)
                        if (
                                "recognition_results" not in recv_data
                                or "final_result" not in recv_data["recognition_results"]
                                or "text" not in recv_data["recognition_results"]
                        ):
                            logger.info(f"返回内容缺少必要属性，当前的返回内容是 {recv_data}")
                            continue
                        self.recv_time.append(time.perf_counter())
                        self.predict_data.append(recv_data)
                        logger.info(f"recv_data {recv_data}")
                else:
                    self.exception = True
                    raise Exception("返回的结果不是字符串形式")
        except websocket.WebSocketConnectionClosedException:
            pass
        except Exception:
            traceback.print_exc()
            logger.info("处理被测服务返回数据时出错")
            self.exception = True
            sys.exit(-1)

    def _close(self):
        while time.perf_counter() < self.close_time and not self.exception:
            time.sleep(1)
        try:
            self.ws.close()
        except Exception:
            pass

    def _gen_result(self) -> tuple:
        return {
            "send_time": self.send_time,
            "recv_time": self.recv_time,
            "predict_data": self.predict_data,
        }


if __name__ == "__main__":
    Client(
        None,
        {
            "lang": "en",
            "file": "converted.wav",
        },
    ).action()
