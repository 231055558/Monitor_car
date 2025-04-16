from picamera2 import Picamera2
import time
import numpy as np
import cv2
import os
from datetime import datetime

def main():
    # 初始化摄像头
    picam2 = Picamera2()
    
    # 配置摄像头
    camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(camera_config)
    
    # 启动摄像头
    picam2.start()
    
    # 创建保存图片的目录
    save_dir = "camera_images"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    print("摄像头已启动，按 Ctrl+C 退出程序")
    
    try:
        while True:
            # 捕获图像
            frame = picam2.capture_array()
            
            # 打印图像信息
            print(f"图像形状: {frame.shape}")
            print(f"图像类型: {frame.dtype}")
            print(f"图像值范围: [{frame.min()}, {frame.max()}]")
            
            # 保存图像为PNG格式
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = os.path.join(save_dir, f"image_{timestamp}.png")
            cv2.imwrite(filename, frame)
            print(f"已保存图片: {filename}")
            
            # 短暂延时以减少CPU使用
            time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    finally:
        # 清理资源
        picam2.stop()

if __name__ == "__main__":
    main() 