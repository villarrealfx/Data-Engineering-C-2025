FROM openjdk:11-jdk-slim

# Instalar dependencias
RUN apt-get update && apt-get install -y python3 python3-pip wget

# Descargar y extraer Spark
RUN wget https://dlcdn.apache.org/spark/spark-3.4.4/spark-3.4.4-bin-hadoop3.tgz && \
    tar -xzf spark-3.4.4-bin-hadoop3.tgz -C /opt && \
    mv /opt/spark-3.4.4-bin-hadoop3 /opt/spark

# Configurar variables de entorno
ENV SPARK_HOME /opt/spark
ENV PATH $SPARK_HOME/bin:$PATH
ENV PYSPARK_PYTHON python3
ENV PYSPARK_DRIVER_PYTHON python3

# Instalar PySpark
RUN pip3 install pyspark jupyter notebook

# Configurar Jupyter Notebook para permitir acceso remoto (opcional, pero recomendado)
RUN jupyter notebook --generate-config

# Configurar Jupyter Notebook para permitir acceso remoto sin token (para desarrollo local, no para producción)
RUN echo "c.NotebookApp.token = ''" >> /root/.jupyter/jupyter_notebook_config.py
RUN echo "c.NotebookApp.password = ''" >> /root/.jupyter/jupyter_notebook_config.py
RUN echo "c.NotebookApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_notebook_config.py
RUN echo "c.NotebookApp.allow_root = True" >> /root/.jupyter/jupyter_notebook_config.py

# Exponer el puerto de Jupyter Notebook
EXPOSE 8888

# Comando para iniciar Jupyter Notebook
CMD ["jupyter", "notebook", "--allow-root"]
