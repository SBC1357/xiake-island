"""
兼容旧脚本的入口。

实际服务逻辑已统一到 src.main。
"""
from src.main import app, main, setup_static_serving


setup_static_serving()


if __name__ == "__main__":
    main()
