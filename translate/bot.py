# translate - A maubot plugin to translate words.
# Copyright (C) 2019 Tulir Asokan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import re
from typing import Optional, Tuple, Type, Dict

from mautrix.util.config import BaseProxyConfig
from mautrix.types import RoomID, EventType, MessageType
from maubot import Plugin, MessageEvent
from maubot.handlers import command, event

from .provider import AbstractTranslationProvider
from .util import Config, LanguageCodePair, TranslationProviderError, AutoTranslateConfig

try:
    import langdetect
except ImportError:
    langdetect = None
    LangDetectException = None
try:
    import langid
except ImportError:
    langid = None
class TranslatorBot(Plugin):
    translator: Optional[AbstractTranslationProvider]
    auto_translate: Dict[RoomID, AutoTranslateConfig]
    config: Config

    def lang_detect(self,string:str,config:AutoTranslateConfig):
        langs = config.accepted_languages | {config.main_language}
        self.log.debug(f"langs: {langs}")
        if config.detector == "langid" and langid is not None:
            langid.set_languages(langs)
            detected_lang = langid.classify(string)[0]
            self.log.debug(f"Detected language via langid: '{detected_lang}'")
            return detected_lang
        elif config.detector == "langdetect" and langdetect is not None:
            max_tries = 6
            tries = 0
            try_detecting = True
            while try_detecting:
                for res in langdetect.detect_langs(string):
                    self.log.debug(res)
                    if res.lang in langs:
                        self.log.debug(f"Detected language via langdetect: '{res.lang}'")
                        return res.lang
                if tries > max_tries:
                    try_detecting = False
                tries += 1
        else:
            self.log.warn(f"Unkown language detector. Expected 'langid' or 'langdetect' got '{config.detector}'")

    async def start(self) -> None:
        await super().start()
        self.on_external_config_update()

    def on_external_config_update(self) -> None:
        self.translator = None
        self.config.load_and_update()
        self.auto_translate = self.config.load_auto_translate()
        try:
            self.translator = self.config.load_translator()
        except TranslationProviderError:
            self.log.exception("")

    @classmethod
    def get_config_class(cls) -> Type['BaseProxyConfig']:
        return Config

    @event.on(EventType.ROOM_MESSAGE)
    async def event_handler(self, evt: MessageEvent) -> None:
        if (evt.content.msgtype == MessageType.NOTICE
                or evt.sender == self.client.mxid):
            return
        try:
            atc = self.auto_translate[evt.room_id]
        except KeyError:
            for key,config in self.auto_translate.items():
                if re.match(key, evt.room_id):
                    atc = config
            if not atc:
                return

        lang = self.lang_detect(evt.content.body,atc)
        if lang:
            langs = config.accepted_languages | {config.main_language}
            other_langs = {l for l in langs if l not in lang}
            for other_lang in other_langs:
                string_in_other_lang = await self.translator.translate(evt.content.body,from_lang=lang, to_lang=other_lang)
                prefix = "**" + other_lang + "**: "
                await evt.reply(f"{prefix if len(other_langs) > 1 else ''}{string_in_other_lang.text}")

    @command.new("translate", aliases=["tr"])
    @LanguageCodePair("language", required=False)
    @command.argument("text", pass_raw=True, required=False)
    async def command_handler(self, evt: MessageEvent, language: Optional[Tuple[str, str]],
                              text: str) -> None:
        if not language:
            await evt.reply("Usage: !translate [from] <to> [text or reply to message]")
            return
        if not self.config["response_reply"]:
            evt.disable_reply = True
        if not self.translator:
            self.log.warn("Translate command used, but translator not loaded")
            return
        if not text and evt.content.get_reply_to():
            reply_evt = await self.client.get_event(evt.room_id, evt.content.get_reply_to())
            text = reply_evt.content.body
        if not text:
            await evt.reply("Usage: !translate [from] <to> [text or reply to message]")
            return
        result = await self.translator.translate(text, to_lang=language[1], from_lang=language[0])
        await evt.reply(result.text)
