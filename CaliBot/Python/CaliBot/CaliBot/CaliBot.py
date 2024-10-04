
import azure.cognitiveservices.speech as speechsdk
import json

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from rag_trainer import RAGTrainer

# Cargar configuraci�n
with open('appsettings.json') as config_file:
    config = json.load(config_file)

# Configurar el servicio de voz de Azure
speech_config = speechsdk.SpeechConfig(
    subscription=config['AzureSpeechConfig']['SpeechKey'],
    region=config['AzureSpeechConfig']['SpeechRegion']
)
speech_config.speech_recognition_language = config['AzureSpeechConfig']['SpeechRecognitionLanguage']
speech_config.speech_synthesis_language = config['AzureSpeechConfig']['SpeechSynthesisLanguage']


# Create and train the RAG model
trainer = RAGTrainer(api_key=config['OpenAI']['ApiKey'], embedding_model=config['OpenAI']['EmbeddingModel'])
trainer.train(config['ChromaDB']['TrainingDirectory'])

# Configure the language model
llm = ChatOpenAI(model_name=config['OpenAI']['ChatModel'], openai_api_key=config['OpenAI']['ApiKey'])


# Create a custom prompt template
template = config['OpenAI']['SystemContext']+"""

Context: {context}

Question: {question}

Answer:"""

PROMPT = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

# Create the retrieval and answer chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=trainer.get_retriever(),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)

def answer_question(question):
    result = qa_chain({"query": question})
    answer = result['result']
    sources = [doc.metadata['source'] for doc in result['source_documents']]
    return answer, sources

# Configurar entrada de audio
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

# Crear reconocedor de voz
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# Crear sintetizador de voz
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

def speak_async(text):
    result = speech_synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Hablado: {text}")
    else:
        print(f"Error al hablar: {result.reason}")

# Saludo inicial
speak_async("Hola, soy CaliBot, y seré tu asistente virtual. Dime, ¿qué necesitas?")

while True:
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        user_input = result.text.lower()
        print(f"Reconocido: {user_input}")
        if "salir" in user_input or "terminar" in user_input:
            speak_async("Hasta luego. ¡Que tengas un buen día!")
            break
        else:
            answer, sources = answer_question(user_input)
            speak_async(answer)
    else:
        print(f"Error al reconocer el habla: {result.reason}")