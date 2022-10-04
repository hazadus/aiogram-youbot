import os
import uuid
import logging

from aiogram import types, Dispatcher
from aiogram.utils.exceptions import NetworkError
from pytube import YouTube

from spawn_bot import bot


async def command_start(message: types.Message):
    # noinspection PyBroadException
    try:
        await bot.send_message(message.from_user.id,
                               'Этот бот умеет качать и отправлять вам видосы с ютуба. '
                               'Киньте ссылку на видео в директ, в ответ получите видос.\n'
                               'Ограничение Telegram API на засылку видоса ботом – 50 Мб, поэтому '
                               'качаю в самом низком разрешении.')
        await message.delete()
    except:
        await message.reply('Этот бот умеет качать и отправлять вам видосы с ютуба. Пишите ему в директ!')


async def download_video(url: str, message: types.Message):
    yt = YouTube(url)
    output_filename = f'{message.from_user.id}_{uuid.uuid1()}.mp4'

    stream = yt.streams.filter(progressive=True, file_extension='mp4')
    # stream.get_highest_resolution().download(filename=output_filename)
    stream.get_lowest_resolution().download(filename=output_filename)

    logging.info(f'Video saved to file {output_filename}')

    with open(output_filename, 'rb') as video:
        try:
            await message.answer_video(video, caption=f'Ваше видео: {yt.title}')
            logging.info(f'Video {output_filename} sent to @{message.from_user.username} ({message.from_user.id})')
        except NetworkError:
            await message.answer('Слишком большое видео! Могу отправить только до 50 Мб (ограничение Telegram API)')
            logging.info(f'Video {output_filename} too large to send.')
        finally:
            os.remove(output_filename)


async def message_youtube_link(message: types.Message):
    yt = YouTube(message.text)
    log_text = f'User @{message.from_user.username} sent video "{yt.title}", link: {message.text}'
    await message.answer(f'Начинаю качать *{yt.title.replace("*", "")}* с канала: "{yt.author}". '
                         f'Наберитесь терпения!',
                         parse_mode='Markdown')
    await bot.send_message(os.getenv('BOT_ADMIN'), log_text)
    logging.info(log_text)
    await download_video(message.text, message)


async def any_message(message: types.Message):
    logging.info(f'"@{message.from_user.username}" id={message.from_user.id} chat_id:{message.chat.id}: {message.text}')
    await message.answer('Лучше пришлите ссылку на видос с ютубчика!')


def filter_youtube_link(message: types.Message):
    return message.text.startswith('https://www.youtube.com/') or message.text.startswith('https://youtu.be/')
    # return message.chat.type == 'private' and \
    #        (message.text.startswith('https://www.youtube.com/') or message.text.startswith('https://youtu.be/'))


def register_client_handlers(disp: Dispatcher):
    disp.register_message_handler(command_start, commands=['start', 'help'])
    disp.register_message_handler(message_youtube_link, filter_youtube_link)
    # Any message to bot/chat. Must be last in order of handlers!
    disp.register_message_handler(any_message, lambda message: message.chat.type == 'private')

