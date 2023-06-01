FROM python:3.9
WORKDIR ./
COPY ./requirement.txt ./requirement.txt
RUN pip install -r requirement.txt
COPY ./create_pod_v6.py ./create_pod_v6.py
CMD ["python3","./create_pod_v6.py"]
