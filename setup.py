from setuptools import setup

setup(
    name="ai-cli",
    version="1.0",
    py_modules=["ai"],
    install_requires=[
        "Click",
        "requests",
        "bs4",
        "PyPDF2",
        "nltk",
        "transformers",
        "boto3 @ file:///Users/nipalm/Downloads/bedrock-python-sdk/boto3-1.28.21-py3-none-any.whl",
        "botocore @ file:///Users/nipalm/Downloads/bedrock-python-sdk/botocore-1.31.21-py3-none-any.whl",
    ],
    entry_points="""
        [console_scripts]
        ai=ai:cli
    """,
)
