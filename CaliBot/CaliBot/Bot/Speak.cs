using Microsoft.CognitiveServices.Speech;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CaliBot.Bot
{
    public class Speak
    {
        private readonly SpeechSynthesizer _speechSynthesizer;

        public Speak(SpeechConfig speechConfig)
        {
            _speechSynthesizer = new SpeechSynthesizer(speechConfig);
        }

        public async Task SpeakAsync( string text)
        {
            var result = await _speechSynthesizer.SpeakTextAsync(text);
            if (result.Reason != ResultReason.SynthesizingAudioCompleted)
            {
                Console.WriteLine($"Error en la síntesis de voz: {result.Reason}");
            }
        }
    }
}
