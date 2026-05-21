FROM python

WORKDIR /gestionale_eventi

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app.py ./app.py
COPY ./models.py ./models.py
COPY ./routes.py ./routes.py
COPY ./templates ./templates
COPY ./static ./static
COPY ./migrations ./migrations
COPY ./entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
