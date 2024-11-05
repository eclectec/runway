FROM python:3.10

COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy

WORKDIR /code
RUN mkdir -p /code/files

COPY ./app /code/app
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]