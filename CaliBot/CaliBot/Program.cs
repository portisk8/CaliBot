// See https://aka.ms/new-console-template for more information
using Microsoft.CognitiveServices.Speech.Audio;
using Microsoft.CognitiveServices.Speech;
using CaliBot.Bot;
using Microsoft.Extensions.Configuration;

Console.WriteLine("Hello, World!");

IConfiguration config = new ConfigurationBuilder()
            .AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
            .Build();

var speechConfig = SpeechConfig.FromSubscription(
    config["AzureSpeechConfig:SpeechKey"],
    config["AzureSpeechConfig:SpeechRegion"]);

speechConfig.SpeechRecognitionLanguage = config["AzureSpeechConfig:SpeechRecognitionLanguage"];
speechConfig.SpeechSynthesisLanguage = config["AzureSpeechConfig:SpeechSynthesisLanguage"];

using var audioConfig = AudioConfig.FromDefaultMicrophoneInput();
using var speechRecognizer = new SpeechRecognizer(speechConfig, audioConfig);
var speak = new Speak(speechConfig);

await speak.SpeakAsync("Hola, soy CaliBot, y seré tu asistente virtual. Dime, ¿qué necesitas?");

while (true)
{

    var result = await speechRecognizer.RecognizeOnceAsync();
    if (result.Reason == ResultReason.RecognizedSpeech)
    {
        string userInput = result.Text.ToLower();
        Console.WriteLine($"Reconocido: {userInput}");

        if (userInput.Contains("clima") || userInput.Contains("tiempo"))
        {
            // Aquí iría la lógica para obtener el clima
            await speak.SpeakAsync("Lo siento, aún no puedo proporcionar información del clima. Esta función está en desarrollo.");
        }
        else if (userInput.Contains("salir") || userInput.Contains("terminar"))
        {
            await speak.SpeakAsync("Hasta luego. ¡Que tengas un buen día!");
            break;
        }
        else
        {
            await speak.SpeakAsync("Lo siento, no entendí tu solicitud. ¿Puedes repetirla?");
        }
    }
    else
    {
        Console.WriteLine($"Error al reconocer el habla: {result.Reason}");
    }
}