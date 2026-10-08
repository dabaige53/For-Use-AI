"""Chinese labels for the shared GPU parallelism animation."""

from reconstruction_gpu import Parallelizability


class ParallelizabilityChinese(Parallelizability):
    input_label = "输入"
    output_label = "输出"
    gpu_label = "GPU（图形处理器）"
    text_kwargs = {"font": "PingFang SC"}
    gpu_text_kwargs = {"font": "PingFang SC", "font_size": 30}
