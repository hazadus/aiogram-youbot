import os
import uuid
import logging
import subprocess
from urllib.error import HTTPError

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
                               'в случае большого видео, придется подождать подольше.')
        await message.delete()
    except:
        await message.reply('Этот бот умеет качать и отправлять вам видосы с ютуба. Пишите ему в директ!')


async def download_video(url: str, message: types.Message):
    yt = YouTube(url)
    output_filename = f'{message.from_user.id}_{uuid.uuid1()}.mp4'

    logging.info(f'Trying to save video from {url}')

    try:
        stream = yt.streams.filter(progressive=True, file_extension='mp4')
        stream.get_highest_resolution().download(filename=output_filename)
        logging.info(f'Video saved to file {output_filename}')
    except HTTPError as e:
        logging.info(f'An error has occured while downloading video: {e.info}')
        return

    with open(output_filename, 'rb') as video:
        try:
            await message.answer_video(video, caption=f'Ваше видео: {yt.title}')
            logging.info(f'Video {output_filename} sent to @{message.from_user.username} ({message.from_user.id})')
        except NetworkError:
            my_msg = await message.answer('Слишком большое видео! Могу отправить только до 50 Мб '
                                          '(ограничение Telegram API). Но я сейчас попробую обойти это ограничение '
                                          'хитрожопым способом, всё для вас! Ждите, пожалуйста... (Пока я пробую, не '
                                          'смогу реагировать на другие сообщения.)')
            logging.info(f'Video {output_filename} too large to send.')
            logging.info(f'Trying to send video using telegram-upload utility...')
            # telegram-upload --to @HazadusBot 'archive.txt' --caption '123456'
            # subprocess.run(['telegram-upload', '--to', '@HazadusBot', output_filename, '--caption',
            #                 f'{message.chat.id}'])
            os.spawnv(os.P_NOWAIT, 'telegram-upload', ['--to', '@HazadusBot', output_filename, '--caption',
                      message.chat.id])
            logging.info('telegram-upload executed in background.')
        #     await my_msg.delete()
        # finally:
        #     os.remove(output_filename)


async def message_youtube_link(message: types.Message):
    yt = YouTube(message.text)
    log_text = f'User @{message.from_user.username} ({message.from_user.full_name}) sent video "{yt.title}", ' \
               f'link: {message.text}'
    await message.answer(f'Начинаю качать *{yt.title.replace("*", "")}* с канала: "{yt.author}". '
                         f'Наберитесь терпения!',
                         parse_mode='Markdown')
    await bot.send_message(os.getenv('BOT_ADMIN'), log_text)
    logging.info(log_text)
    await download_video(message.text, message)
    await message.delete()


async def any_message(message: types.Message):
    logging.info(f'"@{message.from_user.username}" id={message.from_user.id} chat_id:{message.chat.id}: {message.text}')
    await message.answer('Лучше пришлите ссылку на видос с ютубчика!')


async def resend_video(message: types.Message):
    # Set video caption to chat_id where it must be sent!
    logging.info(f'Got msg from admin to resend: {message.video.file_id} to chat_id={message.caption}')
    # message.forward(message.caption)
    await bot.send_video(message.caption, message.video.file_id)


def filter_youtube_link(message: types.Message):
    return message.text.startswith('https://www.youtube.com/') or message.text.startswith('https://youtu.be/')


def filter_admin_msg(message: types.Message):
    return message.chat.type == 'private' and str(message.from_user.id) == os.getenv('BOT_ADMIN')


def register_client_handlers(disp: Dispatcher):
    disp.register_message_handler(command_start, commands=['start', 'help'])
    disp.register_message_handler(message_youtube_link, filter_youtube_link)
    disp.register_message_handler(resend_video, filter_admin_msg, content_types=['video'])
    # Any message to bot/chat. Must be last in order of handlers!
    disp.register_message_handler(any_message, lambda message: message.chat.type == 'private')

