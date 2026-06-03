cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="holiday_bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "workalendar>=16.3.0",
        "requests>=2.25.0",
    ],
)
EOF