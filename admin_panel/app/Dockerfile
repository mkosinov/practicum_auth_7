FROM python:3.12

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && \
    apt-get install --no-install-recommends -y gettext && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /usr/src/app
COPY . .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN chmod +x run_entrypoint.sh    
RUN python manage.py compilemessages
RUN useradd -u 8000 uwsgi-user
ENTRYPOINT [ "/usr/src/app/run_entrypoint.sh" ]