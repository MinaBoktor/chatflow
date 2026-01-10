from setuptools import setup, find_packages

setup(
    name="chatflow",
    version="2.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "playwright",
        "opencv-python",
        "numpy",
        "pyautogui",
        "Pillow",
        "pywin32; sys_platform == 'win32'"
    ],
    description="Production-ready WhatsApp Automation Library",
)