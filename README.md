# CaliBot
# Sistema de Diálogo Hablado para Responder Preguntas Frecuentes de la App de Calificadas

## Integrantes
- Lapertosa Sergio
- Portillo Augusto
- Romero Gilda

## Resumen General del Proyecto

Utilizando los conceptos vistos durante las clases y aprovechando los recursos disponibles, decidimos construir un RAG (Retrieve Augmentation Generative) que permite implementar un **Sistema de Diálogo Hablado** (SDH) basado en un documento de texto que contiene **Preguntas Frecuentes** de la App de Calificadas.

Utilizamos servicios como **OpenAI**, **Azure AI Speech**, **Chroma** y **LangChain** para contar con todas las funcionalidades necesarias para la gestión del SDH.

- [Enlace a la aplicación en Google Play](https://play.google.com/store/apps/details?id=com.calificadas.app)
- [Repositorio en GitHub](https://github.com/portisk8/CaliBot/tree/main/CaliBot/Python/CaliBot/CaliBot)

## Mapeo entre los Conceptos Vistos y las Tecnologías Utilizadas

### Reconocimiento del Habla
- **Servicio de Azure AI Speech**: [Transcribe speech to text](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-to-text)

### Síntesis del Habla
- **Servicio de Azure AI Speech**: [Convert text to speech](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech)

Más información sobre estos servicios se puede encontrar en el siguiente [enlace](https://azure.microsoft.com/en-us/products/ai-services/ai-speech).

### Comprensión y Generación del Lenguaje
Para la **comprensión** y **generación del lenguaje**, utilizamos un modelo LLM, específicamente **gpt-4o-mini**. El contexto del prompt es:

> “You are a helpful and friendly assistant. Use the following information to answer the user's question. If you can't find a specific answer in the provided information say that you don't know.”

Este prompt se encuentra en el archivo de configuración y puede ser modificado según se requiera.

### Administración del Diálogo - Máquina de Estados
Para la administración del diálogo, construimos una aplicación de terminal en Python que utiliza **Microsoft Speech SDK for Python**. Esto nos permite:

- Configurar entrada de audio
- Crear reconocedor de voz
- Crear sintetizador de voz

Las preguntas y respuestas con las que se dialoga se obtienen de una base vectorial en **Chroma**, la cual construimos utilizando el modelo **text-embedding-3-large**.

- Archivo de preguntas frecuentes: `training_data/QuestionAnswer.txt`
- Entrenamiento y recuperación: `rag_trainer.py`

### Flujo del Sistema
Podemos considerar que no hay una máquina de estados con un flujo predeterminado que gestionar, pero podemos representar el funcionamiento de la siguiente manera:

1. **Reconocimiento del Habla**: Conversión de voz a texto.
2. **RAG**: Creación del prompt utilizando embeddings.
3. **Síntesis del Habla**: Conversión de texto a voz.

## Ejecución de la Aplicación

Para ejecutar la aplicación, basta con correr el archivo `CaliBot.py`. Se deben instalar las librerías requeridas mediante:

```bash
pip install -r requirements.txt
```

Librerías necesarias: chromadb, langchain, langchain_community, langchain_openai, azure.cognitiveservices.speech.

Nota: Si es la primera vez que se ejecuta, el parámetro "Train" en appsettings.json debe estar en true. Luego de entrenar, se puede cambiar a false para evitar reentrenamientos.
