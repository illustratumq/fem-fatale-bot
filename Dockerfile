FROM python:3.10-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBEFFERED=1

WORKDIR /src

COPY . /src

#RUN py app/admin/manage.py runserver
RUN python -m pip install --upgrade pip && python -m pip install --requirement requirements.txt
