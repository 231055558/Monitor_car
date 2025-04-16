from picamera2 import Picamera2
import time
import numpy as np
import cv2

def main():
    # 初始化摄像头
    picam2 = Picamera2()
    
    # 配置摄像头
    camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(camera_config)
    
    # 启动摄像头
    picam2.start()
    
    print("摄像头已启动，按 Ctrl+C 退出程序")
    print("按 'q' 键退出程序")
    
    try:
        while True:
            # 捕获图像
            frame = picam2.capture_array()
            
            # 显示图像
            cv2.imshow("Camera Feed", frame)
            
            # 检查是否按下 'q' 键退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # 打印图像形状
            print(f"图像形状: {frame.shape}")
            
            # 短暂延时以减少CPU使用
            time.sleep(0.03)
                
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    finally:
        # 清理资源
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 