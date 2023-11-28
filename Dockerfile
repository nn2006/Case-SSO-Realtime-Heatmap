FROM python:3.11.4-alpine3.18

WORKDIR /Case-SSO-Realtime-Heatmap
COPY templates/ /Case-SSO-Realtime-Heatmap/templates/
COPY Data/ /Case-SSO-Realtime-Heatmap/Data/
COPY ./requirements.txt /Case-SSO-Realtime-Heatmap/
COPY ./app.py /Case-SSO-Realtime-Heatmap/
RUN pip install -r requirements.txt

RUN chmod -R 777 /Case-SSO-Realtime-Heatmap/




CMD ["flask", "run", "--host", "0.0.0.0"]