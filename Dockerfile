# base image  
FROM python:3.8   
 
ENV APP_DIR=/app/webapp   
RUN mkdir -p $APP_DIR  
WORKDIR $APP_DIR  

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

RUN pip install --upgrade pip  


COPY ./requirements.txt $APP_DIR 
RUN pip install -r requirements.txt

COPY . $APP_DIR
# port where the Django app runs  
EXPOSE 8000  
# start server  
#CMD python manage.py runserver 0.0.0.0:8000 
CMD gunicorn NaaS_Tracker_v17:server --bind 0.0.0.0:8000