import torch
from torchvision import transforms
from sklearn.preprocessing import LabelEncoder
import pickle
from bs4 import BeautifulSoup
from PIL import Image

import config

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode

import aiohttp

import os
from dotenv import load_dotenv

import text
import re
from urllib.parse import quote_plus, quote

load_dotenv()


class NNProcessor:
    _TRAIN_RESCALE_SIZE = 640
    # к этому размеру мы приводим картинки train'а
    # для дальнейшего рандомного обрезания под размер RESCALE_SIZE для аугментации данных
    _RESCALE_SIZE = 512

    def __init__(self, PATH_TO_MODEL, PATH_TO_ENCODER):
        self.nn_model = torch.load(PATH_TO_MODEL, map_location=torch.device("cpu"))

        with open(PATH_TO_ENCODER, "rb") as f:
            # dict1 = pickle.load(f)
            self.label_encoder = pickle.load(f)

        self.photo_transformations = transforms.Compose(
            [
                transforms.Resize(self._RESCALE_SIZE),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

    def predict(self, img: Image):
        jpg_image = img.convert("RGB")
        jpg_image = transforms.Compose(
            [transforms.ToTensor(), transforms.CenterCrop(max(jpg_image.size))]
        )(jpg_image)
        jpg_image = self.photo_transformations(jpg_image)
        jpg_image = jpg_image.unsqueeze(
            0
        )  # Добавление размерности пакета (batch dimension)

        # Передача изображения через модель для получения предсказания
        with torch.no_grad():
            output = self.nn_model(jpg_image)

        # Обработка предсказания
        top_predicted_classes = torch.topk(output.flatten(), 3).indices

        # Вывод результата предсказания
        return self.label_encoder.inverse_transform(top_predicted_classes)


class ResultComposer:
    def __init__(self):
        pass

    async def compose_result(self, mushrooms_list):
        mushrooms_list = list(
            map(lambda s: re.sub(r"[^a-zA-Z]", " ", s).title(), mushrooms_list)
        )

        items = [
            text.RESULT_BULLET_LI.format(
                *(
                    text.LINK_TEMPLATE.format(
                        config.SEARCH_ENGINE.format(quote(mushroom)), mushroom
                    ),
                    text.PLATFORM_SEARCH_TEMPLATE.format(
                        config.PLATFORM_SEARCH.format(quote(mushroom))
                    ),
                )
            )
            + await self._compose_article_answer(mushroom)
            for mushroom in mushrooms_list
        ]

        bullet_list = "\n\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])
        return text.RESULT_TEMPLATE + bullet_list

    async def _compose_article_answer(self, mushroom):
        article = await self._brief_on_platform(mushroom)

        answer = (
            text.FIRST_ARTICLE.format(article)
            if article is not None
            else text.NO_ARTICLES.format(
                config.SEARCH_ENGINE.format(quote_plus(mushroom))
            )
        )

        return answer

    async def _brief_on_platform(self, mushroom):
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(
                config.PLATFORM_SEARCH.format(quote_plus(mushroom))
            ) as resp:
                body = await resp.text()
                soup = BeautifulSoup(body, "html.parser")

                top_link = soup.select_one("span.taxon a").attrs["href"]

                return (
                    config.PLATFORM_WEBSCRAPPING + "/" + top_link
                    if top_link is not None
                    else None
                )


nn_processor = NNProcessor(config.PATH_TO_MODEL, config.PATH_TO_ENCODER)

result_composer = ResultComposer()

bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=ParseMode.HTML)
