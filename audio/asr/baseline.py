"""faster-whisper"""
from faster_whisper import WhisperModel
import os
import time
import numpy as np

# model_path = '/Users/4paradigm/data/modelscope_hub/angelala00/faster-whisper-small'
# model_path = '/Users/4paradigm/data/model_hub/Systran/faster-whisper-tiny'
# model_path = '/Users/4paradigm//data/modelscope_hub/pengzhendong/faster-whisper-large-v3-turbo'
# model_path = "/Users/4paradigm//data/modelscope_hub/belingud/faster-whisper-tiny.en"
# model_path = "/Users/4paradigm//data/modelscope_hub/belingud/faster-whisper-tiny"
# model_path = "/Users/4paradigm//data/modelscope_hub/pengzhendong/faster-whisper-tiny"
model_path = "/Users/4paradigm/data/model_hub/deepdml/faster-whisper-large-v3-turbo-ct2"
cpu_cuda_flag = int(os.getenv('flag', 0))
device = None
if cpu_cuda_flag == 0:
    device = 'cpu'
else:
    device = 'cuda'
print(f"used device:{device}")
MIN_CHUNK = float(os.environ.get("MIN_CHUNK", 4.5))  # 10
print(f"used min_chunck:{MIN_CHUNK}")

COMPUTE_TYPE = os.environ.get("COMPUTE_TYPE", "int8") # int8
print(f"used compute_type:{COMPUTE_TYPE}")

self_lang = str(os.getenv('lang', 'en'))
print(f"used lang :{self_lang}")

beam_size = int(os.getenv('beam', 1))
print(f"used beam: {beam_size}")
silence_duration = int(os.getenv('silence', 800))
print(f"used silence: {silence_duration}")

model_whisper = WhisperModel(model_size_or_path=model_path, device=device, local_files_only=True,
                             compute_type=COMPUTE_TYPE)
wav_path = '../../data/asr_example.wav'
wav_path = '../../data/warmup.wav'
# wav_path = '../../data/zh_fln.wav'

time_use = []
for i in range(100):
    s_time = time.time()
    segments, info = model_whisper.transcribe(wav_path, language=self_lang,
                                              word_timestamps=True,
                                              beam_size=beam_size,
                                              vad_filter=True,
                                              vad_parameters=dict(min_silence_duration_ms=silence_duration))
    time_use.append(time.time() - s_time)
    print('time usage:', time_use[-1])
for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

print('time_usage:')
print('min:', np.min(time_use))
print('25%:', np.percentile(time_use, 25))
print('50%:', np.percentile(time_use, 50))
print('75%:', np.percentile(time_use, 75))
print('90%:', np.percentile(time_use, 90))
print('max:', np.max(time_use))

"""
-------------------------------------------
angelala00/faster-whisper-small
int8
asr_example.wav en
[0.02s -> 1.96s]  He tried to think how it could be.
time_usage:
min: 0.06117606163024902
25%: 0.06384927034378052
50%: 0.08230996131896973
75%: 0.15500503778457642
90%: 0.1879654884338379
max: 0.19817590713500977

warmup.wav en
[0.00s -> 10.34s]  And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country.
time_usage:
min: 0.09580087661743164
25%: 0.09804713726043701
50%: 0.10058295726776123
75%: 0.1027824878692627
90%: 0.1092793703079224
max: 0.25080084800720215

zh_fln.wav zh
[0.00s -> 3.04s] 既然如此,審判的事就到此結束
[3.80s -> 6.60s] 正義之神可不能冤枉了無罪之人
time_usage:
min: 0.0823981761932373
25%: 0.08517229557037354
50%: 0.08617246150970459
75%: 0.0924978256225586
90%: 0.11961448192596431
max: 0.2337038516998291

int8_float32
time_usage:
min: 0.08170008659362793
25%: 0.08306562900543213
50%: 0.08592045307159424
75%: 0.08765155076980591
90%: 0.111159062385559
max: 0.28929615020751953

-------------------------------------------
Systran/faster-whisper-tiny
time usage: 0.09958028793334961
[0.00s -> 0.66s] 既然如此
[1.26s -> 3.56s] 審判的事就到此结束
[3.82s -> 6.66s] 正一支神可不能愿望了无罪之人
time_usage:
min: 0.08263587951660156
25%: 0.08366161584854126
50%: 0.08455896377563477
75%: 0.09624868631362915
90%: 0.11120636463165279
max: 0.21584105491638184

warmup.wav en
[0.00s -> 10.50s]  And so my fellow Americans ask not what your country can do for you, ask what you can do for your country.
time_usage:
min: 0.09652304649353027
25%: 0.09772086143493652
50%: 0.09916961193084717
75%: 0.1015704870223999
90%: 0.10369932651519775
max: 0.20861101150512695

-------------------------------------------
pengzhendong/faster-whisper-large-v3-turbo
[0.00s -> 10.36s]  And so, my fellow Americans, ask not what your country can do for you, ask what you can do for your country.
time_usage:
min: 0.09595918655395508
25%: 0.09725433588027954
50%: 0.09919106960296631
75%: 0.10078209638595581
90%: 0.1041564702987671
max: 0.22385573387145996

-------------------------------------------
belingud/faster-whisper-tiny.en
[0.00s -> 7.64s]  And so my fellow Americans ask not what your country can do for you
[8.26s -> 10.48s]  ask what you can do for your country.
time_usage:
min: 0.09637212753295898
25%: 0.09827977418899536
50%: 0.10087704658508301
75%: 0.10354846715927124
90%: 0.10950109958648682
max: 0.2982189655303955

-------------------------------------------
belingud/faster-whisper-tiny
[0.00s -> 10.50s]  And so my fellow Americans ask not what your country can do for you, ask what you can do for your country.
time_usage:
min: 0.09685587882995605
25%: 0.09930992126464844
50%: 0.10220873355865479
75%: 0.10480755567550659
90%: 0.11499679088592533
max: 0.21738219261169434

-------------------------------------------
pengzhendong/faster-whisper-tiny
[0.00s -> 10.50s]  And so my fellow Americans ask not what your country can do for you, ask what you can do for your country.
time_usage:
min: 0.09650588035583496
25%: 0.09734994173049927
50%: 0.09816360473632812
75%: 0.10049504041671753
90%: 0.10130431652069091
max: 0.21500802040100098



-------------------------------------------
对比结论75%分位数
angelala00/faster-whisper-small
50%: 0.10058295726776123
75%: 0.1027824878692627

Systran/faster-whisper-tiny
英文句子切分少
50%: 0.09916961193084717
75%: 0.1015704870223999

pengzhendong/faster-whisper-large-v3-turbo，胜出, modelscope
50%: 0.09919106960296631
75%: 0.10078209638595581

belingud/faster-whisper-tiny.en
50%: 0.10087704658508301
75%: 0.10354846715927124

belingud/faster-whisper-tiny
50%: 0.10220873355865479
75%: 0.10480755567550659

pengzhendong/faster-whisper-tiny，胜出
50%: 0.09816360473632812
75%: 0.10049504041671753

deepdml/faster-whisper-large-v3-turbo-ct2
50%: 0.10154199600219727
75%: 0.10563427209854126


"""
