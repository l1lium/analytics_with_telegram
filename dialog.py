import os
import db_utils as db
import torch
import telebot
import pandas as pd
import matplotlib.pyplot as plt
from transformers import AutoModelForCausalLM, AutoTokenizer

# Read DB
df = db.read_db()

# Settings for LLM
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-large", padding_side='left')
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-large")
chat_history_ids = torch.tensor([[0]])
step = 0

# Settings for Telegram Bot
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Nice to talk with you!")


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    chat_id = message.chat.id
    global chat_history_ids, step

    # encode the new user input, add the eos_token and return a tensor in Pytorch
    new_user_input_ids = tokenizer.encode(message.text + tokenizer.eos_token, return_tensors='pt')

    # append the new user input tokens to the chat history
    bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

    # generated a response while limiting the total chat history to 1000 tokens,
    chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

    # pretty print last ouput tokens from bot
    output_text = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

    # conversation flow
    try:
        if 'plot for' in message.text:
            mes_text = message.text.split()
            columns = [i for i in mes_text if i in list(df.head())]
            df[columns].plot()
            plt.savefig('imgs/plot.png')
            bot.reply_to(message, "Look at the plot for chosen columns")
            bot.send_photo(chat_id, photo=open('imgs/plot.png', 'rb'))

        elif 'plot' in message.text:
            df.plot()
            plt.savefig('imgs/plot.png')
            bot.reply_to(message, "Please, see at a plot of the database")
            bot.send_photo(chat_id, photo=open('imgs/plot.png', 'rb'))

        elif 'bar for' in message.text:
            mes_text = message.text.split()
            columns = [i for i in mes_text if i in list(df.head())]
            df[columns].plot.bar()
            plt.savefig('imgs/bar.png')
            bot.reply_to(message, "Look at the bar plot for chosen columns")
            bot.send_photo(chat_id, photo=open('imgs/bar.png', 'rb'))

        elif 'bar' in message.text:
            df.plot.bar()
            plt.savefig('imgs/bar.png')
            bot.reply_to(message, "Please, see at the bar plot of the database")
            bot.send_photo(chat_id, photo=open('imgs/bar.png', 'rb'))

        elif 'box for' in message.text:
            mes_text = message.text.split()
            columns = [i for i in mes_text if i in list(df.head())]
            df[columns].plot.box()
            plt.savefig('imgs/box.png')
            bot.reply_to(message, "Look at the box plot for chosen columns")
            bot.send_photo(chat_id, photo=open('imgs/box.png', 'rb'))

        elif 'box' in message.text:
            df.plot.box()
            plt.savefig('imgs/box.png')
            bot.reply_to(message, "Please, see at the box plot of the database")
            bot.send_photo(chat_id, photo=open('imgs/box.png', 'rb'))

        elif 'histogram for' in message.text:
            mes_text = message.text.split()
            columns = [i for i in mes_text if i in list(df.head())]
            df[columns].hist(bins=10)
            plt.savefig('imgs/histogram.png')
            bot.reply_to(message, "Look at the histogram for chosen columns")
            bot.send_photo(chat_id, photo=open('imgs/histogram.png', 'rb'))

        elif 'histogram' in message.text:
            df.hist(bins=10)
            plt.savefig('imgs/histogram.png')
            bot.reply_to(message, "Please, see at the histogram of the database")
            bot.send_photo(chat_id, photo=open('imgs/histogram.png', 'rb'))

        elif 'read database' in message.text or 'read db' in message.text:
            df = db.read_db()
            bot.reply_to(message, "Here is information about database: \n" + str(df.describe()))
            bot.reply_to(message, "Database is being read")

        elif 'data attributes' in message.text or 'show data attributes' in message.text:
            bot.reply_to(message, "Here is a list of data attributes: " + str(list(df.head())))

        elif 'types of charts' in message.text or 'of charts' in message.text:
            bot.reply_to(message, "I can show you: simple plot, bar plot, box plot and histogram")

        elif message.text:
            bot.reply_to(message, output_text)

    except Exception as e:
        bot.reply_to(message, e)
    step += 1

bot.infinity_polling()
