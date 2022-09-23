FROM public.ecr.aws/lambda/python:3.8

COPY requirements.txt ${LAMBDA_TASK_ROOT}
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY .env ${LAMBDA_TASK_ROOT}

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD [ "lambda_function.handler" ]