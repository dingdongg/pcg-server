FROM python:3.10-alpine
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

# 0.0.0.0 is needed, because I don't know which IP address
# this container will be assigned ahead of time.
# So, gunicorn will listen on all incoming connections outside 
# of the docker network
# CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:9000", "app:app"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9000"]