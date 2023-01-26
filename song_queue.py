import asyncio
from collections import deque

import discord
import youtube_dl

class SongQueue:
    class Song:
        def __init__(self, title, url, filename, length):
            self.title = title
            self.url = url
            self.filename = filename
            self.length = length

    def __init__(self, ytdl_format_options, voice_client, loop):
        self.__ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
        self.__voice = voice_client
        self.__play_queue = deque()
        self.__dl_queue = deque()
        self.__play_task = None
        self.__dl_task = None
        self.__loop = loop
        self.playing = False
        self.downloading = False

    def __str__(self):
        dls = ["[{index}] {title}".format(index=i, title=song.title) for i, song in self.__dl_queue]
        playing = ["[{index}] {title}".format(index=i, title=song.title) for i, song in self.__play_queue]
        out = "**Downloading**" + "\n    ".join(dls) + "\n**Now Playing**" + "\n    ".join(playing)
        return out

    async def add(self, url, channel):
        # get song metadata
        data = await self.__loop.run_in_executor(None, lambda: self.__ytdl.extract_info(url, download=False))
        # get song filename
        filename = self.__ytdl.prepare_filename(data)
        # add to queue
        song = self.Song(data["title"], url, filename, 0)
        self.__dl_queue.put(song)
        await channel.send("{} added to queue".format(song.title))
        # start download coroutine
        if not self.downloading:
            self.__dl_task = asyncio.create_task(self.__dl_queue_coro)

    async def __dl_queue_coro(self):
        self.downloading = True
        while not self.__dl_queue.empty():
            # get song from download queue
            song = self.__dl_queue.get()
            # download file -- how to manage concurrent downloads? need to make this a coroutine
            # and manage it with a task group
            await self.__loop.run_in_executor(None, lambda: self.__ytdl.download(song.url))
            # move song to play queue
            self.__play_queue.put(song)
            # start play coroutine
            if not self.playing:
                self.__play_task = asyncio.create_task(self.__play_queue_coro)
        self.downloading = False
        self.__dl_task = None

    async def __play_queue_coro(self):
        self.playing = True
        while not self.__play_queue.empty():
            song = self.__play_queue.get()
            await self.__voice.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=song.filename))
        self.playing = False
        self.__play_task = None
