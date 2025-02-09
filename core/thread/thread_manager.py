# =================
# 线程管理器
# Version: 1.0.0
# =================
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, Optional, Dict
from core.log.log_manager import log
import threading
import queue
import time
import psutil
import os


class ThreadManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ThreadManager, cls).__new__(cls)
            return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.max_workers = self._calculate_optimal_thread_count()
            self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
            self.tasks: Dict[str, Future] = {}
            self.task_queue = queue.Queue()
            self.results = {}
            self.task_stats = {}
            self.initialized = True
            self._start_monitoring()
            log.info(f"线程管理器初始化完成，当前线程数: {self.max_workers}")
    
    def _calculate_optimal_thread_count(self) -> int:
        cpu_count = psutil.cpu_count(logical=True)
        memory = psutil.virtual_memory()
        
        # 基础线程数：CPU核心数 * 2
        base_threads = cpu_count * 2
        
        # 根据内存使用情况调整
        memory_factor = 1.0
        if memory.percent > 80:
            memory_factor = 0.5
        elif memory.percent > 60:
            memory_factor = 0.7
        
        optimal_threads = int(base_threads * memory_factor)
        return max(4, min(optimal_threads, 256))
    
    def _start_monitoring(self):
        def monitor():
            while True:
                try:
                    self._adjust_thread_pool()
                    time.sleep(30)
                except Exception as e:
                    log.error(f"线程池监控异常: {str(e)}")
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def _adjust_thread_pool(self):
        active_tasks = len([t for t in self.tasks.values() if not t.done()])
        current_workers = self.executor._max_workers
        optimal_count = self._calculate_optimal_thread_count()
        
        # 根据任务负载调整线程数
        if active_tasks > current_workers * 0.8:
            new_workers = min(current_workers * 2, 256)
        elif active_tasks < current_workers * 0.2:
            new_workers = max(current_workers // 2, optimal_count)
        else:
            new_workers = optimal_count
        
        if new_workers != current_workers:
            log.info(f"调整线程池大小: {current_workers} -> {new_workers}")
            new_executor = ThreadPoolExecutor(max_workers=new_workers)
            old_executor = self.executor
            self.executor = new_executor
            old_executor.shutdown(wait=False)

    def submit_task(self, task_id: str, func: Callable, *args, **kwargs) -> Future:
        try:
            self.task_stats[task_id] = {
                'start_time': time.time(),
                'status': 'running'
            }
            
            def wrapped_func(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    self.task_stats[task_id]['status'] = 'completed'
                    self.task_stats[task_id]['end_time'] = time.time()
                    return result
                except Exception as e:
                    self.task_stats[task_id]['status'] = 'failed'
                    self.task_stats[task_id]['error'] = str(e)
                    raise
            
            future = self.executor.submit(wrapped_func, *args, **kwargs)
            self.tasks[task_id] = future
            log.debug(f"提交任务: {task_id}")
            return future

        except Exception as e:
            log.error(f"提交任务失败 {task_id}: {str(e)}")
            raise
    
    def run_in_thread(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            return self.submit_task(
                f"task_{time.time()}_{threading.get_ident()}", 
                func, 
                *args, 
                **kwargs
            )
        return wrapper
    
    def get_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        try:
            if task_id in self.tasks:
                return self.tasks[task_id].result(timeout=timeout)
            return None
        except Exception as e:
            log.error(f"获取任务结果失败 {task_id}: {str(e)}")
            return None
    
    def cancel_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            self.task_stats[task_id]['status'] = 'cancelled'
            return self.tasks[task_id].cancel()
        return False
    
    def is_task_running(self, task_id: str) -> bool:
        return task_id in self.tasks and not self.tasks[task_id].done()
    
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> bool:
        try:
            if task_id in self.tasks:
                self.tasks[task_id].result(timeout=timeout)
                return True
            return False
        except Exception:
            return False
    
    def get_task_stats(self, task_id: str = None) -> Dict:
        if task_id:
            return self.task_stats.get(task_id)
        return self.task_stats
    
    def shutdown(self, wait: bool = True):
        try:
            self.executor.shutdown(wait=wait)
            log.info("线程管理器关闭")
        except Exception as e:
            log.error(f"线程管理器关闭失败: {str(e)}")

# 全局实例
thread_manager = ThreadManager() 