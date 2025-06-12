FROM python:3.12-bookworm

WORKDIR /usr/src/app

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./bot.py ./
COPY ./database.py ./
COPY ./scripts/generate_file_ids.py ./scripts/

CMD ["python", "bot.py"]