from setuptools import setup, find_packages

setup(
    name="chatflow",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "playwright",
        "opencv-python",
        "numpy",
        "pyautogui",
        "Pillow",
        "pywin32; sys_platform == 'win32'"
    ],
    author="Mina Maged",
    description="A robust WhatsApp Web automation library using Playwright and Computer Vision.",
    python_requires='>=3.8',
)