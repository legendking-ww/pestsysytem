"""
系统资源监控模块
使用 psutil 库监控 CPU、内存、GPU 占用
"""

import psutil
import threading
import time
from datetime import datetime

class ResourceMonitor:
    """系统资源监控类"""
    
    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.current_stats = {
            'cpu_percent': 0,
            'memory_used_mb': 0,
            'memory_percent': 0,
            'gpu_used_mb': 0,
            'timestamp': None
        }
        self.history = []
    
    def start_monitoring(self, interval=1.0):
        """启动资源监控（后台线程）"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("✅ 资源监控已启动")
    
    def stop_monitoring(self):
        """停止资源监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("✅ 资源监控已停止")
    
    def _monitor_loop(self, interval):
        """监控循环"""
        while self.is_monitoring:
            try:
                # CPU占用率
                cpu_percent = psutil.cpu_percent(interval=0.5)
                
                # 内存占用
                memory_info = psutil.Process().memory_info()
                memory_used_mb = memory_info.rss / (1024 * 1024)  # 转换为MB
                memory_percent = psutil.Process().memory_percent()
                
                # GPU占用（如果有显卡）
                gpu_used_mb = self._get_gpu_memory()
                
                self.current_stats = {
                    'cpu_percent': round(cpu_percent, 1),
                    'memory_used_mb': round(memory_used_mb, 0),
                    'memory_percent': round(memory_percent, 1),
                    'gpu_used_mb': gpu_used_mb,
                    'timestamp': datetime.now()
                }
                
                # 记录历史（保留最近60条）
                self.history.append(self.current_stats.copy())
                if len(self.history) > 60:
                    self.history.pop(0)
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"监控错误: {e}")
                time.sleep(interval)
    
    def _get_gpu_memory(self):
        """获取GPU显存占用（MB）"""
        try:
            import subprocess
            # 尝试使用 nvidia-smi 获取显存
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                return int(result.stdout.strip().split('\n')[0])
        except:
            pass
        return 0  # 无GPU或获取失败
    
    def get_current_stats(self):
        """获取当前资源占用"""
        return self.current_stats
    
    def get_average_stats(self):
        """获取平均资源占用"""
        if not self.history:
            return {'cpu_percent': 0, 'memory_used_mb': 0, 'gpu_used_mb': 0}
        
        avg_cpu = sum(s['cpu_percent'] for s in self.history) / len(self.history)
        avg_memory = sum(s['memory_used_mb'] for s in self.history) / len(self.history)
        avg_gpu = sum(s['gpu_used_mb'] for s in self.history) / len(self.history)
        
        return {
            'cpu_percent': round(avg_cpu, 1),
            'memory_used_mb': round(avg_memory, 0),
            'gpu_used_mb': round(avg_gpu, 0)
        }
    
    def get_peak_stats(self):
        """获取峰值资源占用"""
        if not self.history:
            return {'cpu_percent': 0, 'memory_used_mb': 0, 'gpu_used_mb': 0}
        
        peak_cpu = max(s['cpu_percent'] for s in self.history)
        peak_memory = max(s['memory_used_mb'] for s in self.history)
        peak_gpu = max(s['gpu_used_mb'] for s in self.history)
        
        return {
            'cpu_percent': peak_cpu,
            'memory_used_mb': peak_memory,
            'gpu_used_mb': peak_gpu
        }
    
    def get_test_report(self):
        """生成测试报告"""
        avg = self.get_average_stats()
        peak = self.get_peak_stats()
        
        report = f"""
        ========================================
        系统资源占用测试报告
        ========================================
        测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        采样次数: {len(self.history)}
        
        【CPU占用】
          平均: {avg['cpu_percent']}%
          峰值: {peak['cpu_percent']}%
        
        【内存占用】
          平均: {avg['memory_used_mb']} MB
          峰值: {peak['memory_used_mb']} MB
        
        【GPU显存占用】
          平均: {avg['gpu_used_mb']} MB
          峰值: {peak['gpu_used_mb']} MB
        """
        return report
    
    def print_status(self):
        """打印当前状态"""
        stats = self.current_stats
        if stats['timestamp']:
            print(f"\n📊 资源占用 [{stats['timestamp'].strftime('%H:%M:%S')}]")
            print(f"   CPU: {stats['cpu_percent']}%")
            print(f"   内存: {stats['memory_used_mb']} MB")
            print(f"   GPU显存: {stats['gpu_used_mb']} MB")


# 测试代码
if __name__ == '__main__':
    monitor = ResourceMonitor()
    monitor.start_monitoring(interval=1)
    
    print("监控中，按 Ctrl+C 停止...")
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    
    monitor.stop_monitoring()
    print(monitor.get_test_report())