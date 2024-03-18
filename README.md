# TraderBot
Build a trader bot which looks makes stock trades by reading news headlines, utilizes AI to gather the sentiment around a stock, and make the judgement whether to invest or not


## Running the project
1. Create a virtual environment `conda create -n trader python=3.10`
2. Activate it `conda activate trader`
3. Install initial dependants `pip install lumibot timedelta alpaca-trade-api==3.1.1`
4. Install transformers `pip install torch torchvision torchaudio transformers`
5. Update the API_KEY and API_SECRET with values from your Alpaca account
6. Run the bot `python tradingbot.py`
   
N.B. Torch installation instructions will vary depending on your operating system and hardware. See here for more: PyTorch Installation Instructions

Utilizes Alpaca trade api and Lumibot to make trades
