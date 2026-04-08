import os
import sys
import subprocess

# 猴子补丁：替换 subprocess.run，拦截 git 命令
original_run = subprocess.run


def patched_run(*args, **kwargs):
    """拦截 git 命令，直接返回空结果"""
    cmd = args[0] if args else kwargs.get('args', [])
    if isinstance(cmd, list) and len(cmd) > 0 and cmd[0] == 'git':
        # 如果是 git 命令，返回一个假的成功结果
        class FakeResult:
            returncode = 0
            stdout = b''
            stderr = b''
        return FakeResult()
    return original_run(*args, **kwargs)


# 应用补丁
subprocess.run = patched_run

# 设置环境变量跳过 git 检查
os.environ['GIT_PYTHON_REFRESH'] = 'quiet'

# 现在导入 ultralytics
import cv2
import time
from ultralytics import YOLO


class ModelService:
    def __init__(self, model_path='models/best1.pt'):
        """初始化模型服务"""
        self.model_path = model_path
        self.model = None
        self.class_names = []
        self.load_model()

    def load_model(self):
        """加载YOLO模型"""
        if not os.path.exists(self.model_path):
            print(f"⚠️ 模型文件不存在: {self.model_path}")
            return

        try:
            self.model = YOLO(self.model_path)
            self.class_names = self.model.names
            print(f"✅ 模型加载成功")
            print(f"   类别数: {len(self.class_names)}")
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")

    def detect_image(self, image_path, conf_threshold=0.25):
        """检测单张图片"""
        if self.model is None:
            return {"error": "模型未加载"}

        if not os.path.exists(image_path):
            return {"error": f"图片不存在: {image_path}"}

        start_time = time.time()

        results = self.model(image_path, conf=conf_threshold)

        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.class_names.get(cls_id, f"未知_{cls_id}")

                detections.append({
                    'class_id': cls_id,
                    'class_name': class_name,
                    'confidence': round(conf, 4)
                })

        # 保存结果图片
        result_img = results[0].plot()
        output_path = f"images/result_{int(time.time())}.jpg"
        os.makedirs('images', exist_ok=True)
        cv2.imwrite(output_path, result_img)

        process_time = round(time.time() - start_time, 2)

        return {
            'success': True,
            'detections': detections,
            'total_count': len(detections),
            'image_path': output_path,
            'process_time': process_time
        }

    def detect_camera_frame(self, frame):
        """检测摄像头帧（CPU优化版）"""
        if self.model is None:
            return frame, []

        # 可选：缩小图片尺寸加速（如果需要进一步优化，取消注释）
        # frame_small = cv2.resize(frame, (320, 320))
        # results = self.model(frame_small, conf=0.25, verbose=False)
        # 然后把检测框坐标映射回原图

        results = self.model(frame, conf=0.25, verbose=False)
        annotated_frame = results[0].plot()

        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.class_names.get(cls_id, f"未知_{cls_id}")
                detections.append({
                    'class_name': class_name,
                    'confidence': round(conf, 4)
                })

        return annotated_frame, detections