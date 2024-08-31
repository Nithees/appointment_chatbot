from setuptools import setup, find_packages

setup(
    name="appointment_booking_project",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "anthropic"
    ],
    entry_points={
        "console_scripts": [
            "run-app = main",
        ],
    },
)
