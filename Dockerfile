FROM python:3.10-slim
RUN pip install kubernetes
COPY apiserver_monitor.py /apiserver_monitor.py
CMD ["python", "/apiserver_monitor.py"]