from setuptools import setup, find_packages

# Read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="zajel",
    version="1.0.1",
    author="Mina Boktor",
    author_email="mina.maged.pe@gmail.com",
    keywords=["whatsapp", "automation", "selenium", "playwright", "bot", "opencv", "computer-vision"],
    description="A Computer-Vision powered WhatsApp automation library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MinaBoktor/zajel",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "playwright",
        "opencv-python",
        "pyautogui",
        "Pillow",
        "pywin32; platform_system=='Windows'",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)