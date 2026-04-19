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
    def __init__(self, model_path='models/pest_102class_best.pt', cascade_model_path='models/pest_8class_best.pt', use_cascade=True):
        """Initialize model service"""
        self.model_path = model_path
        self.cascade_model_path = cascade_model_path
        self.use_cascade = use_cascade
        self.model = None
        self.cascade_model = None
        self.class_names = []
        self.pest_category_names = []
        # 害虫类别映射表（8类模型输出到具体害虫的映射）
        self.pest_category_map = {
            '水稻害虫': ['稻纵卷叶螟', '稻螟蛉', '稻潜叶蝇', '三化螟', '稻飞虱', '稻蓟马', '稻象甲', '稻水象甲', '稻蝽', '稻蝗', '稻螟', '稻赤斑沫蝉', '稻黑蝽', '稻绿蝽', '稻小潜叶蝇'],
            '玉米害虫': ['亚洲玉米螟', '玉米螟', '夜蛾'],
            '小麦害虫': ['麦二叉蚜', '麦红吸浆虫', '麦叶蜂', '麦长管蚜', '麦圆蜘蛛', '麦叶螨', '麦茎蜂', '麦蚜', '小麦吸浆虫', '小麦叶蜂', '麦蜘蛛'],
            '甜菜害虫': ['蛴螬', '蝼蛄', '金针虫', '甜菜夜蛾', '甜菜象甲', '甜菜根蛆', '甜菜潜叶蝇', '甜菜螟', '甜菜蚜', '甜菜叶蛾'],
            '苜蓿害虫': ['苜蓿叶象甲', '苜蓿夜蛾', '蝗虫', '苜蓿蚜', '苜蓿盲蝽', '苜蓿切叶蜂', '苜蓿籽蜂', '苜蓿蓟马', '苜蓿斑螟', '苜蓿根瘤象', '苜蓿叶蝉', '苜蓿叶甲', '苜蓿蚜茧蜂', '苜蓿食心虫', '苜蓿蛀茎虫', '苜蓿潜叶蝇'],
            '葡萄害虫': ['葡萄根瘤蚜', '葡萄瘿螨', '葡萄透翅蛾', '葡萄斑叶蝉', '葡萄天蛾', '葡萄虎蛾', '葡萄粉蚧', '葡萄短须螨', '葡萄卷叶蛾', '葡萄叶甲', '葡萄叶蝉', '葡萄实蝇', '葡萄瘿蚊', '葡萄根结线虫', '葡萄盾蚧'],
            '柑橘害虫': ['柑橘凤蝶', '柑橘全爪螨', '柑橘大实蝇', '柑橘小实蝇', '柑橘红蜘蛛', '柑橘潜叶蛾', '柑橘木虱', '柑橘粉虱', '柑橘蚜虫', '柑橘介壳虫', '柑橘天牛', '柑橘吉丁虫', '柑橘叶甲', '柑橘瘿螨', '柑橘卷叶蛾', '柑橘吸果夜蛾', '柑橘象甲', '柑橘蝽象', '柑橘锈壁虱'],
            '芒果害虫': ['芒果切叶象甲', '芒果扁喙叶蝉', '芒果果肉象甲', '芒果象甲', '芒果蚜', '芒果瘿蚊', '芒果天牛', '芒果介壳虫', '芒果叶蝉', '芒果夜蛾']
        }
        self.load_model()
        if self.use_cascade:
            self.load_cascade_model()

    def load_model(self):
        """Load YOLO model"""
        if not os.path.exists(self.model_path):
            print(f"⚠️ Model file not found: {self.model_path}")
            return

        try:
            self.model = YOLO(self.model_path)
            self.class_names = self.model.names
            print(f"✅ Model loaded successfully")
            print(f"   Number of classes: {len(self.class_names)}")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")

    def load_cascade_model(self):
        """Load 8-class pest category model"""
        if not os.path.exists(self.cascade_model_path):
            print(f"⚠️ Cascade model file not found: {self.cascade_model_path}")
            self.use_cascade = False
            return

        try:
            self.cascade_model = YOLO(self.cascade_model_path)
            self.pest_category_names = self.cascade_model.names
            print(f"✅ Cascade model loaded successfully")
            print(f"   Number of pest categories: {len(self.pest_category_names)}")
        except Exception as e:
            print(f"❌ Failed to load cascade model: {e}")
            self.use_cascade = False

    def predict_pest_category(self, image):
        """Predict pest category"""
        if not self.use_cascade or self.cascade_model is None:
            return None, 0.0

        try:
            results = self.cascade_model(image, conf=0.5, verbose=False)
            if results and len(results) > 0:
                boxes = results[0].boxes
                if boxes and len(boxes) > 0:
                    # Find pest category with highest confidence
                    max_conf = 0.0
                    best_category = None
                    for box in boxes:
                        conf = float(box.conf[0])
                        cls_id = int(box.cls[0])
                        if conf > max_conf:
                            max_conf = conf
                            # 处理列表或字典类型的names
                            if isinstance(self.pest_category_names, dict):
                                best_category = self.pest_category_names.get(cls_id, f"Unknown_{cls_id}")
                            elif isinstance(self.pest_category_names, list) and cls_id < len(self.pest_category_names):
                                best_category = self.pest_category_names[cls_id]
                            else:
                                best_category = f"Unknown_{cls_id}"
                    return best_category, max_conf
        except Exception as e:
            print(f"❌ Failed to predict pest category: {e}")
        return None, 0.0

    def detect_image(self, image_path, conf_threshold=0.25):
        """Detect pests in a single image"""
        if self.model is None:
            return {"error": "Model not loaded"}

        if not os.path.exists(image_path):
            return {"error": f"Image not found: {image_path}"}

        start_time = time.time()
        category_start_time = time.time()

        # Pest category detection (8-class model)
        pest_category = None
        category_conf = 0.0
        category_index = -1
        warning = None
        if self.use_cascade:
            pest_category, category_conf = self.predict_pest_category(image_path)
            # Get category index if category name exists
            if pest_category and self.pest_category_names:
                if isinstance(self.pest_category_names, dict):
                    for idx, name in self.pest_category_names.items():
                        if name == pest_category:
                            category_index = idx
                            break
                elif isinstance(self.pest_category_names, list):
                    for idx, name in enumerate(self.pest_category_names):
                        if name == pest_category:
                            category_index = idx
                            break
        category_time = round(time.time() - category_start_time, 3)

        pest_start_time = time.time()
        # Pest detection (102-class model)
        results = self.model(image_path, conf=conf_threshold)

        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.class_names.get(cls_id, f"Unknown_{cls_id}")
                bbox = box.xyxy[0].tolist()

                detections.append({
                    'class_id': cls_id,
                    'class_name': class_name,
                    'confidence': round(conf, 4),
                    'bbox': [round(coord, 2) for coord in bbox]
                })
        pest_time = round(time.time() - pest_start_time, 3)

        # Classify pests
        filtered_pests = []
        other_pests = []
        best_match = None
        has_consistent_pest = False
        has_any_pest = len(detections) > 0

        if self.use_cascade and pest_category:
            # Classify pests
            for pest in detections:
                if pest_category in self.pest_category_map:
                    if pest['class_name'] in self.pest_category_map[pest_category]:
                        filtered_pests.append(pest)
                        has_consistent_pest = True
                    else:
                        other_pests.append(pest)
                else:
                    other_pests.append(pest)

            # Find best match
            if detections:
                best_match = max(detections, key=lambda x: x['confidence'])

            # Generate warning if no consistent pest but has pests
            if not has_consistent_pest and has_any_pest:
                if best_match:
                    warning = f"Warning: Detected pest {best_match['class_name']} may not match pest category {pest_category}, please review"
        else:
            # Standard mode - all pests are in other_pests
            other_pests = detections
            if detections:
                best_match = max(detections, key=lambda x: x['confidence'])

        # Save result image
        result_img = results[0].plot()
        output_path = f"images/result_{int(time.time())}.jpg"
        os.makedirs('images', exist_ok=True)
        cv2.imwrite(output_path, result_img)

        process_time = round(time.time() - start_time, 3)

        result = {
            'success': True,
            'detections': detections,
            'total_count': len(detections),
            'image_path': output_path,
            'process_time': process_time
        }

        # Add cascade inference results
        if self.use_cascade:
            result['cascade'] = {
                'pest_category': {
                    'name': pest_category,
                    'confidence': round(category_conf, 4),
                    'index': category_index
                },
                'pests': {
                    'filtered': filtered_pests,
                    'others': other_pests,
                    'all': detections
                },
                'best_match': best_match,
                'has_consistent_pest': has_consistent_pest,
                'has_any_pest': has_any_pest,
                'inference_time': {
                    'total': process_time,
                    'category': category_time,
                    'pest': pest_time
                }
            }
            if warning:
                result['warning'] = warning

        return result

    def detect_camera_frame(self, frame):
        """Detect pests in camera frame (CPU optimized)"""
        if self.model is None:
            return frame, []

        # Pest category detection
        pest_category = None
        category_conf = 0.0
        warning = None
        if self.use_cascade:
            pest_category, category_conf = self.predict_pest_category(frame)

        # Pest detection
        results = self.model(frame, conf=0.25, verbose=False)
        annotated_frame = results[0].plot()

        # Create a writable copy of the frame
        annotated_frame = annotated_frame.copy()

        # Draw pest category information in the format "水稻害虫 0.95"
        if self.use_cascade and pest_category:
            # 显示害虫类别和置信度
            category_text = f"{pest_category}"
            confidence_text = f"Confidence: {category_conf:.2f}"
            cv2.putText(annotated_frame, category_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(annotated_frame, confidence_text, (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Check for consistency
            detections = []
            has_consistent_pest = False
            best_pest = None
            best_conf = 0.0
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = self.class_names.get(cls_id, f"Unknown_{cls_id}")
                    detections.append({
                        'class_name': class_name,
                        'confidence': round(conf, 4)
                    })
                    # Check if this pest is consistent with the category
                    if pest_category in self.pest_category_map:
                        if class_name in self.pest_category_map[pest_category]:
                            has_consistent_pest = True
                    # Find best pest
                    if conf > best_conf:
                        best_conf = conf
                        best_pest = class_name
            
            # 显示最佳匹配害虫
            if best_pest:
                best_pest_text = f"Best Match: {best_pest}"
                best_conf_text = f"Confidence: {best_conf:.2f}"
                cv2.putText(annotated_frame, best_pest_text, (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
                cv2.putText(annotated_frame, best_conf_text, (10, 115),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
            
            # Draw warning if inconsistent
            if not has_consistent_pest and detections:
                warning_text = "⚠️ Inconsistent: Pest does not match category"
                cv2.putText(annotated_frame, warning_text, (10, 145),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        else:
            # Standard mode
            detections = []
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = self.class_names.get(cls_id, f"Unknown_{cls_id}")
                    detections.append({
                        'class_name': class_name,
                        'confidence': round(conf, 4)
                    })

        return annotated_frame, detections