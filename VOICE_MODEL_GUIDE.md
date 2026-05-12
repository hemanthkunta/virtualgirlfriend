# Custom Voice Model Development Guide

This guide will walk you through setting up a completely custom AI voice for your Virtual Girlfriend, using your own voice or a voice actor (such as a "cute Indian girl's voice with Hyderabadi slang").

We are using **Coqui XTTSv2**, the state-of-the-art open-source text-to-speech engine. Unlike older models that require hours of audio and days of training, XTTSv2 can perform **zero-shot voice cloning**. This means it can generate a highly realistic voice model using just a **single 5 to 10-second reference audio clip**.

## Step 1: Install Dependencies

The engine requires the `TTS` library to run locally. Ensure your virtual environment is activated and install it:

```bash
# Activate your environment
source .venv/bin/activate  # Or your respective activation command

# Install the TTS library and its dependencies
pip install TTS soundfile
```

## Step 2: Record Your Reference Audio

To get the perfect "Hyderabadi slang" and "cute tone", you need to record a short audio clip. The quality of this clip determines the quality of the AI's generated voice.

**Guidelines for the perfect recording:**
1. **Length:** Keep it between **5 and 10 seconds**. (Do not make it too long).
2. **Quality:** Record in a quiet room with no background noise or echo.
3. **Tone & Slang:** Speak exactly in the way you want the AI to speak. If you want a cute Hyderabadi slang, the reference audio **MUST** contain that exact accent, tone, and slang. The AI will mimic the emotion and accent perfectly.
4. **Format:** Save the file as a `.wav` file.

*Example script to read out loud:*
> "Arre yaar, I was waiting for you! Ekdum mast lag rahe ho aaj. Chalo, let's go do something fun!"

## Step 3: Add the Audio to the Project

1. Rename your recording to `reference_voice.wav`.
2. Place it in the `custom_voice` folder located in the root of your project:
   `virtualgirlfriend/custom_voice/reference_voice.wav`

## Step 4: Run the App

That's it! When you start the application (`python app.py`), the `tts_engine.py` will automatically detect `reference_voice.wav` and switch from the default TTS to your custom Coqui XTTS model. 

*Note: The first time you run this, it will download the XTTSv2 model (around 2-3 GB). Please be patient. On subsequent runs, it will load instantly.*

## Troubleshooting

- **Voice doesn't sound right:** Ensure the reference audio is clean. Try a different 10-second clip with more emphasis on the slang.
- **Model takes too long to generate:** Voice cloning is computationally intensive. If you have an Apple Silicon Mac (M1/M2/M3), it will use the GPU (MPS). If it's too slow, ensure `torch` is correctly installed for your hardware.
- **Out of Memory Error:** Ensure you have at least 8GB of free RAM.

## Advanced Fine-Tuning (Optional)

If the zero-shot cloning is not sufficient and you want to explicitly train the model on a large dataset (1-2 hours of audio):
1. You will need to create a dataset using LJSpeech format (a folder of wavs and a `metadata.csv` mapping files to transcripts).
2. Use the Coqui TTS trainer recipes. However, for 99% of use-cases, XTTSv2's zero-shot cloning provides better and faster results for specific accents like Hyderabadi slang!
